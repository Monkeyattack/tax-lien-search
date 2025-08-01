# Tax Lien Search - Texas Tax Deed Investment Tracker

A comprehensive web application for tracking and managing tax lien investments in Texas, with specialized support for Collin and Dallas counties.

## Features

### Core Functionality
- **Property Search & Analysis**: Search tax sale properties with detailed metrics and ROI calculations
- **Investment Tracking**: Monitor purchases, redemption periods, and returns
- **County-Specific Support**: Tailored procedures for Collin County (in-person auctions) and Dallas County (online auctions)
- **Automated Alerts**: Email notifications for auction dates, redemption deadlines, and important milestones
- **Document Management**: Store deeds, receipts, and legal documents
- **ROI Calculator**: Calculate potential returns based on Texas redemption laws (25%/50% penalties)

### Texas Tax Deed Rules (Built Into System)
- **Redemption Periods**: 180 days (standard) or 2 years (homestead/agricultural)
- **Penalty Rates**: 25% first year, 50% second year for redemption
- **Auction Schedule**: First Tuesday of each month
- **Payment Requirements**: Cash/cashier's check required immediately

### Investment Analysis
- Real-time ROI calculations
- Risk assessment scoring
- Portfolio performance tracking
- Break-even analysis
- Comparative county statistics

## Technology Stack

### Backend
- **FastAPI** (Python 3.12+)
- **SQLAlchemy** with SQLite (dev) / PostgreSQL (prod)
- **JWT Authentication** with bcrypt password hashing
- **SendGrid** for email notifications
- **Pydantic** for data validation

### Frontend
- **React 18** with React Router
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **Heroicons** for UI icons
- **React Hook Form** for form handling

### Database Schema
- Users and authentication
- Counties with specific procedures
- Properties with detailed attributes
- Tax sales and auction data
- Investments with redemption tracking
- Alerts and notifications
- Document storage
- Research notes and valuations

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd tax-lien-search
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Configure environment variables**:
   Edit `.env` file with your settings:
   ```env
   SECRET_KEY=your-secret-key-here
   SENDGRID_API_KEY=your-sendgrid-api-key
   FROM_EMAIL=your-email@domain.com
   ```

4. **Start the backend**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   cd backend
   python main.py
   ```

5. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm start
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

### Getting Started
1. **Register an account** at http://localhost:3000/register
2. **Log in** and explore the dashboard
3. **Browse counties** to understand local procedures
4. **Search properties** for investment opportunities
5. **Track investments** and monitor redemption periods

### Key Workflows

#### Researching Properties
1. Navigate to Properties section
2. Filter by county, property type, and value range
3. Analyze potential ROI and risk factors
4. Save research notes and property valuations

#### Tracking Investments
1. Record property purchases with all relevant details
2. Monitor redemption deadlines automatically
3. Calculate potential returns based on holding period
4. Receive email alerts for important dates

#### Managing Alerts
1. Set up custom notifications for various events
2. Receive redemption deadline warnings
3. Get notified of upcoming auctions
4. Track portfolio performance metrics

## County-Specific Features

### Collin County
- **Auction Type**: In-person at courthouse steps
- **Schedule**: First Tuesday, 10:00 AM - 4:00 PM
- **Requirements**: $10 no-taxes-due certificate required
- **Payment**: Cash/cashier's check immediately
- **Deed Type**: Constable's Deed without warranty

### Dallas County
- **Auction Type**: Online via RealAuction platform
- **Schedule**: First Tuesday (online bidding)
- **Requirements**: Platform registration and no-taxes-due certificate
- **Payment**: Wire transfer/cashier's check by next business day
- **Deed Type**: Sheriff's Deed without warranty

## API Documentation

The backend provides a comprehensive REST API with the following endpoints:

- **Authentication**: `/api/auth/*` - User registration, login, profile management
- **Properties**: `/api/properties/*` - Property search, details, and analysis
- **Investments**: `/api/investments/*` - Investment tracking and management
- **Counties**: `/api/counties/*` - County information and procedures
- **Alerts**: `/api/alerts/*` - Notification management

Full API documentation is available at http://localhost:8000/docs when running the backend.

## Development

### Project Structure
```
tax-lien-search/
├── backend/                 # FastAPI backend
│   ├── models/             # Database models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── main.py            # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── contexts/      # React contexts
│   └── public/
├── database/              # Database schema and migrations
├── docs/                  # Documentation
└── setup.py              # Setup script
```

### Database Migrations
The application uses SQLAlchemy for database management. The initial schema is created automatically on first run.

### Adding New Features
1. Backend: Add models, routers, and services as needed
2. Frontend: Create components and pages following existing patterns
3. Update API documentation and type definitions
4. Add tests for new functionality

## Deployment

### Production Environment
1. **Backend**: Deploy to VPS with Gunicorn/uWSGI
2. **Frontend**: Build and serve static files
3. **Database**: Use PostgreSQL for production
4. **Email**: Configure SendGrid with proper API keys
5. **SSL**: Use Let's Encrypt or CloudFlare SSL

### Environment Variables
Set the following in production:
```env
APP_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
SENDGRID_API_KEY=your-production-key
SECRET_KEY=secure-random-key
```

## Legal and Compliance

⚠️ **Important Disclaimer**: This application is for informational and tracking purposes only. Users are responsible for:

- Verifying all property and legal information independently
- Complying with local laws and regulations
- Conducting proper due diligence before investing
- Understanding the risks of tax lien investments

Tax lien investing involves significant risks and requires thorough research and legal compliance.

## Support

For questions, issues, or feature requests:
- Check the API documentation at `/docs`
- Review county-specific procedures in the Counties section
- Consult with legal professionals for investment advice

## License

This project is for personal/educational use. Commercial use requires appropriate licensing and compliance with all applicable laws and regulations.

---

**Built for Texas tax lien investors by investors** 🏠💰