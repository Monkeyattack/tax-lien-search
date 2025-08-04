from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import HTTPException, Request
from decouple import config
from sqlalchemy.orm import Session
from models.user import User
import secrets

# OAuth setup
oauth = OAuth()

# Google OAuth configuration
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID', default=''),
    client_secret=config('GOOGLE_CLIENT_SECRET', default=''),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

class GoogleAuthService:
    """Service for handling Google OAuth authentication"""
    
    @staticmethod
    async def get_or_create_user(user_info: dict, db: Session) -> User:
        """Get existing user or create new one from Google OAuth data"""
        email = user_info.get('email')
        google_id = user_info.get('sub')  # Google's unique user ID
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        if user:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = 'google'
            
            # Update profile picture if provided
            if user_info.get('picture'):
                user.profile_picture = user_info['picture']
                
            # Set admin status for specific email
            if email == 'meredith@monkeyattack.com':
                user.is_admin = True
                
            db.commit()
            return user
        
        # Create new user
        username = email.split('@')[0]
        # Ensure unique username
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=email,
            google_id=google_id,
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            auth_provider='google',
            profile_picture=user_info.get('picture', ''),
            is_active=True,
            is_admin=(email == 'meredith@monkeyattack.com')  # Set admin for your email
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def generate_state_token() -> str:
        """Generate a secure random state token for OAuth"""
        return secrets.token_urlsafe(32)