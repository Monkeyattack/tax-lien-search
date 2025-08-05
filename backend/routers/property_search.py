from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from database import get_database
from models import Property, County, TaxSale, PropertyEnrichment, User
from routers.auth import get_current_user

router = APIRouter(prefix="/property-search", tags=["property-search"])


class EnrichedPropertyResponse(BaseModel):
    id: int
    parcel_number: str
    owner_name: str
    property_address: str
    city: Optional[str]
    state: str
    zip_code: Optional[str]
    property_type: Optional[str]
    assessed_value: Optional[float]
    market_value: Optional[float]
    
    # County info
    county_name: str
    
    # Tax sale info
    next_sale_date: Optional[date]
    minimum_bid: Optional[float]
    taxes_owed: Optional[float]
    
    # Enrichment data
    zestimate: Optional[float]
    monthly_rent_estimate: Optional[float]
    investment_score: Optional[float]
    roi_percentage: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_footage: Optional[int]
    year_built: Optional[int]
    lot_size_sqft: Optional[int]
    
    # Neighborhood
    school_rating: Optional[float]
    walk_score: Optional[int]
    
    class Config:
        from_attributes = True


class PropertySearchRequest(BaseModel):
    # Location filters
    county_ids: Optional[List[int]] = []
    cities: Optional[List[str]] = []
    zip_codes: Optional[List[str]] = []
    
    # Property filters
    property_types: Optional[List[str]] = []
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    
    # Value filters
    min_assessed_value: Optional[float] = None
    max_assessed_value: Optional[float] = None
    min_zestimate: Optional[float] = None
    max_zestimate: Optional[float] = None
    min_minimum_bid: Optional[float] = None
    max_minimum_bid: Optional[float] = None
    
    # Investment filters
    min_investment_score: Optional[float] = None
    min_roi_percentage: Optional[float] = None
    min_monthly_rent: Optional[float] = None
    
    # Sale filters
    has_upcoming_sale: Optional[bool] = None
    sale_date_start: Optional[date] = None
    sale_date_end: Optional[date] = None
    
    # Search text
    search_text: Optional[str] = None
    
    # Sorting
    sort_by: Optional[str] = "investment_score"  # investment_score, roi_percentage, minimum_bid, sale_date
    sort_order: Optional[str] = "desc"  # asc or desc


