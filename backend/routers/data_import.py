from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from models import Property, TaxSale, County, PropertyValuation, Alert
from routers.auth import get_current_user
from services.scraper_service import ScraperService
from models.user import User

router = APIRouter(prefix="/data-import", tags=["data-import"])

@router.post("/csv/properties")
async def import_properties_csv(
    file: UploadFile = File(...),
    county_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import properties from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        # Expected columns
        required_columns = ['parcel_number', 'owner_name', 'property_address']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if property already exists
                existing = db.query(Property).filter(
                    Property.parcel_number == row['parcel_number']
                ).first()
                
                if not existing:
                    property_data = {
                        'parcel_number': str(row['parcel_number']),
                        'owner_name': row['owner_name'],
                        'property_address': row['property_address'],
                        'county_id': county_id or row.get('county_id', 1),
                        'property_type': row.get('property_type', 'residential'),
                        'legal_description': row.get('legal_description', ''),
                        'property_city': row.get('city', ''),
                        'property_zip': str(row.get('zip', '')),
                        'tax_rate': float(row.get('tax_rate', 0.02)),
                        'homestead_exemption': bool(row.get('homestead_exemption', False)),
                        'agricultural_exemption': bool(row.get('agricultural_exemption', False)),
                        'senior_exemption': bool(row.get('senior_exemption', False)),
                        'land_size_acres': float(row.get('land_size_acres', 0)) if pd.notna(row.get('land_size_acres')) else None,
                        'building_sqft': int(row.get('building_sqft', 0)) if pd.notna(row.get('building_sqft')) else None,
                        'year_built': int(row.get('year_built', 0)) if pd.notna(row.get('year_built')) else None,
                        'last_sale_date': pd.to_datetime(row.get('last_sale_date')) if pd.notna(row.get('last_sale_date')) else None,
                        'last_sale_amount': float(row.get('last_sale_amount', 0)) if pd.notna(row.get('last_sale_amount')) else None,
                    }
                    
                    new_property = Property(**property_data)
                    db.add(new_property)
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported_count,
            "errors": errors,
            "total_rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@router.post("/csv/tax-sales")
async def import_tax_sales_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import tax sales from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        required_columns = ['parcel_number', 'sale_date', 'minimum_bid']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Find property by parcel number
                property = db.query(Property).filter(
                    Property.parcel_number == str(row['parcel_number'])
                ).first()
                
                if not property:
                    errors.append(f"Row {index + 2}: Property with parcel {row['parcel_number']} not found")
                    continue
                
                # Check if tax sale already exists
                sale_date = pd.to_datetime(row['sale_date']).date()
                existing = db.query(TaxSale).filter(
                    TaxSale.property_id == property.id,
                    TaxSale.sale_date == sale_date
                ).first()
                
                if not existing:
                    tax_sale_data = {
                        'property_id': property.id,
                        'county_id': property.county_id,
                        'sale_date': sale_date,
                        'minimum_bid': float(row['minimum_bid']),
                        'taxes_owed': float(row.get('taxes_owed', row['minimum_bid'])),
                        'interest_penalties': float(row.get('interest_penalties', 0)),
                        'court_costs': float(row.get('court_costs', 0)),
                        'attorney_fees': float(row.get('attorney_fees', 0)),
                        'total_judgment': float(row.get('total_judgment', row['minimum_bid'])),
                        'sale_status': row.get('sale_status', 'scheduled'),
                        'constable_precinct': str(row.get('constable_precinct', '')),
                        'case_number': str(row.get('case_number', '')),
                    }
                    
                    new_sale = TaxSale(**tax_sale_data)
                    db.add(new_sale)
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported_count,
            "errors": errors,
            "total_rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@router.post("/excel/combined")
async def import_excel_combined(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import properties and tax sales from Excel file with multiple sheets"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format")
    
    try:
        contents = await file.read()
        excel_file = pd.ExcelFile(BytesIO(contents))
        
        results = {}
        
        # Import properties from 'Properties' sheet if exists
        if 'Properties' in excel_file.sheet_names:
            df_properties = pd.read_excel(excel_file, sheet_name='Properties')
            # Process properties similar to CSV import
            imported_properties = 0
            property_errors = []
            
            for index, row in df_properties.iterrows():
                try:
                    existing = db.query(Property).filter(
                        Property.parcel_number == str(row['parcel_number'])
                    ).first()
                    
                    if not existing:
                        property_data = {
                            'parcel_number': str(row['parcel_number']),
                            'owner_name': row['owner_name'],
                            'property_address': row['property_address'],
                            'county_id': int(row.get('county_id', 1)),
                            'property_type': row.get('property_type', 'residential'),
                            'legal_description': row.get('legal_description', ''),
                            'property_city': row.get('city', ''),
                            'property_zip': str(row.get('zip', '')),
                            'tax_rate': float(row.get('tax_rate', 0.02)),
                            'homestead_exemption': bool(row.get('homestead_exemption', False)),
                        }
                        
                        new_property = Property(**property_data)
                        db.add(new_property)
                        imported_properties += 1
                        
                except Exception as e:
                    property_errors.append(f"Row {index + 2}: {str(e)}")
            
            db.commit()
            results['properties'] = {
                'imported': imported_properties,
                'errors': property_errors
            }
        
        # Import tax sales from 'TaxSales' sheet if exists
        if 'TaxSales' in excel_file.sheet_names:
            df_sales = pd.read_excel(excel_file, sheet_name='TaxSales')
            imported_sales = 0
            sale_errors = []
            
            for index, row in df_sales.iterrows():
                try:
                    property = db.query(Property).filter(
                        Property.parcel_number == str(row['parcel_number'])
                    ).first()
                    
                    if property:
                        sale_date = pd.to_datetime(row['sale_date']).date()
                        existing = db.query(TaxSale).filter(
                            TaxSale.property_id == property.id,
                            TaxSale.sale_date == sale_date
                        ).first()
                        
                        if not existing:
                            tax_sale_data = {
                                'property_id': property.id,
                                'county_id': property.county_id,
                                'sale_date': sale_date,
                                'minimum_bid': float(row['minimum_bid']),
                                'taxes_owed': float(row.get('taxes_owed', row['minimum_bid'])),
                                'total_judgment': float(row.get('total_judgment', row['minimum_bid'])),
                                'sale_status': row.get('sale_status', 'scheduled'),
                            }
                            
                            new_sale = TaxSale(**tax_sale_data)
                            db.add(new_sale)
                            imported_sales += 1
                    else:
                        sale_errors.append(f"Row {index + 2}: Property not found")
                        
                except Exception as e:
                    sale_errors.append(f"Row {index + 2}: {str(e)}")
            
            db.commit()
            results['tax_sales'] = {
                'imported': imported_sales,
                'errors': sale_errors
            }
        
        return {
            "success": True,
            "results": results,
            "sheets_processed": list(results.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel: {str(e)}")

@router.get("/templates/{template_type}")
async def get_import_template(
    template_type: str,
    current_user: User = Depends(get_current_user)
):
    """Get CSV template for importing data"""
    templates = {
        "properties": {
            "columns": [
                "parcel_number", "owner_name", "property_address", "city", "zip",
                "property_type", "legal_description", "tax_rate", "homestead_exemption",
                "agricultural_exemption", "senior_exemption", "land_size_acres",
                "building_sqft", "year_built", "last_sale_date", "last_sale_amount"
            ],
            "sample_data": [
                {
                    "parcel_number": "123-456-789",
                    "owner_name": "John Doe",
                    "property_address": "123 Main St",
                    "city": "Dallas",
                    "zip": "75201",
                    "property_type": "residential",
                    "legal_description": "Lot 1, Block 2",
                    "tax_rate": 0.02,
                    "homestead_exemption": True,
                    "agricultural_exemption": False,
                    "senior_exemption": False,
                    "land_size_acres": 0.25,
                    "building_sqft": 2500,
                    "year_built": 1995,
                    "last_sale_date": "2020-01-15",
                    "last_sale_amount": 250000
                }
            ]
        },
        "tax_sales": {
            "columns": [
                "parcel_number", "sale_date", "minimum_bid", "taxes_owed",
                "interest_penalties", "court_costs", "attorney_fees",
                "total_judgment", "sale_status", "constable_precinct", "case_number"
            ],
            "sample_data": [
                {
                    "parcel_number": "123-456-789",
                    "sale_date": "2025-09-01",
                    "minimum_bid": 5000,
                    "taxes_owed": 3500,
                    "interest_penalties": 800,
                    "court_costs": 400,
                    "attorney_fees": 300,
                    "total_judgment": 5000,
                    "sale_status": "scheduled",
                    "constable_precinct": "1",
                    "case_number": "2025-12345"
                }
            ]
        }
    }
    
    if template_type not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return templates[template_type]

@router.post("/validate")
async def validate_import_file(
    file: UploadFile = File(...),
    import_type: str = "properties",
    current_user: User = Depends(get_current_user)
):
    """Validate import file before actual import"""
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Get expected columns based on import type
        if import_type == "properties":
            required_columns = ['parcel_number', 'owner_name', 'property_address']
        elif import_type == "tax_sales":
            required_columns = ['parcel_number', 'sale_date', 'minimum_bid']
        else:
            raise HTTPException(status_code=400, detail="Invalid import type")
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        # Validate data
        validation_errors = []
        
        if import_type == "properties":
            # Check for duplicate parcel numbers
            duplicates = df[df.duplicated(['parcel_number'], keep=False)]
            if not duplicates.empty:
                validation_errors.append(f"Duplicate parcel numbers found: {duplicates['parcel_number'].unique().tolist()}")
        
        elif import_type == "tax_sales":
            # Validate dates
            try:
                df['sale_date'] = pd.to_datetime(df['sale_date'])
            except:
                validation_errors.append("Invalid date format in sale_date column")
            
            # Validate numeric fields
            numeric_fields = ['minimum_bid', 'taxes_owed', 'total_judgment']
            for field in numeric_fields:
                if field in df.columns:
                    try:
                        df[field] = pd.to_numeric(df[field], errors='coerce')
                        if df[field].isna().any():
                            validation_errors.append(f"Non-numeric values found in {field} column")
                    except:
                        validation_errors.append(f"Error converting {field} to numeric")
        
        return {
            "valid": len(missing_columns) == 0 and len(validation_errors) == 0,
            "total_rows": len(df),
            "columns_found": df.columns.tolist(),
            "missing_columns": missing_columns,
            "validation_errors": validation_errors,
            "preview": df.head(5).to_dict(orient='records') if len(df) > 0 else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating file: {str(e)}")

@router.post("/scrape/{county_code}")
async def scrape_county_data(
    county_code: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scrape tax sale data for a specific county"""
    scraper_service = ScraperService(db)
    
    # Validate county code
    valid_counties = ['collin', 'dallas']
    if county_code not in valid_counties:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid county code. Valid options: {', '.join(valid_counties)}"
        )
    
    # Run scraping in background
    background_tasks.add_task(
        scraper_service.scrape_county,
        county_code,
        current_user
    )
    
    return {
        "message": f"Scraping initiated for {county_code} county",
        "status": "processing",
        "note": "Check alerts for completion status"
    }

@router.post("/scrape/all")
async def scrape_all_counties(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scrape tax sale data for all configured counties"""
    scraper_service = ScraperService(db)
    
    # Run scraping in background
    background_tasks.add_task(
        scraper_service.scrape_all_counties,
        current_user
    )
    
    return {
        "message": "Scraping initiated for all counties",
        "status": "processing",
        "counties": ['collin', 'dallas'],
        "note": "Check alerts for completion status"
    }

@router.get("/scrape/status")
async def get_scraping_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of recent scraping operations"""
    # Get recent alerts related to scraping
    recent_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.title.contains("Scraping")
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    return {
        "recent_operations": [
            {
                "id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "created_at": alert.created_at,
                "is_urgent": alert.is_urgent
            }
            for alert in recent_alerts
        ]
    }