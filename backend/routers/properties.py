from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime

from database import get_database
from models.property import Property
from models.county import County
from models.tax_sale import TaxSale
from models.property_valuation import PropertyValuation
from models.property_enrichment import PropertyEnrichment
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class PropertyBase(BaseModel):
    property_address: str
    legal_description: str = None
    appraisal_district_id: str = None
    property_type: str = None
    assessed_value: float = None
    market_value: float = None
    lot_size: float = None
    square_feet: int = None
    year_built: int = None
    homestead_exemption: bool = False
    agricultural_exemption: bool = False
    mineral_rights: bool = False
    latitude: float = None
    longitude: float = None
    notes: str = None

class PropertyCreate(PropertyBase):
    county_id: int

class PropertyResponse(PropertyBase):
    id: int
    county_id: int
    redemption_period_months: int
    expected_penalty_rate: int
    created_at: date
    updated_at: date = None
    
    class Config:
        from_attributes = True

class PropertyWithCounty(PropertyResponse):
    county: dict = None
    recent_tax_sales: List[dict] = []

class PropertySearchFilters(BaseModel):
    county_id: Optional[int] = None
    property_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    homestead_only: Optional[bool] = None
    agricultural_only: Optional[bool] = None
    has_mineral_rights: Optional[bool] = None
    search_term: Optional[str] = None

@router.get("/", response_model=List[PropertyResponse])
def get_properties(
    skip: int = 0,
    limit: int = 100,
    county_id: Optional[int] = Query(None),
    property_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Property)
    
    # Apply filters
    if county_id:
        query = query.filter(Property.county_id == county_id)
    
    if property_type:
        query = query.filter(Property.property_type == property_type)
    
    if search:
        query = query.filter(
            or_(
                Property.property_address.contains(search),
                Property.legal_description.contains(search),
                Property.appraisal_district_id.contains(search)
            )
        )
    
    properties = query.offset(skip).limit(limit).all()
    return properties

