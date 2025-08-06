from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from database import get_database
from models.saved_search import SavedSearch, SearchResult
from models.property import Property
from models.property_enrichment import PropertyEnrichment
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class SavedSearchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    email_alerts: bool = True
    alert_frequency: str = Field(default="daily", pattern="^(instant|daily|weekly)$")

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    email_alerts: Optional[bool] = None
    alert_frequency: Optional[str] = Field(None, pattern="^(instant|daily|weekly)$")
    is_active: Optional[bool] = None

class SavedSearchResponse(SavedSearchBase):
    id: int
    user_id: int
    is_active: bool
    match_count: int
    last_alert_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SearchResultResponse(BaseModel):
    id: int
    property_id: int
    matched_at: datetime
    alert_sent: bool
    property: Dict[str, Any]
    
    class Config:
        from_attributes = True

class SavedSearchWithResults(SavedSearchResponse):
    recent_matches: List[SearchResultResponse] = []
    new_matches_count: int = 0

@router.get("/", response_model=List[SavedSearchResponse])
def get_saved_searches(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get all saved searches for the current user"""
    query = db.query(SavedSearch).filter(SavedSearch.user_id == current_user.id)
    
    if active_only:
        query = query.filter(SavedSearch.is_active == True)
    
    searches = query.order_by(SavedSearch.created_at.desc()).offset(skip).limit(limit).all()
    return searches

@router.get("/{search_id}", response_model=SavedSearchWithResults)
def get_saved_search(
    search_id: int,
    include_results: bool = True,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get a specific saved search with recent results"""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    response = SavedSearchResponse.from_orm(search).dict()
    
    if include_results:
        # Get recent matches
        recent_results = db.query(SearchResult).join(
            Property
        ).options(
            joinedload(SearchResult.property).joinedload(Property.enrichment)
        ).filter(
            SearchResult.saved_search_id == search_id
        ).order_by(SearchResult.matched_at.desc()).limit(10).all()
        
        # Format results
        response['recent_matches'] = []
        for result in recent_results:
            prop = result.property
            property_data = {
                'id': prop.id,
                'property_address': prop.property_address,
                'city': prop.city,
                'state': prop.state,
                'zip_code': prop.zip_code,
                'property_type': prop.property_type,
                'assessed_value': float(prop.assessed_value) if prop.assessed_value else None,
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                'year_built': prop.year_built,
                'investment_score': float(prop.enrichment.investment_score) if prop.enrichment and prop.enrichment.investment_score else None
            }
            
            response['recent_matches'].append({
                'id': result.id,
                'property_id': result.property_id,
                'matched_at': result.matched_at,
                'alert_sent': result.alert_sent,
                'property': property_data
            })
        
        # Count new matches since last alert
        last_alert = search.last_alert_sent or search.created_at
        new_matches = db.query(func.count(SearchResult.id)).filter(
            SearchResult.saved_search_id == search_id,
            SearchResult.matched_at > last_alert
        ).scalar()
        response['new_matches_count'] = new_matches
    
    return response

@router.post("/", response_model=SavedSearchResponse)
def create_saved_search(
    search_data: SavedSearchCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Create a new saved search"""
    # Check user's saved search limit (optional)
    search_count = db.query(func.count(SavedSearch.id)).filter(
        SavedSearch.user_id == current_user.id,
        SavedSearch.is_active == True
    ).scalar()
    
    if search_count >= 10:  # Limit to 10 active searches per user
        raise HTTPException(
            status_code=400,
            detail="Maximum number of saved searches reached. Please deactivate an existing search."
        )
    
    # Create the saved search
    saved_search = SavedSearch(
        user_id=current_user.id,
        **search_data.dict()
    )
    
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    
    # Run initial search to populate results
    run_search_for_saved_search(db, saved_search)
    
    return saved_search

@router.put("/{search_id}", response_model=SavedSearchResponse)
def update_saved_search(
    search_id: int,
    search_data: SavedSearchUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Update a saved search"""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    # Update fields
    update_data = search_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(search, field, value)
    
    search.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(search)
    
    # If filters changed, re-run the search
    if 'filters' in update_data:
        # Clear old results
        db.query(SearchResult).filter(SearchResult.saved_search_id == search_id).delete()
        db.commit()
        
        # Run new search
        run_search_for_saved_search(db, search)
    
    return search

@router.delete("/{search_id}")
def delete_saved_search(
    search_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved search"""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    db.delete(search)
    db.commit()
    
    return {"message": "Saved search deleted successfully"}

@router.post("/{search_id}/run")
def run_saved_search(
    search_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Manually run a saved search to find new matches"""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    # Run the search
    new_matches = run_search_for_saved_search(db, search)
    
    return {
        "message": f"Search completed. Found {new_matches} new properties.",
        "new_matches": new_matches
    }

@router.post("/{search_id}/test")
def test_saved_search(
    search_id: int,
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Test a saved search to see what properties it would match"""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    # Build query based on filters
    query = build_property_query(db, search.filters)
    
    # Get sample results
    properties = query.limit(limit).all()
    
    # Format results
    results = []
    for prop in properties:
        enrichment = prop.enrichment
        results.append({
            'id': prop.id,
            'property_address': prop.property_address,
            'city': prop.city,
            'state': prop.state,
            'property_type': prop.property_type,
            'assessed_value': float(prop.assessed_value) if prop.assessed_value else None,
            'bedrooms': prop.bedrooms,
            'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
            'year_built': prop.year_built,
            'investment_score': float(enrichment.investment_score) if enrichment and enrichment.investment_score else None,
            'roi_percentage': float(enrichment.roi_percentage) if enrichment and enrichment.roi_percentage else None
        })
    
    total_count = query.count()
    
    return {
        'total_matches': total_count,
        'sample_results': results,
        'filters_applied': search.filters
    }

def build_property_query(db: Session, filters: Dict[str, Any]):
    """Build a SQLAlchemy query based on saved search filters"""
    query = db.query(Property).outerjoin(PropertyEnrichment)
    
    # County filter
    if filters.get('counties'):
        query = query.filter(Property.county_id.in_(filters['counties']))
    
    # Property type filter
    if filters.get('property_types'):
        query = query.filter(Property.property_type.in_(filters['property_types']))
    
    # Value filters
    if filters.get('min_value'):
        query = query.filter(Property.assessed_value >= filters['min_value'])
    
    if filters.get('max_value'):
        query = query.filter(Property.assessed_value <= filters['max_value'])
    
    # Property characteristics
    if filters.get('bedrooms_min'):
        query = query.filter(Property.bedrooms >= filters['bedrooms_min'])
    
    if filters.get('bathrooms_min'):
        query = query.filter(Property.bathrooms >= filters['bathrooms_min'])
    
    if filters.get('year_built_after'):
        query = query.filter(Property.year_built >= filters['year_built_after'])
    
    if filters.get('lot_size_min'):
        query = query.filter(Property.lot_size >= filters['lot_size_min'])
    
    # Boolean filters
    if filters.get('homestead_only'):
        query = query.filter(Property.homestead_exemption == True)
    
    if filters.get('no_homestead'):
        query = query.filter(Property.homestead_exemption == False)
    
    # Investment metrics
    if filters.get('min_investment_score'):
        query = query.filter(PropertyEnrichment.investment_score >= filters['min_investment_score'])
    
    if filters.get('min_roi'):
        query = query.filter(PropertyEnrichment.roi_percentage >= filters['min_roi'])
    
    if filters.get('min_cap_rate'):
        query = query.filter(PropertyEnrichment.cap_rate >= filters['min_cap_rate'])
    
    if filters.get('has_zestimate'):
        query = query.filter(PropertyEnrichment.zestimate.isnot(None))
    
    # Location filters
    if filters.get('cities'):
        query = query.filter(Property.city.in_(filters['cities']))
    
    if filters.get('zip_codes'):
        query = query.filter(Property.zip_code.in_(filters['zip_codes']))
    
    return query

def run_search_for_saved_search(db: Session, saved_search: SavedSearch) -> int:
    """Run a saved search and store new matches"""
    # Get existing property IDs for this search
    existing_ids = db.query(SearchResult.property_id).filter(
        SearchResult.saved_search_id == saved_search.id
    ).all()
    existing_ids = {id[0] for id in existing_ids}
    
    # Build and run query
    query = build_property_query(db, saved_search.filters)
    
    # Only get properties not already in results
    if existing_ids:
        query = query.filter(~Property.id.in_(existing_ids))
    
    new_properties = query.all()
    
    # Create search results
    new_matches = 0
    for prop in new_properties:
        result = SearchResult(
            saved_search_id=saved_search.id,
            property_id=prop.id
        )
        db.add(result)
        new_matches += 1
    
    # Update match count
    saved_search.match_count = len(existing_ids) + new_matches
    
    db.commit()
    
    return new_matches