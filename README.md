# Mindful Progress Backend API

A comprehensive FastAPI backend for the Mindful Progress App with features for habit tracking, mood logging, goal management, and analytics.

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.13.0
- **Authentication**: JWT with Python-Jose
- **Password Hashing**: Passlib + Bcrypt
- **Validation**: Pydantic 2.5.0

## Quick Start

### 1. Setup Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Update `.env` with your PostgreSQL connection:

```
DATABASE_URL=postgresql://user:password@localhost:5432/mindful_db
```

### 4. Configure Firebase (for Push Notifications)

**Important**: Firebase credentials are now stored securely in environment variables.

1. Copy your Firebase credentials to `.env`:
   ```bash
   # If you have existing JSON files, extract them:
   python extract_firebase_to_env.py
   
   # Or manually add to .env (see .env.example)
   ```

2. The application will auto-generate JSON files from environment variables on startup.

For detailed Firebase setup instructions, see [FIREBASE_ENV_SETUP.md](FIREBASE_ENV_SETUP.md).

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start Server

```bash
python -m uvicorn app.main:app --reload
```

### 7. Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Features

### ✅ Authentication
- User registration with email validation
- JWT-based login/logout
- Password hashing with bcrypt
- Token refresh endpoint

### ✅ User Management
- Complete user profiles
- Gender, motivations, language preferences
- Profile picture support

### ✅ Habit Tracking
- Create and manage habits
- Track streaks and success rates
- Habit categories and frequencies
- Mark habits as complete

### ✅ Mood Tracking
- Log mood entries with intensity (1-10)
- Add notes to mood entries
- Weekly/monthly mood summaries
- Mood breakdown analysis

### ✅ Goal Management
- Create and track goals
- Update completion percentage
- Goal types and timeframes
- Mark goals as completed

### ✅ Reminders & Timers
- Create reminders with custom messages
- Timer functionality for meditation, exercise, etc.
- Background task handling
- Notification system

### ✅ Notes
- Create, update, delete notes
- Pin important notes
- Sort and filter notes

### ✅ Analytics & Insights
- Overall progress score
- Mood analysis and trends
- Habit completion rates
- Goal progress tracking
- Personalized insights

## API Endpoints

### Authentication
```
POST   /auth/signup
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh-token
```

### Habits
```
POST   /habits
GET    /habits
GET    /habits/{id}
PUT    /habits/{id}
DELETE /habits/{id}
POST   /habits/{id}/complete
```

### Moods
```
POST   /moods
GET    /moods
GET    /moods/{id}
PUT    /moods/{id}
DELETE /moods/{id}
GET    /moods/summary/weekly
```

### Goals
```
POST   /goals
GET    /goals
GET    /goals/{id}
PUT    /goals/{id}
DELETE /goals/{id}
POST   /goals/{id}/update-progress
```

### Reminders
```
POST   /reminders
GET    /reminders
GET    /reminders/{id}
PUT    /reminders/{id}
DELETE /reminders/{id}
POST   /reminders/timer/start
GET    /reminders/pending
POST   /reminders/{id}/complete
```

### Notes
```
POST   /notes
GET    /notes
GET    /notes/{id}
PUT    /notes/{id}
DELETE /notes/{id}
POST   /notes/{id}/pin
POST   /notes/{id}/unpin
```

### Analytics
```
GET    /analytics/progress/summary
GET    /analytics/mood/summary
GET    /analytics/habits/stats
POST   /analytics/save-summary
```

### User
```
GET    /user/profile
PUT    /user/profile
GET    /user/profile/{user_id}
```

## Database Models

### Users
- Basic authentication and profile info
- One-to-many relationships with habits, moods, goals, notes, reminders, analytics

### Habits
- Habit tracking with streaks
- Success rate calculation
- Frequency and category support

### Moods
- Mood type and intensity
- Notes and timestamps
- Used for analytics and insights

### Goals
- Goal type and timeframe
- Completion percentage tracking
- Completion status

### Notes
- Title and content
- Pin functionality
- Timestamps

### Reminders
- Reminder type and message
- Trigger time and frequency
- Status tracking (pending, triggered, completed)

### Analytics
- Overall score calculation
- Mood, habit, and goal metrics
- Period-based analysis
- Insights generation

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mindful_db

# JWT Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=True

# App Configuration
APP_NAME=Mindful Progress API
APP_VERSION=1.0.0
```

## Database Schema

See `alembic/versions/001_initial.py` for complete schema definition.

Initial migration creates:
- `users` table
- `habits` table
- `moods` table
- `goals` table
- `notes` table
- `reminders` table
- `analytics` table

All with proper foreign key relationships and constraints.

## Authentication Flow

1. User signs up with email and password
2. Password hashed with bcrypt
3. User logs in with credentials
4. Server returns JWT token
5. Client includes token in Authorization header
6. Server validates token on each request
7. User can refresh token before expiration

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black app/
```

### Lint Code
```bash
pylint app/
```

### Type Check
```bash
mypy app/
```

## Production Deployment

1. Set `DEBUG=False`
2. Generate strong `SECRET_KEY`
3. Configure PostgreSQL with backups
4. Use production ASGI server (Gunicorn)
5. Set up proper logging
6. Configure CORS properly
7. Use HTTPS
8. Set up monitoring and alerts

Example production run:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## Docker

You can run the application using Docker and Docker Compose. This repository includes a `Dockerfile` and `docker-compose.yml` for a quick local setup.

Build and start the services (rebuild images if needed):

```powershell
docker-compose up --build -d
```

After the containers start, the API will be available at http://localhost:8000 (unless overridden in `docker-compose.yml`). Use the logs to inspect service output:

```powershell
docker-compose logs -f
```

To stop and remove containers, networks and volumes created by Compose:

```powershell
docker-compose down
```

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

MIT

## Support

For issues or questions, please refer to the SETUP.md file or create an issue in the repository.