@router.post("/search", response_model=List[EnrichedPropertyResponse])
def search_properties(
    request: PropertySearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Search properties with advanced filters and enrichment data"""
    
    # Base query with joins
    query = db.query(Property).join(County).outerjoin(PropertyEnrichment)
    
    # Join with tax sales subquery to get next sale
    next_sale_subq = db.query(
        TaxSale.property_id,
        func.min(TaxSale.sale_date).label('next_sale_date')
    ).filter(
        TaxSale.sale_date >= datetime.now().date(),
        TaxSale.sale_status == 'scheduled'
    ).group_by(TaxSale.property_id).subquery()
    
    query = query.outerjoin(
        next_sale_subq,
        Property.id == next_sale_subq.c.property_id
    ).outerjoin(
        TaxSale,
        and_(
            TaxSale.property_id == Property.id,
            TaxSale.sale_date == next_sale_subq.c.next_sale_date
        )
    )
    
    # Apply filters
    
    # Location filters
    if request.county_ids:
        query = query.filter(Property.county_id.in_(request.county_ids))
    
    if request.cities:
        query = query.filter(Property.city.in_(request.cities))
    
    if request.zip_codes:
        query = query.filter(Property.zip_code.in_(request.zip_codes))
    
    # Property type filter
    if request.property_types:
        query = query.filter(Property.property_type.in_(request.property_types))
    
    # Property characteristics filters
    if request.min_bedrooms is not None:
        query = query.filter(Property.bedrooms >= request.min_bedrooms)
    if request.max_bedrooms is not None:
        query = query.filter(Property.bedrooms <= request.max_bedrooms)
    
    if request.min_bathrooms is not None:
        query = query.filter(Property.bathrooms >= request.min_bathrooms)
    if request.max_bathrooms is not None:
        query = query.filter(Property.bathrooms <= request.max_bathrooms)
    
    if request.min_sqft is not None:
        query = query.filter(Property.square_footage >= request.min_sqft)
    if request.max_sqft is not None:
        query = query.filter(Property.square_footage <= request.max_sqft)
    
    if request.min_year_built is not None:
        query = query.filter(Property.year_built >= request.min_year_built)
    if request.max_year_built is not None:
        query = query.filter(Property.year_built <= request.max_year_built)
    
    # Value filters
    if request.min_assessed_value is not None:
        query = query.filter(Property.assessed_value >= request.min_assessed_value)
    if request.max_assessed_value is not None:
        query = query.filter(Property.assessed_value <= request.max_assessed_value)
    
    if request.min_zestimate is not None:
        query = query.filter(PropertyEnrichment.zestimate >= request.min_zestimate)
    if request.max_zestimate is not None:
        query = query.filter(PropertyEnrichment.zestimate <= request.max_zestimate)
    
    if request.min_minimum_bid is not None:
        query = query.filter(TaxSale.minimum_bid >= request.min_minimum_bid)
    if request.max_minimum_bid is not None:
        query = query.filter(TaxSale.minimum_bid <= request.max_minimum_bid)
    
    # Investment filters
    if request.min_investment_score is not None:
        query = query.filter(PropertyEnrichment.investment_score >= request.min_investment_score)
    
    if request.min_roi_percentage is not None:
        query = query.filter(PropertyEnrichment.roi_percentage >= request.min_roi_percentage)
    
    if request.min_monthly_rent is not None:
        query = query.filter(PropertyEnrichment.monthly_rent_estimate >= request.min_monthly_rent)
    
    # Sale filters
    if request.has_upcoming_sale:
        query = query.filter(next_sale_subq.c.next_sale_date.isnot(None))
    
    if request.sale_date_start:
        query = query.filter(TaxSale.sale_date >= request.sale_date_start)
    
    if request.sale_date_end:
        query = query.filter(TaxSale.sale_date <= request.sale_date_end)
    
    # Text search
    if request.search_text:
        search_term = f"%{request.search_text}%"
        query = query.filter(
            or_(
                Property.property_address.ilike(search_term),
                Property.owner_name.ilike(search_term),
                Property.parcel_number.ilike(search_term),
                Property.city.ilike(search_term),
                Property.zip_code.ilike(search_term)
            )
        )
    
    # Sorting
    if request.sort_by == "investment_score":
        order_col = PropertyEnrichment.investment_score
    elif request.sort_by == "roi_percentage":
        order_col = PropertyEnrichment.roi_percentage
    elif request.sort_by == "minimum_bid":
        order_col = TaxSale.minimum_bid
    elif request.sort_by == "sale_date":
        order_col = TaxSale.sale_date
    elif request.sort_by == "assessed_value":
        order_col = Property.assessed_value
    else:
        order_col = PropertyEnrichment.investment_score
    
    if request.sort_order == "asc":
        query = query.order_by(order_col.asc().nullslast())
    else:
        query = query.order_by(order_col.desc().nullsfirst())
    
    # Execute query
    properties = query.offset(skip).limit(limit).all()
    
    # Format response
    results = []
    for prop in properties:
        # Extract school rating from neighborhood data
        school_rating = None
        walk_score = None
        if prop.enrichment and prop.enrichment.neighborhood_data:
            schools = prop.enrichment.neighborhood_data.get('schools', [])
            if schools:
                ratings = [s.get('rating', 0) for s in schools if s.get('rating')]
                school_rating = sum(ratings) / len(ratings) if ratings else None
            
            walk_score = prop.enrichment.neighborhood_data.get('demographics', {}).get('walkability_score')
        
        # Get next tax sale info
        next_sale = None
        for sale in prop.tax_sales:
            if sale.sale_date >= datetime.now().date() and sale.sale_status == 'scheduled':
                if not next_sale or sale.sale_date < next_sale.sale_date:
                    next_sale = sale
        
        result = EnrichedPropertyResponse(
            id=prop.id,
            parcel_number=prop.parcel_number,
            owner_name=prop.owner_name,
            property_address=prop.property_address,
            city=prop.city,
            state=prop.state,
            zip_code=prop.zip_code,
            property_type=prop.property_type,
            assessed_value=float(prop.assessed_value) if prop.assessed_value else None,
            market_value=float(prop.market_value) if prop.market_value else None,
            
            # County
            county_name=prop.county.county_name if prop.county else '',
            
            # Tax sale
            next_sale_date=next_sale.sale_date if next_sale else None,
            minimum_bid=float(next_sale.minimum_bid) if next_sale else None,
            taxes_owed=float(next_sale.taxes_owed) if next_sale else None,
            
            # Enrichment
            zestimate=float(prop.enrichment.zestimate) if prop.enrichment and prop.enrichment.zestimate else None,
            monthly_rent_estimate=float(prop.enrichment.monthly_rent_estimate) if prop.enrichment and prop.enrichment.monthly_rent_estimate else None,
            investment_score=float(prop.enrichment.investment_score) if prop.enrichment and prop.enrichment.investment_score else None,
            roi_percentage=float(prop.enrichment.roi_percentage) if prop.enrichment and prop.enrichment.roi_percentage else None,
            
            # Property details from base or enrichment
            bedrooms=prop.bedrooms,
            bathrooms=float(prop.bathrooms) if prop.bathrooms else None,
            square_footage=prop.square_footage,
            year_built=prop.year_built,
            lot_size_sqft=int(prop.lot_size) if prop.lot_size else None,
            
            # Neighborhood
            school_rating=school_rating,
            walk_score=walk_score
        )
        
        results.append(result)
    
    return results


@router.get("/filters")
def get_filter_options(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get available filter options based on data in database"""
    
    # Get counties
    counties = db.query(County.id, County.county_name).all()
    
    # Get unique cities
    cities = db.query(Property.city).distinct().filter(Property.city.isnot(None)).all()
    cities = [c[0] for c in cities if c[0]]
    
    # Get property types
    property_types = db.query(Property.property_type).distinct().filter(Property.property_type.isnot(None)).all()
    property_types = [p[0] for p in property_types if p[0]]
    
    # Get value ranges
    value_stats = db.query(
        func.min(Property.assessed_value).label('min_assessed'),
        func.max(Property.assessed_value).label('max_assessed'),
        func.min(PropertyEnrichment.zestimate).label('min_zestimate'),
        func.max(PropertyEnrichment.zestimate).label('max_zestimate'),
        func.min(TaxSale.minimum_bid).label('min_bid'),
        func.max(TaxSale.minimum_bid).label('max_bid')
    ).outerjoin(PropertyEnrichment).outerjoin(TaxSale).first()
    
    return {
        "counties": [{"id": c[0], "name": c[1]} for c in counties],
        "cities": sorted(cities),
        "property_types": sorted(property_types),
        "value_ranges": {
            "assessed_value": {
                "min": float(value_stats.min_assessed) if value_stats.min_assessed else 0,
                "max": float(value_stats.max_assessed) if value_stats.max_assessed else 1000000
            },
            "zestimate": {
                "min": float(value_stats.min_zestimate) if value_stats.min_zestimate else 0,
                "max": float(value_stats.max_zestimate) if value_stats.max_zestimate else 1000000
            },
            "minimum_bid": {
                "min": float(value_stats.min_bid) if value_stats.min_bid else 0,
                "max": float(value_stats.max_bid) if value_stats.max_bid else 100000
            }
        }
    }


@router.get("/saved-searches")
def get_saved_searches(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get user's saved searches"""
    # TODO: Implement saved searches model
    return []


@router.post("/saved-searches")
def save_search(
    name: str,
    filters: PropertySearchRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Save a search with filters for alerts"""
    # TODO: Implement saved searches
    return {"message": "Search saved", "id": 1}