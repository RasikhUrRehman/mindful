# How to Get Firebase Admin SDK Credentials

## Important: You Have the Wrong File

The `google-services.json` file you have is for **Android client apps**, not for backend server authentication.

For backend push notifications, you need the **Firebase Admin SDK Service Account** credentials.

## Steps to Get the Correct File:

### 1. Go to Firebase Console
Visit: https://console.firebase.google.com/

### 2. Select Your Project
- Project: **mindful-dfeab** (from your google-services.json)

### 3. Navigate to Project Settings
1. Click the gear icon ⚙️ next to "Project Overview"
2. Select "Project settings"

### 4. Go to Service Accounts Tab
1. Click on "Service accounts" tab
2. You should see "Firebase Admin SDK"

### 5. Generate New Private Key
1. Scroll down to "Firebase Admin SDK" section
2. Click "Generate new private key"
3. Click "Generate key" in the confirmation dialog
4. A JSON file will download automatically

### 6. Rename and Place the File
1. Rename the downloaded file to: `firebase-credentials.json`
2. Place it in: `d:\obaid\mindful\firebase-credentials.json`

## What the Correct File Looks Like:

```json
{
  "type": "service_account",
  "project_id": "mindful-dfeab",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@mindful-dfeab.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Key differences:**
- Has `"type": "service_account"` field
- Has `private_key` field with actual key
- Has `client_email` for service account

## Quick Link:
https://console.firebase.google.com/project/mindful-dfeab/settings/serviceaccounts/adminsdk

## After You Get the File:

1. Place it as `d:\obaid\mindful\firebase-credentials.json`
2. Restart the container:
   ```powershell
   docker-compose restart api
   ```
3. Check logs:
   ```powershell
   docker-compose logs --tail=20 api
   ```

You should see: "Firebase Admin SDK initialized successfully"
