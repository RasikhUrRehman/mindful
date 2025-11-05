# Push Notifications Setup Guide

This guide explains how to set up push notifications using Firebase Cloud Messaging (FCM) for the Mindful Progress app.

## Prerequisites

1. Firebase project with FCM enabled
2. Firebase service account credentials JSON file
3. Docker and Docker Compose installed

## Setup Steps

### 1. Place Firebase Credentials

Place your Firebase service account JSON file (the one you downloaded from Firebase) in the project root directory and name it `google-services.json`.

```
mindful/
├── google-services.json  # <-- Place your file here
├── docker-compose.yml
├── requirements.txt
└── ...
```

Alternatively, you can place it anywhere and set the `FIREBASE_CREDENTIALS_PATH` environment variable to point to it.

### 2. Update Environment Variables

Add the following to your `.env` file:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=google-services.json
```

### 3. Update Docker Compose

The `docker-compose.yml` has been configured to mount the credentials file into the container. Make sure the following is in your `docker-compose.yml`:

```yaml
api:
  environment:
    FIREBASE_CREDENTIALS_PATH: /app/google-services.json
  volumes:
    - .:/app
```

### 4. Create Database Migration

Run the Alembic migration to add the `fcm_token` field to the users table:

```bash
# If using Docker:
docker-compose exec api alembic revision --autogenerate -m "add_fcm_token_to_users"
docker-compose exec api alembic upgrade head

# If running locally:
alembic revision --autogenerate -m "add_fcm_token_to_users"
alembic upgrade head
```

### 5. Install Dependencies

The required package `firebase-admin` has been added to `requirements.txt`. Rebuild your Docker container:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## How It Works

### Architecture

1. **FCM Service** (`app/services/fcm_service.py`): Handles sending push notifications via Firebase
2. **Reminder Scheduler Service** (`app/services/reminder_scheduler_service.py`): Background service that checks for due reminders every minute and sends notifications
3. **User Model**: Now includes `fcm_token` field to store device tokens
4. **User Routes**: New endpoints for registering/unregistering FCM tokens

### Workflow

1. **User Registration**: Mobile app registers and gets an FCM token from Firebase
2. **Token Storage**: App sends FCM token to backend via `POST /user/fcm-token`
3. **Reminder Creation**: User creates reminders via existing reminder endpoints
4. **Background Processing**: 
   - Scheduler runs every minute
   - Queries for due reminders
   - Sends push notifications to users with valid FCM tokens
   - Updates reminder status based on frequency (one-time, recurring)
5. **Token Cleanup**: App can remove FCM token via `DELETE /user/fcm-token` (e.g., on logout)

### Reminder Status Flow

- **pending**: Reminder is waiting to be triggered
- **triggered**: Notification sent successfully (for recurring reminders)
- **completed**: Notification sent successfully (for one-time reminders)
- **failed**: Failed to send notification
- **cancelled**: User has no FCM token

### Recurring Reminders

The scheduler automatically handles recurring reminders:
- **daily**: Reschedules +1 day
- **weekly**: Reschedules +7 days
- **monthly**: Reschedules +30 days
- **hourly**: Reschedules +1 hour
- **one-time**: Marks as completed after sending

## API Endpoints

### Register FCM Token
```http
POST /user/fcm-token
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "fcm_token": "device_fcm_token_here"
}
```

Response:
```json
{
  "success": true,
  "message": "FCM token registered successfully"
}
```

### Unregister FCM Token
```http
DELETE /user/fcm-token
Authorization: Bearer <jwt_token>
```

Response:
```json
{
  "success": true,
  "message": "FCM token unregistered successfully"
}
```

## Mobile App Integration

### Android (Flutter Example)

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// Get FCM token
Future<void> registerFCMToken() async {
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  
  // Request permission
  await messaging.requestPermission();
  
  // Get token
  String? token = await messaging.getToken();
  
  if (token != null) {
    // Send to backend
    await http.post(
      Uri.parse('https://your-api.com/user/fcm-token'),
      headers: {
        'Authorization': 'Bearer $jwtToken',
        'Content-Type': 'application/json',
      },
      body: json.encode({'fcm_token': token}),
    );
  }
}

// Handle token refresh
FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
  // Send updated token to backend
  registerFCMToken();
});
```

### iOS

Make sure to:
1. Add Firebase configuration file (GoogleService-Info.plist)
2. Enable push notifications in Xcode capabilities
3. Configure APNs authentication key in Firebase console

## Testing

### 1. Check Scheduler Status

The scheduler automatically starts when the FastAPI app starts. Check logs:

```bash
docker-compose logs -f api
```

You should see:
```
INFO:app.services.reminder_scheduler_service:Reminder scheduler service started successfully
```

### 2. Test Notification Sending

Create a reminder with a trigger time in the near future (1-2 minutes):

```http
POST /reminders
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "reminder_type": "custom",
  "title": "Test Reminder",
  "message": "This is a test notification",
  "trigger_time": "2025-11-05T10:30:00Z",
  "frequency": "one-time"
}
```

Wait for the trigger time and check:
1. Mobile device should receive push notification
2. Backend logs should show notification sent
3. Reminder status should update to "completed"

## Troubleshooting

### Firebase Not Initialized
**Error**: `Firebase credentials file not found`
**Solution**: Ensure `google-services.json` is in the correct location and accessible by the Docker container

### Notifications Not Sending
1. Check FCM token is registered: Query user table for `fcm_token` field
2. Verify scheduler is running: Check application logs
3. Check reminder trigger time is in the past but within last 2 minutes
4. Verify user `is_active` is `true`

### Invalid FCM Token
**Error**: `Failed to send notification`
**Solution**: 
- Token may have expired - user needs to re-register
- Token may be from wrong Firebase project
- Verify Firebase project credentials match

### Scheduler Not Running
1. Check application startup logs
2. Verify APScheduler is installed
3. Check for initialization errors in main.py

## Security Considerations

1. **Credentials Protection**: Never commit `google-services.json` to version control
2. **Token Validation**: FCM tokens are validated by Firebase when sending
3. **User Authorization**: Only authenticated users can register FCM tokens
4. **Token Cleanup**: Remove tokens on logout to prevent unauthorized notifications

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | `google-services.json` |

## Logs and Monitoring

The system logs important events:
- FCM initialization success/failure
- Notification send attempts
- Scheduler job execution
- Token registration/removal

Check logs regularly to monitor notification delivery:
```bash
docker-compose logs -f api | grep -E "(FCM|Reminder|notification)"
```

## Production Considerations

1. **High Availability**: Consider using a distributed scheduler (e.g., Celery with Redis)
2. **Rate Limiting**: Implement rate limits on notification sending
3. **Batch Processing**: For large user bases, process reminders in batches
4. **Monitoring**: Set up alerting for failed notifications
5. **Token Cleanup**: Periodically remove expired/invalid tokens
6. **Timezone Handling**: Consider user timezones for reminder scheduling

## Next Steps

1. Place your `google-services.json` file in the project root
2. Run the database migration
3. Rebuild and restart Docker containers
4. Integrate FCM token registration in your mobile app
5. Test with a reminder
