# Next Steps - FCM Push Notifications Setup

## ✅ What's Already Done

The complete push notification system has been implemented with:
- FCM service for sending notifications
- Background scheduler for checking reminders
- User token management endpoints
- Database schema updates
- Docker configuration
- Comprehensive documentation

## 🔧 What You Need to Do

### 1. Place Firebase Credentials File

**Action Required:** 
- Locate the Firebase service account JSON file you mentioned
- Rename it to `google-services.json`
- Place it in the project root: `d:\obaid\mindful\google-services.json`

**File Structure Should Look Like:**
```
d:\obaid\mindful\
├── google-services.json  ← PLACE YOUR FILE HERE
├── docker-compose.yml
├── requirements.txt
├── app/
└── ...
```

**Note:** This file is already in `.gitignore` so it won't be committed to git.

### 2. Run Database Migration

Since your app is running in Docker, you need to create and apply the migration for the new `fcm_token` field.

**Option A: Use the PowerShell Script (Recommended)**
```powershell
# From the project root directory
.\run_fcm_migration.ps1
```

**Option B: Run Manually**
```powershell
# Stop containers
docker-compose down

# Rebuild with new dependencies
docker-compose build

# Start containers
docker-compose up -d

# Create migration
docker-compose exec api alembic revision --autogenerate -m "add_fcm_token_to_users"

# Apply migration
docker-compose exec api alembic upgrade head
```

### 3. Verify Setup

**Check the logs to ensure everything started correctly:**
```powershell
docker-compose logs -f api
```

**Look for these success messages:**
```
INFO:app.services.reminder_scheduler_service:Reminder scheduler service started successfully
INFO:app.services.fcm_service:Firebase Admin SDK initialized successfully
```

### 4. Test the System

#### A. Check Notification Status
```bash
curl http://localhost:8000/notifications/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Expected response:
```json
{
  "fcm_initialized": true,
  "scheduler_running": true,
  "user_has_token": false,
  "message": "No FCM token registered for this user"
}
```

#### B. Register FCM Token (from mobile app)
```bash
curl -X POST http://localhost:8000/user/fcm-token \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fcm_token": "YOUR_DEVICE_FCM_TOKEN"}'
```

#### C. Send Test Notification
```bash
curl -X POST http://localhost:8000/notifications/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "message": "Testing push notifications!"}'
```

#### D. Create Test Reminder
```bash
# Calculate a time 2 minutes from now in UTC
curl -X POST http://localhost:8000/reminders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reminder_type": "custom",
    "title": "Test Reminder",
    "message": "This is a test push notification!",
    "trigger_time": "2025-11-05T15:30:00Z",
    "frequency": "one-time"
  }'
```

## 📱 Mobile App Integration

Your mobile developers need to:

### 1. Add Firebase SDK

**Android (build.gradle):**
```groovy
dependencies {
    implementation 'com.google.firebase:firebase-messaging:23.3.1'
}
```

**iOS (Podfile):**
```ruby
pod 'Firebase/Messaging'
```

### 2. Request Notification Permissions

The app needs to request permission from users to send notifications.

### 3. Get and Send FCM Token

**Flutter Example:**
```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> registerFCMToken() async {
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  
  // Request permission
  NotificationSettings settings = await messaging.requestPermission();
  
  if (settings.authorizationStatus == AuthorizationStatus.authorized) {
    // Get token
    String? token = await messaging.getToken();
    
    if (token != null) {
      // Send to backend
      final response = await http.post(
        Uri.parse('https://your-api.com/user/fcm-token'),
        headers: {
          'Authorization': 'Bearer $jwtToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({'fcm_token': token}),
      );
      
      if (response.statusCode == 200) {
        print('FCM token registered successfully');
      }
    }
  }
}

// Listen for token refresh
void setupTokenRefreshListener() {
  FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
    // Re-register with backend
    registerFCMToken();
  });
}
```

### 4. Handle Incoming Notifications

The app needs to handle notifications when they arrive.

### 5. Remove Token on Logout

```dart
Future<void> logout() async {
  // Remove FCM token from backend
  await http.delete(
    Uri.parse('https://your-api.com/user/fcm-token'),
    headers: {
      'Authorization': 'Bearer $jwtToken',
    },
  );
  
  // Perform logout
  // ...
}
```

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `FCM_QUICK_START.md` | Quick start guide for setup |
| `PUSH_NOTIFICATIONS_SETUP.md` | Detailed setup and architecture |
| `IMPLEMENTATION_SUMMARY.md` | Complete technical summary |
| `NEXT_STEPS.md` | This file - what to do next |

## 🐛 Troubleshooting

### Issue: "Firebase credentials file not found"

**Solution:**
1. Check file is named exactly `google-services.json`
2. Check file is in project root `d:\obaid\mindful\`
3. Restart Docker containers: `docker-compose restart api`

### Issue: "Scheduler not starting"

**Solution:**
1. Check logs: `docker-compose logs api | Select-String "error"`
2. Verify migration completed: `docker-compose exec api alembic current`
3. Rebuild containers: `docker-compose down && docker-compose build && docker-compose up -d`

### Issue: "Notifications not received"

**Checklist:**
- [ ] Firebase credentials file in place
- [ ] Migration completed (fcm_token field exists)
- [ ] Scheduler is running (check logs)
- [ ] FCM token registered for user
- [ ] Reminder trigger_time is within last 2 minutes
- [ ] User is_active = true
- [ ] Mobile app has notification permissions

## 🎯 Success Criteria

You'll know everything is working when:

1. ✅ Docker containers start without errors
2. ✅ Logs show "Reminder scheduler service started successfully"
3. ✅ Logs show "Firebase Admin SDK initialized successfully"
4. ✅ `/notifications/status` returns all `true` values
5. ✅ Test notification is received on mobile device
6. ✅ Reminder notifications arrive at scheduled time

## 📞 Need Help?

If you encounter issues:

1. **Check logs first:**
   ```powershell
   docker-compose logs -f api
   ```

2. **Verify database:**
   ```powershell
   docker-compose exec api alembic current
   docker-compose exec db psql -U mindful_user -d mindful_db -c "\d users"
   ```
   Should show `fcm_token` column.

3. **Test FCM initialization:**
   ```powershell
   docker-compose exec api python -c "from app.services.fcm_service import FCMService; FCMService.initialize(); print('FCM initialized:', FCMService._initialized)"
   ```

## 🚀 Ready to Start?

**Quick Checklist:**
- [ ] Firebase credentials file placed
- [ ] Docker containers rebuilt
- [ ] Database migration completed
- [ ] Logs checked for errors
- [ ] Status endpoint returns healthy
- [ ] Test notification sent successfully
- [ ] Mobile app integration started

**Minimum Steps to Get Running:**
```powershell
# 1. Place google-services.json in project root

# 2. Run migration
.\run_fcm_migration.ps1

# 3. Check logs
docker-compose logs -f api

# 4. Test (from mobile app or curl)
# Register FCM token and create a reminder
```

That's it! The system is ready to send push notifications for reminders. 🎉
