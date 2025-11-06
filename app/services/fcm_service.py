import os
import json
from typing import Optional, Dict, Any
from firebase_admin import credentials, initialize_app, messaging
from firebase_admin.exceptions import FirebaseError
import logging

logger = logging.getLogger(__name__)


class FCMService:
    """Service for managing Firebase Cloud Messaging."""
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK with service account credentials from environment variables."""
        if cls._initialized:
            return
        
        try:
            # Try to load credentials from environment variables first
            firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
            
            if firebase_project_id:
                # Build credentials from environment variables
                logger.info("Loading Firebase credentials from environment variables")
                from app.utils.firebase_json_generator import generate_firebase_credentials_json
                
                cred_dict = generate_firebase_credentials_json()
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback to loading from file
                logger.info("Loading Firebase credentials from file")
                firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "cred/firebase-credentials.json")
                
                if not os.path.exists(firebase_cred_path):
                    logger.warning(f"Firebase credentials file not found at {firebase_cred_path}")
                    return
                
                cred = credentials.Certificate(firebase_cred_path)
            
            initialize_app(cred)
            cls._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise
    
    @staticmethod
    def send_notification(
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send a push notification to a specific device.
        
        Args:
            fcm_token: FCM token of the target device
            title: Notification title
            body: Notification body/message
            data: Optional additional data payload
            image_url: Optional image URL for notification
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Ensure Firebase is initialized
            FCMService.initialize()
            
            if not FCMService._initialized:
                logger.warning("Firebase not initialized, cannot send notification")
                return False
            
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        priority='high',
                        visibility='public',
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True
                        )
                    )
                )
            )
            
            # Send message
            response = messaging.send(message)
            logger.info(f"Successfully sent notification to {fcm_token[:10]}...: {response}")
            return True
            
        except FirebaseError as e:
            logger.error(f"Firebase error sending notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    @staticmethod
    def send_multicast_notification(
        fcm_tokens: list[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a push notification to multiple devices.
        
        Args:
            fcm_tokens: List of FCM tokens
            title: Notification title
            body: Notification body/message
            data: Optional additional data payload
            image_url: Optional image URL for notification
            
        Returns:
            dict: Result with success and failure counts
        """
        try:
            # Ensure Firebase is initialized
            FCMService.initialize()
            
            if not FCMService._initialized:
                logger.warning("Firebase not initialized, cannot send notifications")
                return {"success_count": 0, "failure_count": len(fcm_tokens), "failed_tokens": fcm_tokens}
            
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=fcm_tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        priority='high',
                        visibility='public',
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True
                        )
                    )
                )
            )
            
            # Send multicast message
            response = messaging.send_multicast(message)
            
            # Process results
            failed_tokens = []
            if response.failure_count > 0:
                for idx, result in enumerate(response.responses):
                    if not result.success:
                        failed_tokens.append(fcm_tokens[idx])
                        logger.error(f"Failed to send to token {fcm_tokens[idx][:10]}...: {result.exception}")
            
            logger.info(f"Multicast notification result - Success: {response.success_count}, Failure: {response.failure_count}")
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "failed_tokens": failed_tokens
            }
            
        except FirebaseError as e:
            logger.error(f"Firebase error sending multicast notification: {str(e)}")
            return {"success_count": 0, "failure_count": len(fcm_tokens), "failed_tokens": fcm_tokens}
        except Exception as e:
            logger.error(f"Error sending multicast notification: {str(e)}")
            return {"success_count": 0, "failure_count": len(fcm_tokens), "failed_tokens": fcm_tokens}
    
    @staticmethod
    def send_reminder_notification(
        fcm_token: str,
        reminder_title: str,
        reminder_message: str,
        reminder_id: int,
        reminder_type: str
    ) -> bool:
        """
        Send a reminder push notification.
        
        Args:
            fcm_token: FCM token of the target device
            reminder_title: Reminder title
            reminder_message: Reminder message
            reminder_id: ID of the reminder
            reminder_type: Type of reminder
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        data = {
            "reminder_id": str(reminder_id),
            "reminder_type": reminder_type,
            "notification_type": "reminder"
        }
        
        return FCMService.send_notification(
            fcm_token=fcm_token,
            title=reminder_title,
            body=reminder_message,
            data=data
        )
