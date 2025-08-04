# Google OAuth Setup Guide

This guide explains how to set up Google OAuth for the Tax Lien Search application.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API for your project

### 2. Create OAuth 2.0 Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Configure the OAuth consent screen if prompted:
   - Choose "External" user type
   - Fill in the required fields
   - Add scopes: `email`, `profile`, `openid`

### 3. Configure OAuth Client

1. Application type: "Web application"
2. Name: "Tax Lien Search"
3. Authorized JavaScript origins:
   ```
   http://localhost:3000
   https://tax.profithits.app
   ```
4. Authorized redirect URIs:
   ```
   http://localhost:8000/api/auth/google/callback
   https://tax.profithits.app/api/auth/google/callback
   ```

### 4. Save Credentials

1. Copy the Client ID and Client Secret
2. Add them to your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

## Production Setup

For production, ensure:

1. Update `APP_ENV=production` in `.env`
2. Add your production domain to authorized origins
3. Add production callback URL to redirect URIs
4. Ensure SSL is properly configured

## Admin Setup

The user with email `meredith@monkeyattack.com` is automatically granted admin privileges upon first login.

## Troubleshooting

### Common Issues

1. **Redirect URI mismatch**: Ensure the callback URL matches exactly what's configured in Google Console
2. **401 Unauthorized**: Check that the client ID and secret are correct
3. **CORS errors**: Verify CORS_ORIGINS in `.env` includes your frontend URL

### Testing

To test the OAuth flow:

1. Navigate to the login page
2. Click "Sign in with Google"
3. Authorize the application
4. You should be redirected back and logged in

## Security Notes

- Never commit the `.env` file with actual credentials
- Use environment variables in production
- Rotate client secrets periodically
- Monitor OAuth usage in Google Console