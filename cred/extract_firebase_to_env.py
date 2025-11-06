#!/usr/bin/env python3
"""
Helper script to extract credentials from existing JSON files and generate .env entries.
This helps migrate from JSON files to environment variables.
"""
import json
import os


def extract_firebase_credentials():
    """Extract credentials from firebase-credentials.json and print as .env entries."""
    try:
        with open('firebase-credentials.json', 'r') as f:
            data = json.load(f)
        
        print("\n# Firebase Service Account Credentials (firebase-credentials.json)")
        print(f'FIREBASE_TYPE={data.get("type", "service_account")}')
        print(f'FIREBASE_PROJECT_ID={data.get("project_id", "")}')
        print(f'FIREBASE_PRIVATE_KEY_ID={data.get("private_key_id", "")}')
        
        # Handle private key - needs to be quoted and newlines escaped
        private_key = data.get("private_key", "").replace("\n", "\\n")
        print(f'FIREBASE_PRIVATE_KEY="{private_key}"')
        
        print(f'FIREBASE_CLIENT_EMAIL={data.get("client_email", "")}')
        print(f'FIREBASE_CLIENT_ID={data.get("client_id", "")}')
        print(f'FIREBASE_AUTH_URI={data.get("auth_uri", "https://accounts.google.com/o/oauth2/auth")}')
        print(f'FIREBASE_TOKEN_URI={data.get("token_uri", "https://oauth2.googleapis.com/token")}')
        print(f'FIREBASE_AUTH_PROVIDER_X509_CERT_URL={data.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs")}')
        print(f'FIREBASE_CLIENT_X509_CERT_URL={data.get("client_x509_cert_url", "")}')
        print(f'FIREBASE_UNIVERSE_DOMAIN={data.get("universe_domain", "googleapis.com")}')
        
        return True
    except FileNotFoundError:
        print("\n✗ firebase-credentials.json not found")
        return False
    except Exception as e:
        print(f"\n✗ Error reading firebase-credentials.json: {e}")
        return False


def extract_google_services():
    """Extract credentials from google-services.json and print as .env entries."""
    try:
        with open('google-services.json', 'r') as f:
            data = json.load(f)
        
        print("\n# Google Services Configuration (google-services.json)")
        
        project_info = data.get("project_info", {})
        print(f'GOOGLE_SERVICES_PROJECT_NUMBER={project_info.get("project_number", "")}')
        print(f'GOOGLE_SERVICES_STORAGE_BUCKET={project_info.get("storage_bucket", "")}')
        
        clients = data.get("client", [])
        if clients:
            client = clients[0]
            client_info = client.get("client_info", {})
            print(f'GOOGLE_SERVICES_MOBILESDK_APP_ID={client_info.get("mobilesdk_app_id", "")}')
            
            android_info = client_info.get("android_client_info", {})
            print(f'GOOGLE_SERVICES_ANDROID_PACKAGE_NAME={android_info.get("package_name", "")}')
            
            api_keys = client.get("api_key", [])
            if api_keys:
                print(f'GOOGLE_SERVICES_API_KEY={api_keys[0].get("current_key", "")}')
        
        return True
    except FileNotFoundError:
        print("\n✗ google-services.json not found")
        return False
    except Exception as e:
        print(f"\n✗ Error reading google-services.json: {e}")
        return False


def main():
    print("=" * 70)
    print("Firebase Credentials Extractor")
    print("=" * 70)
    print("\nThis script extracts credentials from your JSON files and")
    print("generates environment variable entries for your .env file.")
    print("\nCopy the output below and paste it into your .env file:")
    print("=" * 70)
    
    firebase_ok = extract_firebase_credentials()
    google_ok = extract_google_services()
    
    print("\n" + "=" * 70)
    
    if firebase_ok or google_ok:
        print("\n✓ Extraction complete!")
        print("\nNext steps:")
        print("1. Copy the lines above")
        print("2. Paste them into your .env file")
        print("3. Run: python generate_firebase_config.py")
        print("4. Verify the generated JSON files match your originals")
    else:
        print("\n✗ No JSON files found to extract")
        print("\nMake sure you have:")
        print("  - firebase-credentials.json")
        print("  - google-services.json")
        print("\nin the current directory.")


if __name__ == "__main__":
    main()
