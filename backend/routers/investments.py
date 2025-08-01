from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta

from database import get_database
from models.investment import Investment
from models.property import Property
from models.tax_sale import TaxSale
from models.redemption import Redemption
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class InvestmentBase(BaseModel):
    purchase_date: date
    purchase_amount: float
    deed_recording_fee: float = 0
    other_costs: float = 0
    deed_type: str = None
    deed_recorded_date: date = None
    deed_volume: str = None
    deed_page: str = None
    redemption_period_months: int
    expected_return_pct: float = None

class InvestmentCreate(InvestmentBase):
    tax_sale_id: int
    property_id: int

class InvestmentUpdate(BaseModel):
    deed_recorded_date: date = None
    deed_volume: str = None
    deed_page: str = None
    investment_status: str = None
    other_costs: float = None

class InvestmentResponse(InvestmentBase):
    id: int
    user_id: int
    tax_sale_id: int
    property_id: int
    total_investment: float
    redemption_deadline: date
    investment_status: str
    days_until_redemption: int = None
    is_redemption_expired: bool
    potential_return_amount: float
    total_potential_return: float
    annualized_return_rate: float = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvestmentWithDetails(InvestmentResponse):
    property: dict = None
    tax_sale: dict = None
    redemption: dict = None

class RedemptionCreate(BaseModel):
    redemption_date: date
    redemption_amount: float
    penalty_amount: float
    penalty_percentage: float
    redeemer_info: str = None
    payment_method: str = None
    county_processing_fee: float = 0

@router.get("/", response_model=List[InvestmentResponse])
def get_user_investments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Investment).filter(Investment.user_id == current_user.id)
    
    if status:
        query = query.filter(Investment.investment_status == status)
    
    investments = query.order_by(desc(Investment.created_at)).offset(skip).limit(limit).all()
    return investments

