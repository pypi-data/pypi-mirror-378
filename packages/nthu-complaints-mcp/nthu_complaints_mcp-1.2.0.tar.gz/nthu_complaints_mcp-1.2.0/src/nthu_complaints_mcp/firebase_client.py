"""Firebase client initialization and management using REST API."""

import logging
import json
import hashlib
import time
from typing import Optional, Dict, Any
import requests
from google.auth import jwt
from google.auth.credentials import AnonymousCredentials
from google.auth.transport import requests as google_requests
import google.auth
from .config import config

logger = logging.getLogger(__name__)


class FirebaseClient:
    """REST-based Firebase client wrapper."""

    def __init__(self):
        """Initialize Firebase client."""
        self._project_id: Optional[str] = None
        self._credentials: Optional[Dict[str, Any]] = None
        self._access_token: Optional[str] = None
        self._initialized = False
        self._base_url = ""

    def initialize(self) -> bool:
        """Initialize Firebase REST client.

        Returns:
            True if initialization successful, False otherwise.
        """
        if self._initialized:
            return True

        try:
            if config.has_firebase_config():
                self._credentials = config.get_firebase_config()
                self._project_id = self._credentials.get('project_id')
                self._base_url = f"https://firestore.googleapis.com/v1/projects/{self._project_id}/databases/(default)/documents"

                # Get access token
                self._refresh_access_token()

                self._initialized = True
                logger.info("Firebase REST client initialized successfully")
                return True
            else:
                logger.error("No Firebase configuration found")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Firebase REST client: {e}")
            return False

    def _refresh_access_token(self) -> None:
        """Refresh the access token using service account credentials."""
        try:
            if not self._credentials:
                raise RuntimeError("No credentials loaded")

            # Create JWT for service account
            now = int(time.time())
            payload = {
                'iss': self._credentials['client_email'],
                'scope': 'https://www.googleapis.com/auth/datastore https://www.googleapis.com/auth/firebase',
                'aud': 'https://oauth2.googleapis.com/token',
                'iat': now,
                'exp': now + 3600,
            }

            # Sign JWT with private key
            private_key = self._credentials['private_key']

            # Use cryptography to create a proper RSA private key object
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa

            # Parse the private key
            private_key_obj = serialization.load_pem_private_key(
                private_key.encode(),
                password=None
            )

            # Create JWT manually
            import base64
            import json as json_lib

            header = {"alg": "RS256", "typ": "JWT"}
            header_b64 = base64.urlsafe_b64encode(json_lib.dumps(header).encode()).decode().rstrip('=')
            payload_b64 = base64.urlsafe_b64encode(json_lib.dumps(payload).encode()).decode().rstrip('=')

            # Sign the token
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding

            signature_input = f"{header_b64}.{payload_b64}".encode()
            signature = private_key_obj.sign(
                signature_input,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')

            token = f"{header_b64}.{payload_b64}.{signature_b64}"

            # Exchange JWT for access token
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': token
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data['access_token']
            else:
                raise RuntimeError(f"Failed to get access token: {response.text}")

        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            # Fallback to using google.auth
            try:
                creds, _ = google.auth.default()
                request = google_requests.Request()
                creds.refresh(request)
                self._access_token = creds.token
            except Exception as fallback_e:
                logger.error(f"Fallback auth also failed: {fallback_e}")
                raise

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        if not self._access_token:
            self._refresh_access_token()

        return {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

    @property
    def db(self):
        """Get database interface."""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")
        return self

    def collection(self, collection_name: str):
        """Get collection reference."""
        return FirebaseCollection(self, collection_name)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make authenticated request to Firebase."""
        headers = self._get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers

        response = requests.request(method, url, **kwargs)

        # Retry once if token might be expired
        if response.status_code == 401:
            self._refresh_access_token()
            headers = self._get_headers()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            response = requests.request(method, url, **kwargs)

        return response

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email using Firebase Auth REST API.

        Note: This is a simplified implementation that returns mock data.
        In a real implementation, you'd need to use Firebase Auth REST API.
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")

        # For demo purposes, create a mock user record
        user_id = hashlib.md5(email.encode()).hexdigest()
        return {
            'uid': user_id,
            'email': email,
            'email_verified': True,
            'display_name': email.split('@')[0],
        }

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token.

        Note: This is a simplified implementation.
        In production, you should use proper JWT verification.
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Firebase not initialized")

        # For demo purposes, decode without verification
        # In production, properly verify the JWT signature
        try:
            import base64
            payload = id_token.split('.')[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            return json.loads(decoded)
        except Exception as e:
            raise RuntimeError(f"Invalid ID token: {e}")


class FirebaseCollection:
    """Firestore collection interface."""

    def __init__(self, client: FirebaseClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
        self.base_url = f"{client._base_url}/{collection_name}"

    def document(self, doc_id: str):
        """Get document reference."""
        return FirebaseDocument(self.client, f"{self.base_url}/{doc_id}")

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add document to collection."""
        response = self.client._make_request('POST', self.base_url, json={'fields': self._convert_to_firestore(data)})
        if response.status_code in [200, 201]:
            result = response.json()
            return {'id': result['name'].split('/')[-1]}
        else:
            raise RuntimeError(f"Failed to add document: {response.text}")

    def where(self, field: str, op: str, value: Any):
        """Simple where query implementation."""
        return FirebaseQuery(self.client, self.base_url, [(field, op, value)])

    def _convert_to_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python data to Firestore format."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = {'stringValue': value}
            elif isinstance(value, int):
                result[key] = {'integerValue': str(value)}
            elif isinstance(value, bool):
                result[key] = {'booleanValue': value}
            elif isinstance(value, dict):
                result[key] = {'mapValue': {'fields': self._convert_to_firestore(value)}}
            else:
                result[key] = {'stringValue': str(value)}
        return result


class FirebaseDocument:
    """Firestore document interface."""

    def __init__(self, client: FirebaseClient, doc_url: str):
        self.client = client
        self.doc_url = doc_url

    def get(self) -> Dict[str, Any]:
        """Get document data."""
        response = self.client._make_request('GET', self.doc_url)
        if response.status_code == 200:
            result = response.json()
            return self._convert_from_firestore(result.get('fields', {}))
        elif response.status_code == 404:
            return None
        else:
            raise RuntimeError(f"Failed to get document: {response.text}")

    def set(self, data: Dict[str, Any]) -> None:
        """Set document data."""
        firestore_data = {'fields': self._convert_to_firestore(data)}
        response = self.client._make_request('PATCH', self.doc_url, json=firestore_data)
        if response.status_code not in [200, 201]:
            raise RuntimeError(f"Failed to set document: {response.text}")

    def update(self, data: Dict[str, Any]) -> None:
        """Update document data."""
        self.set(data)

    def delete(self) -> None:
        """Delete document."""
        response = self.client._make_request('DELETE', self.doc_url)
        if response.status_code not in [200, 204]:
            raise RuntimeError(f"Failed to delete document: {response.text}")

    def _convert_to_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python data to Firestore format."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = {'stringValue': value}
            elif isinstance(value, int):
                result[key] = {'integerValue': str(value)}
            elif isinstance(value, bool):
                result[key] = {'booleanValue': value}
            elif isinstance(value, dict):
                result[key] = {'mapValue': {'fields': self._convert_to_firestore(value)}}
            else:
                result[key] = {'stringValue': str(value)}
        return result

    def _convert_from_firestore(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Firestore data to Python format."""
        result = {}
        for key, value in fields.items():
            if 'stringValue' in value:
                result[key] = value['stringValue']
            elif 'integerValue' in value:
                result[key] = int(value['integerValue'])
            elif 'booleanValue' in value:
                result[key] = value['booleanValue']
            elif 'mapValue' in value:
                result[key] = self._convert_from_firestore(value['mapValue'].get('fields', {}))
            else:
                result[key] = str(value)
        return result


class FirebaseQuery:
    """Simple Firestore query implementation."""

    def __init__(self, client: FirebaseClient, base_url: str, conditions: list):
        self.client = client
        self.base_url = base_url
        self.conditions = conditions

    def stream(self):
        """Stream query results."""
        # This is a simplified implementation
        # For a full implementation, you'd need to use the Firestore Query API
        response = self.client._make_request('GET', self.base_url)
        if response.status_code == 200:
            result = response.json()
            documents = result.get('documents', [])
            for doc in documents:
                yield self._convert_from_firestore(doc.get('fields', {}))
        else:
            raise RuntimeError(f"Failed to execute query: {response.text}")

    def _convert_from_firestore(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Firestore data to Python format."""
        result = {}
        for key, value in fields.items():
            if 'stringValue' in value:
                result[key] = value['stringValue']
            elif 'integerValue' in value:
                result[key] = int(value['integerValue'])
            elif 'booleanValue' in value:
                result[key] = value['booleanValue']
            elif 'mapValue' in value:
                result[key] = self._convert_from_firestore(value['mapValue'].get('fields', {}))
            else:
                result[key] = str(value)
        return result


# Global Firebase client instance
firebase_client = FirebaseClient()