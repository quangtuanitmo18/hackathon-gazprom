"""Verify human identity using trusted OIDC RS256 access tokens, not form fields.

For production, configure an HTTPS issuer, audience and matching-host HTTPS
JWKS URL from environment. No HTTP claim controls key URL/algorithms.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import jwt


class ReviewTokenError(ValueError):
    """Untrusted, expired, forged, insufficient or wrong-tenant access token."""


@dataclass(frozen=True)
class ReviewerPrincipal:
    reviewer_id: str
    tenant_scope: str
    roles: frozenset[str]


class ReviewerJWTVerifier:
    def __init__(
        self,
        *, issuer: str, audience: str, jwks_url: str | None = None,
        signing_key_resolver: Callable[[str], Any] | None = None,
    ) -> None:
        iss = urlparse(issuer)
        if iss.scheme != "https" or not iss.hostname or iss.username or iss.password:
            raise ValueError("OIDC issuer must be HTTPS and without embedded credentials")
        if not isinstance(audience, str) or not audience.strip():
            raise ValueError("OIDC audience is required")
        if jwks_url is None and signing_key_resolver is None:
            raise ValueError("OIDC JWKS URL is required without test key resolver")
        if jwks_url is not None:
            jwks = urlparse(jwks_url)
            if jwks.scheme != "https" or not jwks.hostname or jwks.username or jwks.password:
                raise ValueError("JWKS URL must be HTTPS without credentials")
            if jwks.hostname != iss.hostname:
                raise ValueError("JWKS host must match trusted OIDC issuer host")
        self.issuer = issuer.rstrip("/")
        self.audience = audience
        # Resolver is used for local crypto tests; production always builds
        # a PyJWT client from a configured, trusted URL.
        self._resolver = signing_key_resolver
        self._jwks = jwt.PyJWKClient(jwks_url, timeout=5, lifespan=300) if jwks_url else None

    def verify(
        self, access_token: str, *,
        expected_scope: str, required_role: str,
    ) -> ReviewerPrincipal:
        if not access_token or not isinstance(access_token, str) or len(access_token) > 16384:
            raise ReviewTokenError("access token is missing or invalid")
        try:
            header = jwt.get_unverified_header(access_token)
            if header.get("alg") != "RS256":
                raise ReviewTokenError("only RS256 access tokens are accepted")
            if self._resolver is not None:
                key = self._resolver(access_token)
            else:
                if self._jwks is None:
                    raise ReviewTokenError("JWKS is unavailable")
                key = self._jwks.get_signing_key_from_jwt(access_token).key
            claims = jwt.decode(
                access_token, key, algorithms=["RS256"],
                audience=self.audience, issuer=self.issuer,
                options={"require": ["iss", "aud", "sub", "exp", "iat", "tenant_scope"]},
            )
        except (jwt.PyJWTError, jwt.exceptions.PyJWKClientError, ValueError, TypeError) as exc:
            raise ReviewTokenError("invalid OIDC access token") from exc

        sub = claims.get("sub")
        tenant = claims.get("tenant_scope")
        roles = claims.get("roles")
        if not isinstance(sub, str) or not sub.strip():
            raise ReviewTokenError("OIDC subject required")
        if not isinstance(tenant, str) or tenant != expected_scope:
            raise ReviewTokenError("token is not valid for this tenant scope")
        if not isinstance(roles, list) or not all(isinstance(x, str) for x in roles):
            raise ReviewTokenError("OIDC roles claim must be an array")
        if required_role not in roles:
            raise ReviewTokenError("required reviewer role absent")
        return ReviewerPrincipal(
            reviewer_id=f"{self.issuer}#{sub}",
            tenant_scope=tenant,
            roles=frozenset(roles),
        )
