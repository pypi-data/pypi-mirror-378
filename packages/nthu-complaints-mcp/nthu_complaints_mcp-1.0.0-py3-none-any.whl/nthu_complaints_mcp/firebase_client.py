"""Firebase client initialization and management."""

import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore, auth
from .config import config

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Firebase client wrapper."""

    def __init__(self):
        """Initialize Firebase client."""
        self._app: Optional[firebase_admin.App] = None
        self._db: Optional[firestore.Client] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Firebase admin SDK.

        Returns:
            True if initialization successful, False otherwise.
        """
        if self._initialized:
            return True

        try:
            # Check if app already exists
            try:
                self._app = firebase_admin.get_app()
            except ValueError:
                # Initialize new app
                if config.has_firebase_config():
                    cred = credentials.Certificate(config.get_firebase_config())
                    self._app = firebase_admin.initialize_app(cred)
                else:
                    # Try to use default credentials
                    self._app = firebase_admin.initialize_app()

            self._db = firestore.client()
            self._initialized = True
            logger.info("Firebase initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False

    @property
    def db(self) -> firestore.Client:
        """Get Firestore client."""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")
        return self._db

    def get_user_by_email(self, email: str) -> auth.UserRecord:
        """Get user by email.

        Args:
            email: User email address.

        Returns:
            Firebase user record.

        Raises:
            auth.UserNotFoundError: If user not found.
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")
        return auth.get_user_by_email(email)

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token.

        Args:
            id_token: Firebase ID token.

        Returns:
            Decoded token claims.

        Raises:
            auth.InvalidIdTokenError: If token is invalid.
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")
        return auth.verify_id_token(id_token)


# Global Firebase client instance
firebase_client = FirebaseClient()