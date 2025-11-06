#!/usr/bin/env python3
"""
Script to generate Firebase JSON files from environment variables.
Run this before starting the application to ensure JSON files are created from .env
"""
import sys
import os

# Add the parent directory to the path to import from app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from app.utils.firebase_json_generator import generate_all_firebase_files


if __name__ == "__main__":
    try:
        # Try to load python-dotenv if available
        try:
            from dotenv import load_dotenv
            # Load .env from parent directory
            env_path = os.path.join(parent_dir, '.env')
            load_dotenv(env_path)
            print(f"✓ Loaded environment variables from {env_path}")
        except ImportError:
            print("ℹ python-dotenv not installed, using system environment variables")
        
        # Generate the JSON files in cred folder
        print("\nGenerating Firebase configuration files from environment variables...")
        cred_dir = os.path.dirname(os.path.abspath(__file__))
        generate_all_firebase_files(cred_dir)
        print("\n✓ Firebase configuration complete!")
        
    except Exception as e:
        print(f"\n✗ Error generating Firebase configuration: {e}", file=sys.stderr)
        sys.exit(1)
