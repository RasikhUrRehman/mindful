# FCM Push Notifications - Quick Start

## Step-by-Step Setup

### 1. Prepare Firebase Credentials
- Place your Firebase service account JSON file (downloaded from Firebase Console) in the project root
- Rename it to `google-services.json`

### 2. Stop Current Containers (if running)
```powershell
docker-compose down
```

### 3. Rebuild Containers with New Dependencies
```powershell
docker-compose build
```

### 4. Start Containers
```powershell
docker-compose up -d
```

### 5. Run Database Migration
```powershell
# Option 1: Use the provided script
.\run_fcm_migration.ps1

# Option 2: Run manually
docker-compose exec api alembic revision --autogenerate -m "add_fcm_token_to_users"
docker-compose exec api alembic upgrade head
```

### 6. Verify Setup
Check the logs to ensure the scheduler started:
```powershell
docker-compose logs -f api
```

You should see:
```
INFO:app.services.reminder_scheduler_service:Reminder scheduler service started successfully
```

### 7. Test the Setup

#### A. Register an FCM Token
```bash
curl -X POST http://localhost:8000/user/fcm-token \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fcm_token": "YOUR_DEVICE_FCM_TOKEN"}'
```

#### B. Create a Test Reminder (trigger in 2 minutes)
```bash
curl -X POST http://localhost:8000/reminders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reminder_type": "custom",
    "title": "Test Notification",
    "message": "This is a test push notification!",
    "trigger_time": "2025-11-05T15:02:00Z",
    "frequency": "one-time"
  }'
```

**Note**: Replace `2025-11-05T15:02:00Z` with a time 2 minutes from now in UTC format.

#### C. Wait and Check
- Wait for the trigger time
- Your mobile device should receive the push notification
- Check logs: `docker-compose logs -f api | Select-String "notification"`

## What's Been Added?

### New Files
- `app/services/fcm_service.py` - FCM notification sending service
- `app/services/reminder_scheduler_service.py` - Background scheduler for reminders
- `PUSH_NOTIFICATIONS_SETUP.md` - Detailed documentation
- `run_fcm_migration.ps1` - Migration script for Windows
- `google-services.json.example` - Example credentials file

### Modified Files
- `app/models/user.py` - Added `fcm_token` field
- `app/schemas/user_schema.py` - Added FCM token schemas
- `app/routes/user_routes.py` - Added FCM token endpoints
- `app/main.py` - Added scheduler lifecycle management
- `app/core/config.py` - Added Firebase configuration
- `requirements.txt` - Added `firebase-admin` package
- `docker-compose.yml` - Added Firebase environment variable
- `.gitignore` - Added Firebase credentials to ignore list

### New API Endpoints
1. `POST /user/fcm-token` - Register/update FCM token
2. `DELETE /user/fcm-token` - Remove FCM token

### How It Works
1. **Background Scheduler**: Runs every minute checking for due reminders
2. **Notification Sending**: Automatically sends push notifications via FCM
3. **Recurring Support**: Handles daily, weekly, monthly, hourly reminders
4. **Status Tracking**: Updates reminder status after sending

## Mobile App Integration Checklist

- [ ] Add Firebase SDK to your mobile app
- [ ] Request notification permissions
- [ ] Get FCM token from Firebase
- [ ] Send token to backend (`POST /user/fcm-token`)
- [ ] Handle token refresh
- [ ] Handle incoming notifications
- [ ] Remove token on logout (`DELETE /user/fcm-token`)

## Troubleshooting

### "Firebase credentials file not found"
- Ensure `google-services.json` is in the project root
- Check file permissions
- Verify Docker volume mounting

### "Scheduler not starting"
- Check application logs: `docker-compose logs api`
- Ensure APScheduler is installed (in requirements.txt)

### "No notifications received"
- Verify FCM token is registered (check database)
- Ensure reminder trigger_time is in the past (within last 2 minutes)
- Check user.is_active is true
- Verify mobile app has notification permissions

## Support

For detailed documentation, see `PUSH_NOTIFICATIONS_SETUP.md`
