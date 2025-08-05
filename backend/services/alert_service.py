from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import logging

from models.saved_search import SavedSearch, SearchResult
from models.property import Property
from models.user import User
from models.alert import Alert
from routers.saved_searches import run_search_for_saved_search

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_saved_search_alerts(self):
        """Check all saved searches and send alerts for new matches"""
        logger.info("Starting saved search alert check")
        
        # Get active saved searches that need alerts
        searches = self._get_searches_needing_alerts()
        
        for search in searches:
            try:
                self._process_search_alerts(search)
            except Exception as e:
                logger.error(f"Error processing alerts for search {search.id}: {str(e)}")
    
    def _get_searches_needing_alerts(self) -> List[SavedSearch]:
        """Get saved searches that need to be checked for alerts"""
        now = datetime.utcnow()
        
        # Get all active searches with email alerts enabled
        query = self.db.query(SavedSearch).filter(
            SavedSearch.is_active == True,
            SavedSearch.email_alerts == True
        )
        
        searches_to_check = []
        
        for search in query.all():
            # Determine if search needs checking based on frequency
            should_check = False
            
            if search.alert_frequency == 'instant':
                # Check every time (for instant alerts)
                should_check = True
            elif search.alert_frequency == 'daily':
                # Check if it's been at least 24 hours
                if not search.last_alert_sent or (now - search.last_alert_sent) >= timedelta(days=1):
                    should_check = True
            elif search.alert_frequency == 'weekly':
                # Check if it's been at least 7 days
                if not search.last_alert_sent or (now - search.last_alert_sent) >= timedelta(days=7):
                    should_check = True
            
            if should_check:
                searches_to_check.append(search)
        
        logger.info(f"Found {len(searches_to_check)} searches needing alert checks")
        return searches_to_check
    
    def _process_search_alerts(self, search: SavedSearch):
        """Process alerts for a single saved search"""
        # Run the search to find new matches
        new_matches = run_search_for_saved_search(self.db, search)
        
        if new_matches == 0:
            logger.info(f"No new matches for search {search.id}")
            return
        
        # Get unsent results
        unsent_results = self.db.query(SearchResult).join(
            Property
        ).options(
            joinedload(SearchResult.property).joinedload(Property.enrichment)
        ).filter(
            SearchResult.saved_search_id == search.id,
            SearchResult.alert_sent == False
        ).order_by(SearchResult.matched_at.desc()).all()
        
        if not unsent_results:
            return
        
        # Create alert message
        alert_message = self._create_alert_message(search, unsent_results)
        
        # Create alert record
        alert = Alert(
            user_id=search.user_id,
            alert_type='saved_search_match',
            alert_date=datetime.utcnow().date(),
            message=alert_message,
            is_sent=False
        )
        self.db.add(alert)
        
        # Mark results as alert sent
        for result in unsent_results:
            result.alert_sent = True
            result.alert_sent_at = datetime.utcnow()
        
        # Update search last alert time
        search.last_alert_sent = datetime.utcnow()
        
        self.db.commit()
        
        # Send email notification (would integrate with email service)
        self._send_email_alert(search.user, search, unsent_results)
        
        # Mark alert as sent
        alert.is_sent = True
        alert.sent_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Sent alert for search {search.id} with {len(unsent_results)} new matches")
    
    def _create_alert_message(self, search: SavedSearch, results: List[SearchResult]) -> str:
        """Create alert message content"""
        property_count = len(results)
        
        message = f"Your saved search '{search.name}' found {property_count} new "
        message += "property" if property_count == 1 else "properties"
        message += " matching your criteria.\n\n"
        
        # Add top properties
        for i, result in enumerate(results[:5]):  # Show top 5
            prop = result.property
            message += f"{i+1}. {prop.property_address}, {prop.city} - "
            message += f"${prop.assessed_value:,.0f}" if prop.assessed_value else "Price N/A"
            
            if prop.enrichment and prop.enrichment.investment_score:
                message += f" (Score: {prop.enrichment.investment_score:.0f})"
            
            message += "\n"
        
        if property_count > 5:
            message += f"\n... and {property_count - 5} more properties"
        
        return message
    
    def _send_email_alert(self, user: User, search: SavedSearch, results: List[SearchResult]):
        """Send email notification for new matches"""
        # This would integrate with an email service like SendGrid, AWS SES, etc.
        # For now, just log it
        logger.info(f"Would send email to {user.email} for search '{search.name}' with {len(results)} matches")
        
        # Example email structure:
        # subject = f"New Tax Lien Properties Match Your Search: {search.name}"
        # html_content = self._generate_email_html(user, search, results)
        # send_email(to=user.email, subject=subject, html=html_content)
    
    def get_user_alerts(self, user_id: int, unread_only: bool = False) -> List[Alert]:
        """Get alerts for a specific user"""
        query = self.db.query(Alert).filter(Alert.user_id == user_id)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        return query.order_by(Alert.alert_date.desc()).all()
    
    def mark_alert_read(self, alert_id: int, user_id: int) -> bool:
        """Mark an alert as read"""
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()
        
        if alert:
            alert.is_read = True
            self.db.commit()
            return True
        
        return False
    
    def get_alert_summary(self, user_id: int) -> Dict[str, Any]:
        """Get alert summary for a user"""
        # Count unread alerts
        unread_count = self.db.query(func.count(Alert.id)).filter(
            Alert.user_id == user_id,
            Alert.is_read == False
        ).scalar()
        
        # Count saved searches with new matches
        searches_with_new = self.db.query(func.count(func.distinct(SearchResult.saved_search_id))).join(
            SavedSearch
        ).filter(
            SavedSearch.user_id == user_id,
            SearchResult.alert_sent == False
        ).scalar()
        
        # Get recent alerts
        recent_alerts = self.db.query(Alert).filter(
            Alert.user_id == user_id
        ).order_by(Alert.alert_date.desc()).limit(5).all()
        
        return {
            'unread_count': unread_count,
            'searches_with_new_matches': searches_with_new,
            'recent_alerts': [
                {
                    'id': alert.id,
                    'type': alert.alert_type,
                    'date': alert.alert_date,
                    'message': alert.message[:100] + '...' if len(alert.message) > 100 else alert.message,
                    'is_read': alert.is_read
                }
                for alert in recent_alerts
            ]
        }