@router.get("/{property_id}", response_model=PropertyWithCounty)
def get_property(
    property_id: int,
    db: Session = Depends(get_database),
    # Temporarily disabled for testing - TODO: re-enable authentication
    # current_user: User = Depends(get_current_user)
):
    """Get basic property information"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get county information
    county = db.query(County).filter(County.id == property_obj.county_id).first()
    
    # Get recent tax sales
    recent_sales = db.query(TaxSale).filter(
        TaxSale.property_id == property_id
    ).order_by(TaxSale.sale_date.desc()).limit(5).all()
    
    response_data = PropertyResponse.from_orm(property_obj).dict()
    response_data['county'] = {
        'id': county.id,
        'name': county.name,
        'state': county.state,
        'auction_type': county.auction_type
    } if county else None
    
    response_data['recent_tax_sales'] = [
        {
            'id': sale.id,
            'sale_date': sale.sale_date,
            'minimum_bid': float(sale.minimum_bid),
            'winning_bid': float(sale.winning_bid) if sale.winning_bid else None,
            'sale_status': sale.sale_status
        } for sale in recent_sales
    ]
    
    return response_data

@router.post("/", response_model=PropertyResponse)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Verify county exists
    county = db.query(County).filter(County.id == property_data.county_id).first()
    if not county:
        raise HTTPException(status_code=400, detail="County not found")
    
    # Create property
    db_property = Property(**property_data.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    return db_property

@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Update property fields
    for field, value in property_data.dict(exclude_unset=True).items():
        setattr(property_obj, field, value)
    
    db.commit()
    db.refresh(property_obj)
    
    return property_obj

@router.delete("/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    db.delete(property_obj)
    db.commit()
    
    return {"message": "Property deleted successfully"}

@router.post("/search", response_model=List[PropertyResponse])
def search_properties(
    filters: PropertySearchFilters,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Property)
    
    # Apply filters
    if filters.county_id:
        query = query.filter(Property.county_id == filters.county_id)
    
    if filters.property_type:
        query = query.filter(Property.property_type == filters.property_type)
    
    if filters.min_value:
        query = query.filter(Property.assessed_value >= filters.min_value)
    
    if filters.max_value:
        query = query.filter(Property.assessed_value <= filters.max_value)
    
    if filters.homestead_only:
        query = query.filter(Property.homestead_exemption == True)
    
    if filters.agricultural_only:
        query = query.filter(Property.agricultural_exemption == True)
    
    if filters.has_mineral_rights:
        query = query.filter(Property.mineral_rights == True)
    
    if filters.search_term:
        query = query.filter(
            or_(
                Property.property_address.contains(filters.search_term),
                Property.legal_description.contains(filters.search_term),
                Property.appraisal_district_id.contains(filters.search_term)
            )
        )
    
    properties = query.offset(skip).limit(limit).all()
    return properties

@router.get("/{property_id}/investment-analysis")
def get_investment_analysis(
    property_id: int,
    estimated_bid: float = Query(..., description="Estimated winning bid amount"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Calculate potential returns
    redemption_months = property_obj.redemption_period_months
    penalty_rate = property_obj.expected_penalty_rate
    
    # Calculate potential return amounts
    penalty_amount = estimated_bid * (penalty_rate / 100)
    total_return = estimated_bid + penalty_amount
    
    # Calculate annualized return
    annualized_return = (penalty_rate / redemption_months) * 12
    
    # Get recent market data if available
    recent_valuation = db.query(PropertyValuation).filter(
        PropertyValuation.property_id == property_id
    ).order_by(PropertyValuation.valuation_date.desc()).first()
    
    analysis = {
        "property_id": property_id,
        "estimated_bid": estimated_bid,
        "redemption_period_months": redemption_months,
        "penalty_rate_percent": penalty_rate,
        "potential_penalty_amount": penalty_amount,
        "total_potential_return": total_return,
        "annualized_return_percent": round(annualized_return, 2),
        "property_type": property_obj.property_type,
        "assessed_value": float(property_obj.assessed_value) if property_obj.assessed_value else None,
        "market_value": float(property_obj.market_value) if property_obj.market_value else None,
        "recent_valuation": {
            "value": float(recent_valuation.estimated_value),
            "date": recent_valuation.valuation_date,
            "source": recent_valuation.valuation_source
        } if recent_valuation else None,
        "risk_factors": {
            "homestead_exemption": property_obj.homestead_exemption,
            "agricultural_exemption": property_obj.agricultural_exemption,
            "mineral_rights": property_obj.mineral_rights,
            "longer_redemption": redemption_months == 24
        }
    }
    
    return analysis

@router.get("/{property_id}/enriched")
def get_property_enriched(
    property_id: int,
    db: Session = Depends(get_database),
    # Temporarily disabled for testing - TODO: re-enable authentication
    # current_user: User = Depends(get_current_user)
):
    """Get property with all enrichment data"""
    property_obj = db.query(Property).options(
        joinedload(Property.county),
        joinedload(Property.enrichment),
        joinedload(Property.tax_sales)
    ).filter(Property.id == property_id).first()
    
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get next tax sale
    next_sale = None
    for sale in property_obj.tax_sales:
        if sale.sale_date >= datetime.now().date() and sale.sale_status == 'scheduled':
            if not next_sale or sale.sale_date < next_sale.sale_date:
                next_sale = sale
    
    # Format response
    response = {
        "id": property_obj.id,
        "parcel_number": property_obj.parcel_number,
        "owner_name": property_obj.owner_name,
        "property_address": property_obj.property_address,
        "city": property_obj.city,
        "state": property_obj.state,
        "zip_code": property_obj.zip_code,
        "property_type": property_obj.property_type,
        "assessed_value": float(property_obj.assessed_value) if property_obj.assessed_value else None,
        "market_value": float(property_obj.market_value) if property_obj.market_value else None,
        "lot_size": float(property_obj.lot_size) if property_obj.lot_size else None,
        "square_footage": property_obj.square_footage,
        "bedrooms": property_obj.bedrooms,
        "bathrooms": float(property_obj.bathrooms) if property_obj.bathrooms else None,
        "year_built": property_obj.year_built,
        "latitude": float(property_obj.latitude) if property_obj.latitude else None,
        "longitude": float(property_obj.longitude) if property_obj.longitude else None,
        "redemption_period_months": property_obj.redemption_period_months,
        "expected_penalty_rate": property_obj.expected_penalty_rate,
        
        "county": {
            "id": property_obj.county.id,
            "name": property_obj.county.county_name,
            "state": property_obj.county.county_state
        } if property_obj.county else None,
        
        "next_tax_sale": {
            "id": next_sale.id,
            "sale_date": next_sale.sale_date.isoformat(),
            "minimum_bid": float(next_sale.minimum_bid),
            "taxes_owed": float(next_sale.taxes_owed),
            "total_judgment": float(next_sale.total_judgment),
            "case_number": next_sale.case_number
        } if next_sale else None,
        
        "enrichment": None
    }
    
    # Add enrichment data if available
    if property_obj.enrichment:
        enr = property_obj.enrichment
        response["enrichment"] = {
            "investment_score": float(enr.investment_score) if enr.investment_score else None,
            "roi_percentage": float(enr.roi_percentage) if enr.roi_percentage else None,
            "cap_rate": float(enr.cap_rate) if enr.cap_rate else None,
            "cash_on_cash_return": float(enr.cash_on_cash_return) if enr.cash_on_cash_return else None,
            "monthly_rent_estimate": float(enr.monthly_rent_estimate) if enr.monthly_rent_estimate else None,
            "gross_rent_multiplier": float(enr.gross_rent_multiplier) if enr.gross_rent_multiplier else None,
            "zestimate": float(enr.zestimate) if enr.zestimate else None,
            "zillow_url": enr.zillow_url,
            "estimated_rehab_cost": float(enr.estimated_rehab_cost) if enr.estimated_rehab_cost else None,
            "estimated_arv": float(enr.estimated_arv) if enr.estimated_arv else None,
            "neighborhood_data": enr.neighborhood_data,
            "zillow_price_history": enr.zillow_price_history,
            "zillow_tax_history": enr.zillow_tax_history,
            "nearby_schools": enr.neighborhood_data.get("schools", []) if enr.neighborhood_data else [],
            "data_quality_score": float(enr.data_quality_score) if enr.data_quality_score else None,
            "last_enriched_at": enr.last_enriched_at.isoformat() if enr.last_enriched_at else None
        }
    
    return response