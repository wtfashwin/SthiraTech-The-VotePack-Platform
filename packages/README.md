# PackVote 2.0 - Complete Implementation Guide

## 🎉 Application Overview

**PackVote 2.0** is a unified group travel super-app that consolidates trip planning, itinerary management, social decision-making (polling), and expense tracking into a single, seamless web application.

### Core Features
- ✅ Trip Creation & Management
- ✅ Participant Invitation & Management
- ✅ Collaborative Day-by-Day Itinerary Building
- ✅ In-Activity Polling for Group Decisions
- ✅ Context-Aware Expense Tracking with Automatic Balance Calculation
- ✅ Real-time "Who Owes Whom" Settlements

---

## 🏗️ Architecture

### Frontend
- **Framework**: React 18+ with Vite & TypeScript
- **Styling**: Tailwind CSS
- **State Management**: 
  - Client State: Zustand (UI state)
  - Server State: TanStack Query v5 (data fetching/caching)
- **Forms**: React Hook Form + Zod validation
- **Routing**: React Router DOM v6
- **Animations**: Framer Motion
- **Notifications**: React Hot Toast

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic v2+
- **Database**: PostgreSQL 15+ with pgvector extension
- **Server**: Uvicorn

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Docker** and Docker Compose

### 1. Start the Database

```bash
# From the packages directory
docker-compose up -d
```

This will start PostgreSQL on port 5433 with the pgvector extension enabled.

### 2. Start the Backend API

```bash
# Navigate to the API directory
cd api

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/`

### 3. Start the Frontend

```bash
# Navigate to the web directory
cd web

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 📁 Project Structure

```
packages/
├── api/                        # FastAPI Backend
│   ├── routers/               # API route handlers
│   │   ├── trips.py          # Trip & participant endpoints
│   │   ├── itinerary.py      # Itinerary & activity endpoints
│   │   ├── polling.py        # Poll & voting endpoints
│   │   └── expenses.py       # Expense & balance endpoints
│   ├── config.py             # Pydantic settings
│   ├── crud.py               # Database service layer
│   ├── database.py           # SQLAlchemy setup
│   ├── dependencies.py       # FastAPI dependencies
│   ├── main.py               # Application entry point
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic validation schemas
│   ├── .env                  # Environment variables
│   └── requirements.txt      # Python dependencies
│
├── web/                       # React Frontend
│   ├── src/
│   │   ├── api/              # API client & hooks
│   │   │   ├── apiClient.ts  # Axios instance & services
│   │   │   └── hooks.ts      # TanStack Query hooks
│   │   ├── components/ui/    # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   └── input.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── CreateTripPage.tsx
│   │   │   └── TripDashboardPage.tsx
│   │   ├── store/            # Zustand stores
│   │   │   └── uiStore.ts
│   │   ├── types/            # TypeScript types
│   │   │   └── db.ts
│   │   ├── App.tsx           # Routing setup
│   │   ├── main.tsx          # App entry point
│   │   └── index.css         # Tailwind setup
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docker-compose.yml         # PostgreSQL setup
├── .env                       # Root environment variables
└── README.md                  # This file
```

---

## 🔧 Configuration

### Environment Variables

**Backend (api/.env)**:
```env
DATABASE_URL="postgresql+asyncpg://admin:password@localhost:5433/packvote"
```

**Frontend (web/.env)** (optional):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Database Connection
The application uses PostgreSQL on port **5433** (not the default 5432) to avoid conflicts.

---

## 📊 Database Schema

### Core Models
- **Trip**: Main trip entity
- **Participant**: Trip participants
- **ItineraryDay**: Days in the trip
- **Activity**: Activities within days
- **Poll** & **PollOption**: Group decision making
- **Vote**: Poll responses
- **Expense** & **ExpenseSplit**: Expense tracking
- **Recommendation**: AI-powered suggestions (with pgvector embeddings)

All models include:
- UUID primary keys
- Integer timestamps (created_at, updated_at)
- Proper relationships with cascade deletes

---

## 🎨 Frontend Features

### Create Trip Page
- Clean, animated landing page
- Form validation with Zod
- Auto-navigation to trip dashboard on success

### Trip Dashboard Page
- **Participants Section**: Add and view trip participants
- **Itinerary Section**: Create days and add activities with times/locations
- **Polls Section**: Create polls and vote on group decisions
- **Expenses Section**: 
  - Add expenses with automatic split calculation
  - Real-time balance tracking (who owes whom)
- Modal-based forms for all interactions
- Smooth animations with Framer Motion

---

## 🔒 API Endpoints

### Trips & Participants
- `POST /api/v1/trips` - Create a new trip
- `GET /api/v1/{trip_id}` - Get trip with all data
- `POST /api/v1/{trip_id}/participants/` - Add participant

### Itinerary
- `POST /api/v1/itinerary/trips/{trip_id}/days/` - Create itinerary day
- `POST /api/v1/itinerary/days/{day_id}/activities/` - Add activity

### Polling
- `POST /api/v1/trips/{trip_id}/polls/` - Create poll
- `POST /api/v1/polls/options/{option_id}/vote` - Cast vote

### Expenses
- `POST /api/v1/trips/{trip_id}/expenses/` - Add expense
- `GET /api/v1/trips/{trip_id}/expenses/balance/` - Get balances

---

## 🧪 Testing the Application

1. **Create a Trip**:
   - Navigate to `http://localhost:5173`
   - Fill in trip name and optional dates
   - Click "Create Trip"

