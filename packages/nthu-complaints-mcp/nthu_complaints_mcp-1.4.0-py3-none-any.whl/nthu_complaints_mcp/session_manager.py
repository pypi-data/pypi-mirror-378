"""Session management for user authentication."""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions."""

    def __init__(self, session_timeout: int = 3600):  # 1 hour default
        """Initialize session manager.

        Args:
            session_timeout: Session timeout in seconds.
        """
        self.session_timeout = session_timeout
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Create a new session.

        Args:
            user_data: User information to store in session.

        Returns:
            Session token.
        """
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)

        self._sessions[session_token] = {
            **user_data,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now().isoformat()
        }

        logger.info(f"Created session for user {user_data.get('email', 'unknown')}")
        return session_token

    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session data.

        Args:
            session_token: Session token.

        Returns:
            Session data if valid, None otherwise.
        """
        if session_token not in self._sessions:
            return None

        session = self._sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])

        if datetime.now() > expires_at:
            # Session expired
            self.delete_session(session_token)
            return None

        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        return session

    def delete_session(self, session_token: str) -> bool:
        """Delete a session.

        Args:
            session_token: Session token to delete.

        Returns:
            True if session was deleted, False if not found.
        """
        if session_token in self._sessions:
            user_email = self._sessions[session_token].get('email', 'unknown')
            del self._sessions[session_token]
            logger.info(f"Deleted session for user {user_email}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions.

        Returns:
            Number of sessions cleaned up.
        """
        now = datetime.now()
        expired_tokens = []

        for token, session in self._sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if now > expires_at:
                expired_tokens.append(token)

        for token in expired_tokens:
            self.delete_session(token)

        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")

        return len(expired_tokens)

    def extend_session(self, session_token: str) -> bool:
        """Extend session expiration time.

        Args:
            session_token: Session token to extend.

        Returns:
            True if session was extended, False if not found.
        """
        session = self.get_session(session_token)
        if session:
            new_expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
            self._sessions[session_token]["expires_at"] = new_expires_at.isoformat()
            return True
        return False

    def get_active_sessions_count(self) -> int:
        """Get number of active sessions.

        Returns:
            Number of active sessions.
        """
        self.cleanup_expired_sessions()
        return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()