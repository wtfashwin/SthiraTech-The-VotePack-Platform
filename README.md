# VotePack - Group Travel Made Simple

Hey there! 👋 Welcome to VotePack, a travel planning app I built to solve a real problem: coordinating group trips without losing your mind.

You know how it goes - trying to plan a trip with friends means endless group chats about where to eat, what to do, and who owes who money. VotePack brings all of that chaos into one place where everyone can actually collaborate.

## What Does It Do?

This isn't just another trip planner. Here's what makes it different:

- **Trip Planning**: Create trips, invite your friends, and keep everyone on the same page
- **Smart Itinerary**: Build your schedule day-by-day with actual times and locations
- **Group Voting**: Can't decide between tacos or pizza? Let the group vote
- **Expense Tracking**: Track who paid for what and see who owes who (no more awkward money conversations)
- **AI Suggestions**: Get smart recommendations for activities based on what your group likes
- **Payment Integration**: Actually settle up using Stripe (because Venmo requests get ignored)

## The Tech Stack

I went with modern, reliable tools that just work:

**Frontend:**
- React with TypeScript (because I like catching bugs before they happen)
- Vite for lightning-fast dev experience
- Tailwind CSS (utility classes for the win)
- TanStack Query for server state - it handles caching so you're not hammering the API
- Zustand for UI state - lightweight and simple
- React Hook Form + Zod for solid form validation
- Framer Motion for smooth animations

**Backend:**
- FastAPI - seriously fast Python framework with auto-generated docs
- SQLAlchemy 2.0 for talking to the database
- Pydantic for data validation (FastAPI and Pydantic are best friends)
- JWT tokens for auth
- Stripe SDK for payments
- Google Gemini for AI features

**Database:**
- PostgreSQL with pgvector extension (for AI embeddings)
- Supabase hosting (free tier is generous and works great)

## Getting Started

### What You'll Need

- Node.js 18 or newer
- Python 3.10 or newer
- A Supabase account (free tier works fine)
- Stripe account for payments (test mode is free)
- Google Gemini API key (also free tier)

### Step 1: Clone and Set Up

```bash
# Clone the repo
<<<<<<< HEAD
git clone https://github.com/wtfashwin/thiraTech-The-VotePack-Platform.git
=======
git clone <your-repo-url>
>>>>>>> 2a2459c24f9c2e8fd51ec645fc397e6525bf6601
cd VotePack
```

### Step 2: Database Setup (Supabase)

This is actually easier than running PostgreSQL locally:

