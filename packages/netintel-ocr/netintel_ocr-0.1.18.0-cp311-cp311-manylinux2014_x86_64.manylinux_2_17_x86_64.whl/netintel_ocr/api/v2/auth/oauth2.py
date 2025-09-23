"""
OAuth2 and OIDC Authentication Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import jwt
import httpx
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2AuthorizationCodeBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from pydantic import BaseModel, Field
from cachetools import TTLCache
import secrets
from ..config import get_settings
from ..exceptions import AuthenticationError, AuthorizationError


logger = logging.getLogger(__name__)
settings = get_settings()


# Token cache to avoid repeated validation
token_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute cache


class TokenData(BaseModel):
    """Token payload data"""
    sub: str  # Subject (user ID)
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    scope: Optional[str] = None


class OIDCConfig(BaseModel):
    """OIDC Provider Configuration"""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "openid profile email"


class OAuth2Service:
    """OAuth2/OIDC authentication service"""

    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl="/api/v2/auth/token",
            auto_error=True,
        )
        
        self.http_bearer = HTTPBearer(auto_error=False)
        
        # OIDC configuration
        self.oidc_config: Optional[OIDCConfig] = None
        if settings.OIDC_ISSUER:
            self.oidc_config = OIDCConfig(
                issuer=settings.OIDC_ISSUER,
                authorization_endpoint=settings.OIDC_AUTH_ENDPOINT,
                token_endpoint=settings.OIDC_TOKEN_ENDPOINT,
                userinfo_endpoint=settings.OIDC_USERINFO_ENDPOINT,
                jwks_uri=settings.OIDC_JWKS_URI,
                client_id=settings.OIDC_CLIENT_ID,
                client_secret=settings.OIDC_CLIENT_SECRET,
                redirect_uri=settings.OIDC_REDIRECT_URI,
                scope=settings.OIDC_SCOPE or "openid profile email",
            )
        
        # JWT configuration
        self.jwt_secret = settings.JWT_SECRET_KEY or secrets.token_urlsafe(32)
        self.jwt_algorithm = settings.JWT_ALGORITHM or "HS256"
        self.jwt_expiry = settings.JWT_EXPIRY_HOURS or 24
        
        # JWKS cache for OIDC
        self.jwks_cache: Optional[Dict[str, Any]] = None
        self.jwks_cache_time: Optional[datetime] = None

    async def create_access_token(
        self,
        subject: str,
        roles: List[str] = None,
        permissions: List[str] = None,
        additional_claims: Dict[str, Any] = None,
    ) -> str:
        """
        Create JWT access token
        
        Args:
            subject: User identifier
            roles: User roles
            permissions: User permissions
            additional_claims: Additional JWT claims
            
        Returns:
            JWT token string
        """
        
        now = datetime.utcnow()
        expire = now + timedelta(hours=self.jwt_expiry)
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": expire,
            "roles": roles or [],
            "permissions": permissions or [],
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Cache token for quick validation
        token_cache[token] = TokenData(**payload)
        
        return token

    async def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData with decoded claims
            
        Raises:
            AuthenticationError: If token is invalid
        """
        
        # Check cache first
        if token in token_cache:
            return token_cache[token]
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
            )
            
            token_data = TokenData(**payload)
            
            # Cache for future use
            token_cache[token] = token_data
            
            return token_data
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    async def get_oidc_authorization_url(self, state: str = None) -> str:
        """
        Get OIDC authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        
        if not self.oidc_config:
            raise AuthenticationError("OIDC not configured")
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.oidc_config.client_id,
            "response_type": "code",
            "redirect_uri": self.oidc_config.redirect_uri,
            "scope": self.oidc_config.scope,
            "state": state,
        }
        
        # Build URL
        url = self.oidc_config.authorization_endpoint
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        
        return f"{url}?{query_string}"

    async def exchange_code_for_token(
        self,
        code: str,
        state: str = None,
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens
        
        Args:
            code: Authorization code
            state: State parameter for validation
            
        Returns:
            Token response from OIDC provider
        """
        
        if not self.oidc_config:
            raise AuthenticationError("OIDC not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.oidc_config.token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.oidc_config.redirect_uri,
                    "client_id": self.oidc_config.client_id,
                    "client_secret": self.oidc_config.client_secret,
                },
            )
            
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to exchange code: {response.text}"
                )
            
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from OIDC provider
        
        Args:
            access_token: Access token from OIDC provider
            
        Returns:
            User information
        """
        
        if not self.oidc_config:
            raise AuthenticationError("OIDC not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.oidc_config.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to get user info: {response.text}"
                )
            
            return response.json()

    async def verify_oidc_token(self, id_token: str) -> TokenData:
        """
        Verify OIDC ID token
        
        Args:
            id_token: ID token from OIDC provider
            
        Returns:
            TokenData with verified claims
        """
        
        if not self.oidc_config:
            raise AuthenticationError("OIDC not configured")
        
        # Get JWKS if not cached or expired
        if not self.jwks_cache or (
            self.jwks_cache_time and
            (datetime.utcnow() - self.jwks_cache_time).seconds > 3600
        ):
            await self._fetch_jwks()
        
        try:
            # Decode without verification first to get header
            unverified = jwt.decode(
                id_token,
                options={"verify_signature": False},
            )
            
            # Get the key ID from header
            header = jwt.get_unverified_header(id_token)
            kid = header.get("kid")
            
            # Find the matching key
            key = self._find_jwk(kid)
            if not key:
                raise AuthenticationError("No matching key found")
            
            # Verify token with the key
            payload = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=self.oidc_config.client_id,
                issuer=self.oidc_config.issuer,
            )
            
            return TokenData(**payload)
            
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid OIDC token: {str(e)}")

    async def _fetch_jwks(self):
        """
        Fetch JWKS from OIDC provider
        """
        
        if not self.oidc_config:
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.oidc_config.jwks_uri)
            
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to fetch JWKS: {response.text}"
                )
            
            self.jwks_cache = response.json()
            self.jwks_cache_time = datetime.utcnow()

    def _find_jwk(self, kid: str) -> Optional[Dict[str, Any]]:
        """
        Find JWK by key ID
        
        Args:
            kid: Key ID
            
        Returns:
            JWK if found
        """
        
        if not self.jwks_cache:
            return None
        
        for key in self.jwks_cache.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        return None

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        
        if not self.oidc_config:
            raise AuthenticationError("OIDC not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.oidc_config.token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.oidc_config.client_id,
                    "client_secret": self.oidc_config.client_secret,
                },
            )
            
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh token: {response.text}"
                )
            
            return response.json()


# Global OAuth2 service instance
oauth2_service = OAuth2Service()


# Dependency for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(oauth2_service.http_bearer),
) -> TokenData:
    """
    FastAPI dependency to get current user from token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_data = await oauth2_service.verify_token(credentials.credentials)
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(required_roles: List[str]):
    """
    Dependency factory to require specific roles
    
    Args:
        required_roles: List of required roles
        
    Returns:
        FastAPI dependency function
    """
    
    async def check_roles(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        """
        Check if user has required roles
        
        Args:
            current_user: Current user data
            
        Returns:
            TokenData if authorized
            
        Raises:
            HTTPException: If user lacks required roles
        """
        
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {required_roles}",
            )
        
        return current_user
    
    return check_roles


def require_permissions(required_permissions: List[str]):
    """
    Dependency factory to require specific permissions
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        FastAPI dependency function
    """
    
    async def check_permissions(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        """
        Check if user has required permissions
        
        Args:
            current_user: Current user data
            
        Returns:
            TokenData if authorized
            
        Raises:
            HTTPException: If user lacks required permissions
        """
        
        if not any(
            perm in current_user.permissions for perm in required_permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permissions: {required_permissions}",
            )
        
        return current_user
    
    return check_permissions