@router.get("/{investment_id}", response_model=InvestmentWithDetails)
def get_investment(
    investment_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        and_(Investment.id == investment_id, Investment.user_id == current_user.id)
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    # Get related data
    property_obj = db.query(Property).filter(Property.id == investment.property_id).first()
    tax_sale = db.query(TaxSale).filter(TaxSale.id == investment.tax_sale_id).first()
    redemption = db.query(Redemption).filter(Redemption.investment_id == investment.id).first()
    
    response_data = InvestmentResponse.from_orm(investment).dict()
    
    response_data['property'] = {
        'id': property_obj.id,
        'address': property_obj.property_address,
        'property_type': property_obj.property_type,
        'assessed_value': float(property_obj.assessed_value) if property_obj.assessed_value else None,
        'homestead_exemption': property_obj.homestead_exemption,
        'agricultural_exemption': property_obj.agricultural_exemption
    } if property_obj else None
    
    response_data['tax_sale'] = {
        'id': tax_sale.id,
        'sale_date': tax_sale.sale_date,
        'minimum_bid': float(tax_sale.minimum_bid),
        'total_judgment': float(tax_sale.total_judgment),
        'case_number': tax_sale.case_number
    } if tax_sale else None
    
    response_data['redemption'] = {
        'id': redemption.id,
        'redemption_date': redemption.redemption_date,
        'redemption_amount': float(redemption.redemption_amount),
        'penalty_amount': float(redemption.penalty_amount),
        'penalty_percentage': float(redemption.penalty_percentage),
        'net_profit': float(redemption.net_profit),
        'annualized_return': float(redemption.annualized_return)
    } if redemption else None
    
    return response_data

@router.post("/", response_model=InvestmentResponse)
def create_investment(
    investment_data: InvestmentCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Verify tax sale exists
    tax_sale = db.query(TaxSale).filter(TaxSale.id == investment_data.tax_sale_id).first()
    if not tax_sale:
        raise HTTPException(status_code=400, detail="Tax sale not found")
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == investment_data.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=400, detail="Property not found")
    
    # Calculate total investment
    total_investment = (
        investment_data.purchase_amount + 
        investment_data.deed_recording_fee + 
        investment_data.other_costs
    )
    
    # Calculate redemption deadline
    redemption_deadline = investment_data.purchase_date + timedelta(
        days=investment_data.redemption_period_months * 30
    )
    
    # Set expected return percentage based on property type
    if not investment_data.expected_return_pct:
        if property_obj.homestead_exemption or property_obj.agricultural_exemption:
            expected_return_pct = 25  # Could be 50% in second year
        else:
            expected_return_pct = 25
    else:
        expected_return_pct = investment_data.expected_return_pct
    
    # Create investment
    db_investment = Investment(
        user_id=current_user.id,
        tax_sale_id=investment_data.tax_sale_id,
        property_id=investment_data.property_id,
        purchase_date=investment_data.purchase_date,
        purchase_amount=investment_data.purchase_amount,
        deed_recording_fee=investment_data.deed_recording_fee,
        other_costs=investment_data.other_costs,
        total_investment=total_investment,
        deed_type=investment_data.deed_type,
        deed_recorded_date=investment_data.deed_recorded_date,
        deed_volume=investment_data.deed_volume,
        deed_page=investment_data.deed_page,
        redemption_period_months=investment_data.redemption_period_months,
        redemption_deadline=redemption_deadline,
        expected_return_pct=expected_return_pct
    )
    
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    
    # Update tax sale status
    tax_sale.sale_status = 'sold'
    tax_sale.winning_bid = investment_data.purchase_amount
    tax_sale.winner_info = current_user.username
    db.commit()
    
    return db_investment

@router.put("/{investment_id}", response_model=InvestmentResponse)
def update_investment(
    investment_id: int,
    investment_data: InvestmentUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        and_(Investment.id == investment_id, Investment.user_id == current_user.id)
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    # Update fields
    for field, value in investment_data.dict(exclude_unset=True).items():
        if field == 'other_costs':
            # Recalculate total investment
            investment.other_costs = value
            investment.total_investment = (
                investment.purchase_amount + 
                investment.deed_recording_fee + 
                investment.other_costs
            )
        else:
            setattr(investment, field, value)
    
    db.commit()
    db.refresh(investment)
    
    return investment

@router.post("/{investment_id}/redeem")
def redeem_investment(
    investment_id: int,
    redemption_data: RedemptionCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        and_(Investment.id == investment_id, Investment.user_id == current_user.id)
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    if investment.investment_status != 'active':
        raise HTTPException(status_code=400, detail="Investment is not active")
    
    # Calculate metrics
    days_held = (redemption_data.redemption_date - investment.purchase_date).days
    net_profit = (
        redemption_data.redemption_amount - 
        float(investment.total_investment) - 
        redemption_data.county_processing_fee
    )
    
    # Calculate annualized return
    if days_held > 0:
        daily_return = redemption_data.penalty_percentage / 100 / days_held
        annualized_return = daily_return * 365
    else:
        annualized_return = 0
    
    # Create redemption record
    db_redemption = Redemption(
        investment_id=investment.id,
        redemption_date=redemption_data.redemption_date,
        redemption_amount=redemption_data.redemption_amount,
        penalty_amount=redemption_data.penalty_amount,
        penalty_percentage=redemption_data.penalty_percentage,
        days_held=days_held,
        annualized_return=annualized_return,
        redeemer_info=redemption_data.redeemer_info,
        payment_method=redemption_data.payment_method,
        county_processing_fee=redemption_data.county_processing_fee,
        net_profit=net_profit
    )
    
    db.add(db_redemption)
    
    # Update investment status
    investment.investment_status = 'redeemed'
    
    db.commit()
    db.refresh(db_redemption)
    
    return {
        "message": "Investment redeemed successfully",
        "redemption_id": db_redemption.id,
        "net_profit": net_profit,
        "annualized_return": annualized_return * 100,
        "days_held": days_held
    }

@router.get("/dashboard/summary")
def get_investment_summary(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Get all user investments
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).all()
    
    # Calculate summary statistics
    total_invested = sum(float(inv.total_investment) for inv in investments)
    active_investments = [inv for inv in investments if inv.investment_status == 'active']
    redeemed_investments = [inv for inv in investments if inv.investment_status == 'redeemed']
    
    # Get redemption data
    redemptions = db.query(Redemption).join(Investment).filter(
        Investment.user_id == current_user.id
    ).all()
    
    total_redeemed_value = sum(float(red.redemption_amount) for red in redemptions)
    total_profit = sum(float(red.net_profit) for red in redemptions)
    
    # Calculate pending returns
    pending_return_amount = sum(inv.potential_return_amount for inv in active_investments)
    
    # Expiring soon (within 30 days)
    expiring_soon = [
        inv for inv in active_investments 
        if inv.days_until_redemption is not None and inv.days_until_redemption <= 30
    ]
    
    summary = {
        "total_investments": len(investments),
        "active_investments": len(active_investments),
        "redeemed_investments": len(redeemed_investments),
        "total_invested": total_invested,
        "total_redeemed_value": total_redeemed_value,
        "total_profit": total_profit,
        "pending_return_amount": pending_return_amount,
        "expiring_soon_count": len(expiring_soon),
        "overall_roi_percent": (total_profit / total_invested * 100) if total_invested > 0 else 0,
        "average_annualized_return": sum(
            float(red.annualized_return) for red in redemptions
        ) / len(redemptions) * 100 if redemptions else 0
    }
    
    return summary

@router.get("/{investment_id}/calculate-redemption")
def calculate_redemption_amount(
    investment_id: int,
    redemption_date: date = Query(default=None),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    investment = db.query(Investment).filter(
        and_(Investment.id == investment_id, Investment.user_id == current_user.id)
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    if not redemption_date:
        redemption_date = datetime.now().date()
    
    calculation = investment.calculate_redemption_amount(redemption_date)
    
    return {
        "investment_id": investment_id,
        "redemption_date": redemption_date,
        "purchase_amount": float(investment.purchase_amount),
        "total_investment": float(investment.total_investment),
        **calculation
    }