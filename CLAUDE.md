# CLAUDE.md - Tax Lien Search Application

## Project Overview
A comprehensive tax lien/deed search and tracking application for Texas tax sales, focusing on Collin and Dallas counties. This system helps investors research, track, and manage tax deed investments with built-in ROI calculations and redemption period monitoring.

## Architecture
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: React with Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **Email**: SendGrid for notifications
- **Authentication**: JWT-based user sessions

## Key Features
1. **Property Search & Analysis**: Search tax sale properties with detailed metrics
2. **Investment Tracking**: Track purchases, redemption periods, and ROI
3. **County Integration**: Support for Collin County (in-person) and Dallas County (online) procedures
4. **Automated Alerts**: Email notifications for auction dates, redemption deadlines
5. **Document Management**: Store deeds, receipts, and legal documents
6. **ROI Calculator**: Calculate potential returns based on Texas redemption laws (25%/50% penalties)

## Texas Tax Deed Rules (Built Into System)
- **Redemption Periods**: 180 days (standard) or 2 years (homestead/agricultural)
- **Penalties**: 25% first year, 50% second year for redemption
- **Auction Schedule**: First Tuesday of each month
- **Payment**: Cash/cashier's check required immediately

## Development Commands
- Setup: `python setup.py`
- Backend: `cd backend && uvicorn main:app --reload`
- Frontend: `cd frontend && npm start`
- Database: `alembic upgrade head`
- Tests: `pytest`

## Key Files
- `backend/main.py`: FastAPI application entry point
- `backend/models/`: Database models for properties, investments, users
- `backend/routers/`: API routes for different features
- `frontend/src/components/`: React components
- `database/schema.sql`: Database schema and migrations

## External Dependencies
- **County Data Sources**: Manual input (no APIs available)
- **SendGrid**: Email notifications and alerts
- **Property APIs**: Integration with county assessor data when available

## Deployment
- **Development**: Local SQLite database
- **Production**: Deploy to VPSServer1 (172.93.51.42)
- **Domain**: webdev.monkeyattack.com or subdomain

## Security Notes
- Never commit API keys or sensitive data
- Use environment variables for all secrets
- Implement proper authentication for multi-user support
- Validate all property data inputs

---
Last Updated: 2025-07-31