"""Validate cryptographic reviewer identity rather than trusting HTTP reviewer_id."""
from datetime import datetime, timezone, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from productpulse.api.reviewer_auth import ReviewerJWTVerifier, ReviewTokenError


ISSUER="https://idp.example.org/realms/productpulse"
AUDIENCE="productpulse-review-api"


@pytest.fixture()
def keypair():
    private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    return private,private.public_key()


@pytest.fixture()
def verifier(keypair):
    _, public=keypair
    return ReviewerJWTVerifier(
        issuer=ISSUER, audience=AUDIENCE,
        signing_key_resolver=lambda token: public,
    )


def token(private,**overrides):
    now=datetime.now(timezone.utc)
    data=dict(
        iss=ISSUER,aud=AUDIENCE,iat=now,nbf=now,exp=now+timedelta(minutes=10),
        sub="user-a", tenant_scope="org-a", roles=["productpulse_reviewer"]
    )
    data.update(overrides)
    return jwt.encode(data,private,algorithm="RS256",headers={"kid":"unit-key-1"})


def test_signed_reviewer_identity_comes_from_claims(verifier,keypair):
    result=verifier.verify(token(keypair[0]),expected_scope="org-a",required_role="productpulse_reviewer")
    assert result.reviewer_id==ISSUER+"#user-a"
    assert result.tenant_scope=="org-a"
    assert "productpulse_reviewer" in result.roles


@pytest.mark.parametrize("claim",[
    {"iss":"https://evil.example.org/realm"},
    {"aud":"wrong-audience"},
    {"exp":datetime.now(timezone.utc)-timedelta(seconds=1)},
    {"iat":datetime.now(timezone.utc)+timedelta(days=1)},
    {"sub":""},
    {"tenant_scope":"other-org"},
    {"roles":["staff-only"]},
    {"roles":"productpulse_reviewer"},
])
def test_untrusted_or_invalid_claims_are_rejected(verifier,keypair,claim):
    with pytest.raises(ReviewTokenError):
        verifier.verify(token(keypair[0],**claim),expected_scope="org-a",required_role="productpulse_reviewer")


def test_different_signing_key_is_rejected(verifier,keypair):
    attacker=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    with pytest.raises(ReviewTokenError):
        verifier.verify(token(attacker),expected_scope="org-a",required_role="productpulse_reviewer")


def test_hs256_algorithm_confusion_rejected_before_key_resolution(verifier):
    forged=jwt.encode({"iss":ISSUER,"sub":"admin","aud":AUDIENCE},"intentionally-long-not-a-real-test-secret-0123456789",algorithm="HS256")
    with pytest.raises(ReviewTokenError):
        verifier.verify(forged,expected_scope="org-a",required_role="productpulse_reviewer")


def test_missing_iat_or_exp_or_sub_rejected(verifier,keypair):
    now=datetime.now(timezone.utc)
    for missing in ("iat","exp","sub"):
        values={"iss":ISSUER,"aud":AUDIENCE,"iat":now,"exp":now+timedelta(minutes=5),
                "sub":"u1","tenant_scope":"org-a","roles":["productpulse_reviewer"]}
        values.pop(missing)
        signed=jwt.encode(values,keypair[0],algorithm="RS256")
        with pytest.raises(ReviewTokenError):
            verifier.verify(signed,expected_scope="org-a",required_role="productpulse_reviewer")


def test_lead_role_required_for_lead_operation(verifier,keypair):
    with pytest.raises(ReviewTokenError):
        verifier.verify(token(keypair[0]),expected_scope="org-a",required_role="productpulse_review_lead")


def test_untrusted_issuer_or_remote_jwks_url_rejected():
    with pytest.raises(ValueError,match="HTTPS"):
        ReviewerJWTVerifier(issuer="http://idp.example.org",audience=AUDIENCE,jwks_url="https://idp.example.org/keys")
    with pytest.raises(ValueError,match="HTTPS"):
        ReviewerJWTVerifier(issuer=ISSUER,audience=AUDIENCE,jwks_url="http://evil.example.org/keys")
    with pytest.raises(ValueError,match="host"):
        ReviewerJWTVerifier(issuer=ISSUER,audience=AUDIENCE,jwks_url="https://evil.example.org/keys")
