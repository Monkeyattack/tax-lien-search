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

### CRITICAL: ALL CODE EXECUTION MUST BE ON VPS
**NEVER run Python, Node, or database commands locally on Windows.**
**ALWAYS SSH to VPS using the KEY: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42`**

### On VPS (172.93.51.42):
- SSH: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42`
- Setup: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search && python setup.py"`
- Backend: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search/backend && uvicorn main:app --reload --port 8000"`
- Frontend: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search/frontend && npm start"`
- Database: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search/backend && alembic upgrade head"`
- Tests: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search && pytest"`
- Deploy: `ssh -i ~/.ssh/tao_alpha_dca_key root@172.93.51.42 "cd /root/tax-lien-search && git pull && cd backend && pm2 restart tax-lien-api"`

### Local Development (Windows):
- **ONLY** for editing code files
- **NEVER** run Python or Node commands locally
- Use Git Bash for file operations only

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
- **Production Path**: /var/www/tax-lien-search
- **VPS**: VPSServer1 (172.93.51.42)
- **Domain**: tax.profithits.app
- **Backend Port**: 8000 (FastAPI)
- **Frontend**: Static build served by NGINX
- **Database**: SQLite at /var/www/tax-lien-search/backend/tax_lien_search.db
- **PM2 Process**: tax-lien-api
- **NGINX Config**: /etc/nginx/sites-available/tax-profithits

## Security Notes
- Never commit API keys or sensitive data
- Use environment variables for all secrets
- Implement proper authentication for multi-user support
- Validate all property data inputs

---
Last Updated: 2025-07-31