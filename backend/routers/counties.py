from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date

from database import get_database
from models.county import County
from models.tax_sale import TaxSale
from models.property import Property
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class CountyBase(BaseModel):
    name: str
    state: str = 'TX'
    auction_schedule: str = None
    auction_location: str = None
    auction_type: str = None
    website_url: str = None
    contact_info: str = None
    special_procedures: str = None

class CountyCreate(CountyBase):
    pass

class CountyResponse(CountyBase):
    id: int
    created_at: date
    
    class Config:
        from_attributes = True

class CountyWithStats(CountyResponse):
    total_properties: int = 0
    upcoming_sales: int = 0
    recent_sales: int = 0
    average_minimum_bid: float = 0

class TaxSaleBase(BaseModel):
    property_id: int
    sale_date: date
    minimum_bid: float
    taxes_owed: float
    interest_penalties: float = 0
    court_costs: float = 0
    attorney_fees: float = 0
    constable_precinct: str = None
    case_number: str = None

class TaxSaleCreate(TaxSaleBase):
    county_id: int

class TaxSaleResponse(TaxSaleBase):
    id: int
    county_id: int
    total_judgment: float
    sale_status: str
    winning_bid: float = None
    winner_info: str = None
    is_upcoming: bool
    excess_proceeds: float
    created_at: date
    
    class Config:
        from_attributes = True

class TaxSaleWithProperty(TaxSaleResponse):
    property: dict = None

