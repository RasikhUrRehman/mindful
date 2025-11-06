"""
Utility to generate Firebase JSON configuration files from environment variables.
This provides better security by keeping credentials in environment variables.
"""
import os
import json
from pathlib import Path


def generate_firebase_credentials_json() -> dict:
    """
    Generate firebase-credentials.json content from environment variables.
    
    Returns:
        dict: Firebase credentials configuration
    """
    return {
        "type": os.getenv("FIREBASE_TYPE", "service_account"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": os.getenv(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
            "https://www.googleapis.com/oauth2/v1/certs"
        ),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", ""),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
    }


def generate_google_services_json() -> dict:
    """
    Generate google-services.json content from environment variables.
    
    Returns:
        dict: Google services configuration
    """
    project_id = os.getenv("FIREBASE_PROJECT_ID", "")
    project_number = os.getenv("GOOGLE_SERVICES_PROJECT_NUMBER", "")
    
    return {
        "project_info": {
            "project_number": project_number,
            "project_id": project_id,
            "storage_bucket": os.getenv("GOOGLE_SERVICES_STORAGE_BUCKET", "")
        },
        "client": [
            {
                "client_info": {
                    "mobilesdk_app_id": os.getenv("GOOGLE_SERVICES_MOBILESDK_APP_ID", ""),
                    "android_client_info": {
                        "package_name": os.getenv("GOOGLE_SERVICES_ANDROID_PACKAGE_NAME", "")
                    }
                },
                "oauth_client": [],
                "api_key": [
                    {
                        "current_key": os.getenv("GOOGLE_SERVICES_API_KEY", "")
                    }
                ],
                "services": {
                    "appinvite_service": {
                        "other_platform_oauth_client": []
                    }
                }
            }
        ],
        "configuration_version": "1"
    }


def save_firebase_credentials_json(output_path: str = "cred/firebase-credentials.json") -> None:
    """
    Save firebase-credentials.json file from environment variables.
    
    Args:
        output_path: Path where to save the file
    """
    credentials = generate_firebase_credentials_json()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✓ Generated {output_path} from environment variables")


def save_google_services_json(output_path: str = "cred/google-services.json") -> None:
    """
    Save google-services.json file from environment variables.
    
    Args:
        output_path: Path where to save the file
    """
    services = generate_google_services_json()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(services, f, indent=2)
    
    print(f"✓ Generated {output_path} from environment variables")


def generate_all_firebase_files(base_path: str = "cred") -> None:
    """
    Generate both Firebase JSON files from environment variables.
    
    Args:
        base_path: Base directory where to save the files (default: cred)
    """
    base = Path(base_path)
    
    save_firebase_credentials_json(str(base / "firebase-credentials.json"))
    save_google_services_json(str(base / "google-services.json"))


if __name__ == "__main__":
    # When run directly, generate both files in the current directory
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    print("Generating Firebase configuration files from environment variables...")
    generate_all_firebase_files()
    print("\n✓ All Firebase configuration files generated successfully!")
