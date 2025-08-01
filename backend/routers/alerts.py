from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta

from database import get_database
from models.alert import Alert
from models.investment import Investment
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class AlertBase(BaseModel):
    alert_type: str
    alert_date: date
    message: str

class AlertCreate(AlertBase):
    investment_id: int = None

class AlertResponse(AlertBase):
    id: int
    user_id: int
    investment_id: int = None
    is_sent: bool
    sent_at: datetime = None
    is_read: bool
    is_overdue: bool
    days_until_alert: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertWithInvestment(AlertResponse):
    investment: dict = None

@router.get("/", response_model=List[AlertResponse])
def get_user_alerts(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    alert_type: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    alerts = query.order_by(desc(Alert.alert_date)).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertWithInvestment)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(
        and_(Alert.id == alert_id, Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    response_data = AlertResponse.from_orm(alert).dict()
    
    # Get investment details if applicable
    if alert.investment_id:
        investment = db.query(Investment).filter(Investment.id == alert.investment_id).first()
        if investment:
            response_data['investment'] = {
                'id': investment.id,
                'property_id': investment.property_id,
                'purchase_amount': float(investment.purchase_amount),
                'redemption_deadline': investment.redemption_deadline,
                'investment_status': investment.investment_status
            }
    
    return response_data

@router.post("/", response_model=AlertResponse)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Verify investment exists if provided
    if alert_data.investment_id:
        investment = db.query(Investment).filter(
            and_(Investment.id == alert_data.investment_id, Investment.user_id == current_user.id)
        ).first()
        if not investment:
            raise HTTPException(status_code=400, detail="Investment not found")
    
    db_alert = Alert(
        user_id=current_user.id,
        investment_id=alert_data.investment_id,
        alert_type=alert_data.alert_type,
        alert_date=alert_data.alert_date,
        message=alert_data.message
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.put("/{alert_id}/mark-read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(
        and_(Alert.id == alert_id, Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    
    return {"message": "Alert marked as read"}

@router.put("/mark-all-read")
def mark_all_alerts_read(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    db.query(Alert).filter(
        and_(Alert.user_id == current_user.id, Alert.is_read == False)
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All alerts marked as read"}

@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(
        and_(Alert.id == alert_id, Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}

@router.post("/generate-investment-alerts")
def generate_investment_alerts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Generate alerts for active investments"""
    
    # Get all active investments for the user
    active_investments = db.query(Investment).filter(
        and_(Investment.user_id == current_user.id, Investment.investment_status == 'active')
    ).all()
    
    alerts_created = 0
    
    for investment in active_investments:
        # Check if redemption deadline alerts already exist
        existing_alerts = db.query(Alert).filter(
            and_(
                Alert.investment_id == investment.id,
                Alert.alert_type == 'redemption_deadline'
            )
        ).count()
        
        if existing_alerts == 0:  # No alerts exist for this investment
            # Create alerts at different intervals before redemption deadline
            alert_intervals = [
                (30, "Redemption deadline in 30 days"),
                (14, "Redemption deadline in 2 weeks"),
                (7, "Redemption deadline in 1 week"),
                (1, "Redemption deadline tomorrow")
            ]
            
            for days_before, message in alert_intervals:
                alert_date = investment.redemption_deadline - timedelta(days=days_before)
                
                # Only create alerts for future dates
                if alert_date >= datetime.now().date():
                    db_alert = Alert(
                        user_id=current_user.id,
                        investment_id=investment.id,
                        alert_type='redemption_deadline',
                        alert_date=alert_date,
                        message=f"{message} for property at {investment.property.property_address if investment.property else 'Unknown Address'}"
                    )
                    
                    db.add(db_alert)
                    alerts_created += 1
    
    db.commit()
    
    return {
        "message": f"Generated {alerts_created} alerts for {len(active_investments)} active investments"
    }

@router.get("/upcoming/summary")
def get_upcoming_alerts_summary(
    days_ahead: int = 30,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get summary of upcoming alerts"""
    
    end_date = datetime.now().date() + timedelta(days=days_ahead)
    
    upcoming_alerts = db.query(Alert).filter(
        and_(
            Alert.user_id == current_user.id,
            Alert.alert_date >= datetime.now().date(),
            Alert.alert_date <= end_date,
            Alert.is_read == False
        )
    ).all()
    
    # Group by alert type
    alert_summary = {}
    for alert in upcoming_alerts:
        if alert.alert_type not in alert_summary:
            alert_summary[alert.alert_type] = {
                'count': 0,
                'urgent_count': 0,  # Within 7 days
                'alerts': []
            }
        
        alert_summary[alert.alert_type]['count'] += 1
        
        if alert.days_until_alert <= 7:
            alert_summary[alert.alert_type]['urgent_count'] += 1
        
        alert_summary[alert.alert_type]['alerts'].append({
            'id': alert.id,
            'alert_date': alert.alert_date,
            'message': alert.message,
            'days_until_alert': alert.days_until_alert,
            'is_urgent': alert.days_until_alert <= 7
        })
    
    return {
        "total_upcoming_alerts": len(upcoming_alerts),
        "urgent_alerts": len([a for a in upcoming_alerts if a.days_until_alert <= 7]),
        "alert_types": alert_summary,
        "date_range": {
            "start_date": datetime.now().date(),
            "end_date": end_date
        }
    }