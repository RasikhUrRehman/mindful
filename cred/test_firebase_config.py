#!/usr/bin/env python3
"""
Test script to verify Firebase configuration from environment variables.
"""
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Try to load environment variables
try:
    from dotenv import load_dotenv
    env_path = os.path.join(parent_dir, '.env')
    load_dotenv(env_path)
except ImportError:
    pass  # Will try again in main()


def test_env_variables():
    """Test that required environment variables are set."""
    print("Testing environment variables...")
    
    required_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "GOOGLE_SERVICES_PROJECT_NUMBER",
        "GOOGLE_SERVICES_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ✗ {var}: NOT SET")
            missing.append(var)
    
    return len(missing) == 0, missing


def test_json_generation():
    """Test JSON file generation."""
    print("\nTesting JSON generation...")
    
    try:
        from app.utils.firebase_json_generator import (
            generate_firebase_credentials_json,
            generate_google_services_json
        )
        
        # Test firebase-credentials.json generation
        firebase_creds = generate_firebase_credentials_json()
        if firebase_creds.get("project_id"):
            print(f"  ✓ firebase-credentials.json: Generated successfully")
            print(f"    Project ID: {firebase_creds.get('project_id')}")
        else:
            print(f"  ✗ firebase-credentials.json: Missing project_id")
            return False
        
        # Test google-services.json generation
        google_services = generate_google_services_json()
        if google_services.get("project_info", {}).get("project_id"):
            print(f"  ✓ google-services.json: Generated successfully")
            print(f"    Project ID: {google_services['project_info']['project_id']}")
        else:
            print(f"  ✗ google-services.json: Missing project_id")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error generating JSON: {e}")
        return False


def test_fcm_service():
    """Test FCM service initialization."""
    print("\nTesting FCM service...")
    
    try:
        from app.services.fcm_service import FCMService
        
        FCMService.initialize()
        
        if FCMService._initialized:
            print(f"  ✓ FCM Service: Initialized successfully")
            return True
        else:
            print(f"  ✗ FCM Service: Initialization failed")
            return False
            
    except Exception as e:
        print(f"  ✗ FCM Service error: {e}")
        return False


def main():
    print("=" * 70)
    print("Firebase Configuration Test")
    print("=" * 70)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        # Load .env from parent directory
        env_path = os.path.join(parent_dir, '.env')
        load_dotenv(env_path)
        print(f"✓ Loaded .env file from {env_path}\n")
    except ImportError:
        print("ℹ python-dotenv not installed, using system environment\n")
    
    # Run tests
    results = []
    
    # Test 1: Environment variables
    env_ok, missing = test_env_variables()
    results.append(("Environment Variables", env_ok))
    
    if not env_ok:
        print(f"\n⚠ Missing environment variables: {', '.join(missing)}")
        print("Please set these in your .env file before continuing.")
    
    # Test 2: JSON generation
    if env_ok:
        json_ok = test_json_generation()
        results.append(("JSON Generation", json_ok))
    
    # Test 3: FCM service
    if env_ok:
        fcm_ok = test_fcm_service()
        results.append(("FCM Service", fcm_ok))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ All tests passed! Your Firebase configuration is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