2. **Add Participants**:
   - Click "+ Add" in the Participants section
   - Enter name and email
   - Submit

3. **Build Itinerary**:
   - Click "+ Add Day" in the Itinerary section
   - Select a date and optional title
   - Click "+ Activity" on any day to add activities

4. **Create Polls**:
   - Click "+ Create Poll"
   - Enter question and at least 2 options
   - Vote on poll options

5. **Track Expenses**:
   - Click "+ Add Expense"
   - Enter expense details
   - Select who paid
   - Expense is automatically split equally among all participants
   - View balances in real-time

---

## 🚨 Troubleshooting

### Database Connection Issues
- Ensure Docker is running: `docker ps`
- Check if PostgreSQL is on port 5433: `docker-compose ps`
- Verify environment variable in `api/.env`

### Backend Not Starting
- Check if port 8000 is available
- Verify Python dependencies are installed: `pip list`
- Check console for detailed error messages

### Frontend Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run build`

### API CORS Issues
- Verify FastAPI CORS middleware allows `http://localhost:5173`
- Check browser console for detailed CORS errors

---

## 📝 Development Notes

### Code Quality
- ✅ **Type Safety**: Full TypeScript coverage on frontend
- ✅ **Validation**: Zod schemas for frontend, Pydantic for backend
- ✅ **Error Handling**: Proper HTTP status codes and user-friendly messages
- ✅ **Performance**: Eager loading to prevent N+1 queries
- ✅ **Scalability**: Modular architecture with separation of concerns

### Best Practices Implemented
- Single Responsibility Principle (SRP)
- Don't Repeat Yourself (DRY)
- Proper separation between UI state (Zustand) and server state (TanStack Query)
- Form validation at both client and server levels
- Optimistic UI updates with proper invalidation

---

## 🎯 Future Enhancements

- [ ] User authentication (JWT tokens)
- [ ] Real-time updates with WebSockets
- [ ] AI-powered destination recommendations (using pgvector)
- [ ] File uploads for itinerary items
- [ ] Export trip details to PDF
- [ ] Mobile responsive improvements
- [ ] Dark mode
- [ ] Multi-currency support
- [ ] Settlement suggestions ("who should pay whom")

---

## 👨‍💻 Tech Stack Summary

**Frontend**: React + Vite + TypeScript + Tailwind + TanStack Query + Zustand + React Hook Form + Zod + Framer Motion

**Backend**: FastAPI + SQLAlchemy + Pydantic + PostgreSQL + pgvector + Uvicorn

**Infrastructure**: Docker + Docker Compose

---

## 📄 License

This is a demo project for educational purposes.

---

## 🙏 Acknowledgments

Built following enterprise-grade best practices with a focus on:
- Clean Architecture
- Type Safety
- Performance Optimization
- Developer Experience
- User Experience

---

**Happy Trip Planning! 🌍✈️**