@router.get("/", response_model=List[CountyResponse])
def get_counties(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    counties = db.query(County).all()
    return counties

@router.get("/{county_id}", response_model=CountyWithStats)
def get_county(
    county_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    
    # Get statistics
    total_properties = db.query(Property).filter(Property.county_id == county_id).count()
    
    upcoming_sales = db.query(TaxSale).filter(
        TaxSale.county_id == county_id,
        TaxSale.sale_status == 'scheduled',
        TaxSale.sale_date >= date.today()
    ).count()
    
    recent_sales = db.query(TaxSale).filter(
        TaxSale.county_id == county_id,
        TaxSale.sale_status == 'sold'
    ).count()
    
    # Calculate average minimum bid
    avg_bid_result = db.query(TaxSale.minimum_bid).filter(
        TaxSale.county_id == county_id
    ).all()
    
    avg_minimum_bid = 0
    if avg_bid_result:
        total_bids = sum(float(bid[0]) for bid in avg_bid_result)
        avg_minimum_bid = total_bids / len(avg_bid_result)
    
    response_data = CountyResponse.from_orm(county).dict()
    response_data.update({
        'total_properties': total_properties,
        'upcoming_sales': upcoming_sales,
        'recent_sales': recent_sales,
        'average_minimum_bid': round(avg_minimum_bid, 2)
    })
    
    return response_data

@router.get("/{county_id}/upcoming-sales", response_model=List[TaxSaleWithProperty])
def get_county_upcoming_sales(
    county_id: int,
    limit: int = 50,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Verify county exists
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    
    # Get upcoming sales
    upcoming_sales = db.query(TaxSale).filter(
        TaxSale.county_id == county_id,
        TaxSale.sale_status == 'scheduled',
        TaxSale.sale_date >= date.today()
    ).order_by(TaxSale.sale_date).limit(limit).all()
    
    # Add property information
    response_data = []
    for sale in upcoming_sales:
        sale_data = TaxSaleResponse.from_orm(sale).dict()
        
        # Get property details
        property_obj = db.query(Property).filter(Property.id == sale.property_id).first()
        if property_obj:
            sale_data['property'] = {
                'id': property_obj.id,
                'address': property_obj.property_address,
                'property_type': property_obj.property_type,
                'assessed_value': float(property_obj.assessed_value) if property_obj.assessed_value else None,
                'homestead_exemption': property_obj.homestead_exemption,
                'agricultural_exemption': property_obj.agricultural_exemption,
                'redemption_period_months': property_obj.redemption_period_months
            }
        
        response_data.append(sale_data)
    
    return response_data

@router.post("/{county_id}/tax-sales", response_model=TaxSaleResponse)
def create_tax_sale(
    county_id: int,
    tax_sale_data: TaxSaleBase,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # Verify county exists
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=400, detail="County not found")
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == tax_sale_data.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=400, detail="Property not found")
    
    # Calculate total judgment
    total_judgment = (
        tax_sale_data.taxes_owed +
        tax_sale_data.interest_penalties +
        tax_sale_data.court_costs +
        tax_sale_data.attorney_fees
    )
    
    # Create tax sale
    db_tax_sale = TaxSale(
        county_id=county_id,
        property_id=tax_sale_data.property_id,
        sale_date=tax_sale_data.sale_date,
        minimum_bid=tax_sale_data.minimum_bid,
        taxes_owed=tax_sale_data.taxes_owed,
        interest_penalties=tax_sale_data.interest_penalties,
        court_costs=tax_sale_data.court_costs,
        attorney_fees=tax_sale_data.attorney_fees,
        total_judgment=total_judgment,
        constable_precinct=tax_sale_data.constable_precinct,
        case_number=tax_sale_data.case_number
    )
    
    db.add(db_tax_sale)
    db.commit()
    db.refresh(db_tax_sale)
    
    return db_tax_sale

@router.get("/{county_id}/procedures")
def get_county_procedures(
    county_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get specific procedures and requirements for a county"""
    
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    
    # County-specific procedures and requirements
    procedures = {
        "county_name": county.name,
        "auction_type": county.auction_type,
        "auction_schedule": county.auction_schedule,
        "auction_location": county.auction_location,
        "website_url": county.website_url,
        "special_procedures": county.special_procedures,
        "contact_info": county.contact_info
    }
    
    # Add specific requirements based on county
    if county.name.lower() == 'collin':
        procedures.update({
            "bidder_requirements": [
                "Must obtain $10 no-taxes-due certificate in advance",
                "Certificate valid for 90 days",
                "Must present certificate at sale"
            ],
            "payment_requirements": [
                "Cash or cashier's check required immediately",
                "No personal checks or financing accepted"
            ],
            "deed_information": {
                "deed_type": "Constable's Deed",
                "warranty": "Deed without warranty",
                "recording_required": True
            },
            "redemption_periods": {
                "standard": "180 days (6 months)",
                "homestead_agricultural": "2 years",
                "penalty_rates": {
                    "first_year": "25%",
                    "second_year": "50%"
                }
            }
        })
    elif county.name.lower() == 'dallas':
        procedures.update({
            "bidder_requirements": [
                "Must register on RealAuction platform",
                "Must obtain no-delinquent-taxes certificate",
                "May require deposit for high-value bids"
            ],
            "payment_requirements": [
                "Wire transfer or cashier's check",
                "Payment due by next business day",
                "Platform fees may apply"
            ],
            "deed_information": {
                "deed_type": "Sheriff's Deed",
                "warranty": "Deed without warranty",
                "recording_handled_by_county": True
            },
            "redemption_periods": {
                "standard": "180 days (6 months)",
                "homestead_agricultural": "2 years",
                "penalty_rates": {
                    "first_year": "25%",
                    "second_year": "50%"
                }
            }
        })
    
    return procedures

@router.get("/{county_id}/statistics")
def get_county_statistics(
    county_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get detailed statistics for a county"""
    
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    
    # Get all tax sales for the county
    all_sales = db.query(TaxSale).filter(TaxSale.county_id == county_id).all()
    sold_sales = [sale for sale in all_sales if sale.sale_status == 'sold']
    struck_off_sales = [sale for sale in all_sales if sale.sale_status == 'struck_off']
    
    # Calculate statistics
    total_sales = len(all_sales)
    total_sold = len(sold_sales)
    total_struck_off = len(struck_off_sales)
    
    if sold_sales:
        avg_winning_bid = sum(float(sale.winning_bid) for sale in sold_sales if sale.winning_bid) / len([s for s in sold_sales if s.winning_bid])
        avg_minimum_bid = sum(float(sale.minimum_bid) for sale in sold_sales) / len(sold_sales)
        avg_premium = ((avg_winning_bid - avg_minimum_bid) / avg_minimum_bid * 100) if avg_minimum_bid > 0 else 0
    else:
        avg_winning_bid = 0
        avg_minimum_bid = 0
        avg_premium = 0
    
    # Property type breakdown
    property_types = {}
    for sale in all_sales:
        if sale.property and sale.property.property_type:
            prop_type = sale.property.property_type
            if prop_type not in property_types:
                property_types[prop_type] = 0
            property_types[prop_type] += 1
    
    statistics = {
        "county_name": county.name,
        "total_tax_sales": total_sales,
        "total_sold": total_sold,
        "total_struck_off": total_struck_off,
        "sale_success_rate": (total_sold / total_sales * 100) if total_sales > 0 else 0,
        "average_winning_bid": round(avg_winning_bid, 2),
        "average_minimum_bid": round(avg_minimum_bid, 2),
        "average_premium_percent": round(avg_premium, 2),
        "property_type_breakdown": property_types,
        "upcoming_sales_count": len([sale for sale in all_sales if sale.is_upcoming]),
        "struck_off_rate": (total_struck_off / total_sales * 100) if total_sales > 0 else 0
    }
    
    return statistics