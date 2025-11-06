# FCM Test Frontend

Simple HTML frontend to test Firebase Cloud Messaging push notifications for the Mindful app.

## Setup Instructions

### 1. Get Your VAPID Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **mindful-dfeab**
3. Go to **Project Settings** (gear icon) → **Cloud Messaging** tab
4. Scroll down to **Web Push certificates**
5. If you don't have one, click **Generate key pair**
6. Copy the **Key pair** value

### 2. Update the VAPID Key

Open `index.html` and replace `YOUR_VAPID_KEY_HERE` on line 223 with your actual VAPID key:

```javascript
const token = await getToken(messaging, {
    vapidKey: 'YOUR_ACTUAL_VAPID_KEY_HERE'
});
```

### 3. Start a Local Web Server

You **cannot** open the HTML file directly in the browser (file://). You need to serve it via HTTP.

#### Option 1: Using Python
```bash
cd test-frontend
python -m http.server 8080
```

#### Option 2: Using Node.js (http-server)
```bash
npm install -g http-server
cd test-frontend
http-server -p 8080
```

#### Option 3: Using VS Code Live Server
1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### 4. Open in Browser

Navigate to: `http://localhost:8080`

### 5. Test the Notifications

1. Click **"Request Notification Permission"** - Allow notifications when prompted
2. Click **"Get FCM Token"** - This will generate your device token
3. Copy the token (click the copy button)
4. Make sure your backend is running on `http://localhost:8000`
5. Click **"Send Test Notification"** to send a test notification to yourself

## Backend Setup

Make sure your backend is running:

```bash
docker-compose up -d
```

The test endpoint should be available at: `http://localhost:8000/notifications/test`

## Testing with cURL

You can also test the notification endpoint directly with cURL:

```bash
curl -X POST http://localhost:8000/notifications/test \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "YOUR_FCM_TOKEN_HERE",
    "title": "Test Notification",
    "body": "This is a test message"
  }'
```

## Troubleshooting

### Service Worker Issues
- Make sure the service worker file (`firebase-messaging-sw.js`) is in the root of your web server
- Check browser console for any service worker registration errors

### CORS Issues
- If you get CORS errors when calling the backend, you may need to add CORS middleware to your FastAPI app

### No Token Generated
- Make sure you've granted notification permission
- Check the browser console for errors
- Verify your VAPID key is correct

### Notifications Not Received
- Check that the backend is running
- Verify the FCM token is correct
- Check backend logs for any errors
- Ensure Firebase credentials are properly configured

## Features

- ✅ Request notification permission
- ✅ Generate FCM registration token
- ✅ Copy token to clipboard
- ✅ Send test notifications via backend API
- ✅ Receive foreground notifications
- ✅ Receive background notifications (via service worker)
- ✅ Customizable notification title and body

## Browser Support

Works best in:
- Chrome/Edge (recommended)
- Firefox
- Safari (with some limitations)

**Note:** Notifications don't work in incognito/private mode in most browsers.