1. Head to [supabase.com](https://supabase.com) and create an account
2. Create a new project (pick a region close to you)
3. Wait a minute for it to spin up (grab some coffee ☕)
4. Go to the SQL Editor and run this:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. Grab your connection string from Settings → Database → Connection String (URI)
   - It'll look like: `postgresql://postgres:[password]@[host]:5432/postgres`

Pro tip: Supabase gives you a nice dashboard to browse your data, which beats the heck out of command-line PostgreSQL.

### Step 3: Backend Setup

```bash
cd packages/api

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Now create a `.env` file in the `packages/api` folder:

```env
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SECRET_KEY=make-this-at-least-32-characters-long-and-random
GEMINI_API_KEY=your-gemini-api-key
STRIPE_SECRET_KEY=sk_test_your-stripe-test-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
FRONTEND_URL=http://localhost:5173
```

**Important:** 
- Replace the DATABASE_URL with your actual Supabase connection string
- The SECRET_KEY should be random - mash your keyboard for a bit
- Get your Gemini key from [ai.google.dev](https://ai.google.dev/)
- Stripe keys come from your Stripe Dashboard → Developers → API keys

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

You should see something like "Uvicorn running on http://127.0.0.1:8000". If you visit that URL, you'll get a simple health check. The real magic is at `http://localhost:8000/docs` - FastAPI auto-generates beautiful API documentation.

### Step 4: Frontend Setup

```bash
cd packages/web

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Visit `http://localhost:5173` and you should see VotePack running! 🎉

## How It Works

### The Database Magic

The app uses SQLAlchemy ORM, which means no raw SQL queries (unless you want to). All the tables get created automatically when the backend starts.

Here's what's happening under the hood:
- **Trips** have many **Participants**
- Each trip has **Itinerary Days**, which have **Activities**
- **Polls** let people vote on decisions
- **Expenses** get split between participants automatically
- **Recommendations** use AI embeddings (that's where pgvector comes in)

The cool part? When you delete a trip, all the related data gets cleaned up automatically thanks to cascade deletes.

### Supabase Connection Details

I set it up so the pgvector extension gets created automatically on first connection (check `database.py`). The connection uses psycopg2-binary driver - I tried asyncpg first but ran into some issues, so I went with what works.

If you're having connection issues (especially from Render or other hosts), the app forces IPv4 connections. See `scripts/start_uvicorn.sh` for the workaround.

## Project Structure

```
VotePack/
├── packages/
│   ├── api/                    # FastAPI backend
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py        # Login/register
│   │   │   ├── trips.py       # Trip management
│   │   │   ├── itinerary.py   # Schedule stuff
│   │   │   ├── polling.py     # Group voting
│   │   │   ├── expenses.py    # Money tracking
│   │   │   ├── payments.py    # Stripe integration
│   │   │   └── ai.py          # AI features
│   │   ├── main.py            # App entry point
│   │   ├── database.py        # DB connection
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # API request/response schemas
│   │   ├── crud.py            # Database operations
│   │   ├── auth.py            # JWT handling
│   │   └── config.py          # Settings
│   │
│   └── web/                   # React frontend
│       ├── src/
│       │   ├── api/          # API client & React Query hooks
│       │   ├── components/   # Reusable UI components
│       │   ├── pages/        # Main pages
│       │   ├── store/        # Zustand state management
│       │   └── types/        # TypeScript definitions
│       └── package.json
│
└── scripts/                   # Deployment scripts
```

## API Endpoints (The Important Ones)

All endpoints start with `/api/v1`:

**Auth:**
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token

**Trips:**
- `POST /trips/` - Create a trip
- `GET /trips/{id}` - Get trip details (includes everything)
- `POST /trips/{id}/participants/` - Add people

**Itinerary:**
- `POST /itinerary/trips/{id}/days/` - Add a day to the itinerary
- `POST /itinerary/days/{day_id}/activities/` - Add activity to a day

**Polls:**
- `POST /trips/{id}/polls/` - Create a poll
- `POST /polls/options/{id}/vote` - Cast your vote

**Expenses:**
- `POST /trips/{id}/expenses/` - Log an expense
- `GET /trips/{id}/expenses/balance/` - See who owes who

**Payments:**
- `POST /payments/create-intent` - Start a Stripe payment
- `POST /payments/stripe/webhook` - Stripe calls this (not you)

**AI:**
- `POST /ai/recommendations` - Get AI suggestions
- `POST /ai/consensus` - Analyze group preferences

Visit `/docs` when the backend is running to try these out interactively!

## Features Breakdown

### Authentication
Uses JWT tokens. When you log in, you get a token that you send with every request. The frontend handles this automatically using Axios interceptors.

Passwords are hashed with SHA-256 (I know, SHA-512 would be better, but this works for now).

### Group Voting
Create a poll, add options, and let people vote. The backend tracks votes and prevents duplicate voting. Simple but effective.

### Expense Tracking
Here's the thing I'm most proud of: expenses get split automatically based on who's in the trip. You can see balances in real-time - no more "I think you owe me $47.32" conversations.

The algorithm figures out the optimal way to settle up (who should pay who to minimize transactions).

### AI Recommendations
This is where pgvector shines. The app stores embeddings of destinations and activities, then uses vector similarity search to find relevant suggestions.

It also has a "consensus" feature that analyzes what the whole group wants and suggests activities that'll make everyone happy.

### Stripe Payments
Instead of manually settling up later, people can actually pay through the app. Uses Stripe's payment intents API - it's secure and handles all the payment stuff for you.

Set up webhooks in Stripe dashboard to notify the app when payments succeed or fail.

## Troubleshooting

**"Can't connect to database"**
- Double-check your Supabase connection string
- Make sure you didn't include extra quotes in the .env file
- Check if you can connect using a tool like pgAdmin or DBeaver

**"Port 8000 already in use"**
- Something else is using that port. Either kill it or change the port in the uvicorn command

**"Module not found" errors**
- Backend: Run `pip install -r requirements.txt` again
- Frontend: Delete `node_modules` and run `npm install`

**"CORS errors in browser"**
- Check that `FRONTEND_URL` in your backend .env matches where your frontend is running
- The backend CORS settings allow localhost:5173 by default

**"AI features aren't working"**
- Verify your Gemini API key is correct
- Check if you've hit the free tier rate limit (it's pretty generous though)

**"Stripe webhooks failing"**
- In development, use Stripe CLI to forward webhooks: `stripe listen --forward-to localhost:8000/api/v1/payments/stripe/webhook`
- Make sure your webhook secret matches

## Deployment

I've deployed this on:
- **Backend**: Render.com (free tier works, but it sleeps after inactivity)
- **Frontend**: Vercel (automatic deploys from git, super easy)
- **Database**: Supabase (already set up!)

**Environment Variables to Set:**
- Backend needs: `DATABASE_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `FRONTEND_URL`
- Frontend needs: `VITE_API_BASE_URL` (your backend URL)

**Gotcha:** Render's free tier has a cold start delay. First request after inactivity takes ~30 seconds. Paid tier fixes this.

## Things I'd Add Next

- [ ] Real-time updates with WebSockets (so you see votes come in live)
- [ ] Mobile app (React Native maybe?)
- [ ] Photo uploads for itinerary items
- [ ] Export trip to PDF
- [ ] Multi-currency support (right now it's USD only)
- [ ] Dark mode (because everyone asks for it)
- [ ] Email notifications for votes and expenses
- [ ] Group chat (might be overkill though)

## Final Thoughts

I built this because I was tired of juggling 5 different apps to plan one trip. Is it perfect? Nope. But it works, and it actually solves the problem.

The code is structured to be maintainable - I tried to follow clean architecture principles without going overboard. If something seems weird, it's probably because I learned it the hard way.

Feel free to use this, modify it, or just poke around the code. If you find bugs (you will), well, that's what GitHub issues are for.

Happy travels! ✈️

---

**License:** Do whatever you want with it

**Questions?** Check the code comments - I tried to explain the weird parts
