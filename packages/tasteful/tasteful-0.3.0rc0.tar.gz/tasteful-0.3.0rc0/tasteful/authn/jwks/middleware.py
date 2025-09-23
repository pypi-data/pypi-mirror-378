import requests
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
from typing import Union

from .user import JWKSUser
from tasteful.authn.base import AsyncAuthenticationMiddleware


class JWKSAuthenticationMiddleware(AsyncAuthenticationMiddleware, HTTPBearer):
    """
    Generic middleware for any OIDC provider publishing JWKS.
    Works with AWS Cognito, Auth0, Keycloak, etc.
    """

    def __init__(self, jwks_url: str, issuer: str, audience: str):
        super().__init__()
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.jwks = self._fetch_jwks()

    def _fetch_jwks(self):
        try:
            return requests.get(self.jwks_url).json()
        except Exception as e:
            raise RuntimeError(f"Unable to fetch JWKS from {self.jwks_url}: {e}")

    async def authenticate(self, request: Request) -> Union[JWKSUser, None]:
        """Authenticate user with any JWKS-based OIDC provider."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                return None

            headers = jwt.get_unverified_header(token)
            kid = headers["kid"]

            # Refresh JWKS if we don’t find the key
            key = next((k for k in self.jwks["keys"] if k["kid"] == kid), None)
            if not key:
                self.jwks = self._fetch_jwks()
                key = next((k for k in self.jwks["keys"] if k["kid"] == kid), None)

            if not key:
                raise HTTPException(status_code=401, detail="Invalid signing key")

            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )

            return JWKSUser(claims=claims, name=claims.get("username"), authenticated=True)

        except Exception as e:
            print("JWT validation error:", e)
            raise HTTPException(status_code=401, detail="Invalid or expired token")
