"""API and JWT contracts affected by the dependency security upgrades."""

import base64
import hashlib
import hmac
import json
import uuid

import pytest

from .. import auth, config, models, utils

# Issued by python-jose 3.3.0 with the public synthetic key in conftest.py.
# The expiration is 2100-01-01, so this compatibility fixture is not time-sensitive.
LEGACY_HS256_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiI0ZmRjYzlkZS1jMjQ1LTQ1NDktOGVjOC04YjRjMjk2ZTdkMmMiLCJleHAiOjQxMDI0NDQ4MDB9."
    "M6p0JOE8dq-lexUS9kchXobwTyDMavxmJWtwM3yW1us"
)


def make_signed_token(subject, *, expiration=4102444800, algorithm="HS256", key=None):
    """Build adversarial JWT inputs independently of the application JWT library."""
    def segment(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).rstrip(b"=")

    unsigned = b".".join([
        segment({"alg": algorithm, "typ": "JWT"}),
        segment({"sub": str(subject), "exp": expiration}),
    ])
    digest = hashlib.sha512 if algorithm == "HS512" else hashlib.sha256
    signature = hmac.new((key or config.settings.SECRET_KEY).encode(), unsigned, digest).digest()
    return (unsigned + b"." + base64.urlsafe_b64encode(signature).rstrip(b"=")).decode()


def test_previously_issued_hs256_token_remains_valid():
    data = auth.decode_access_token(LEGACY_HS256_TOKEN)
    assert data is not None
    assert data.user_id == uuid.UUID("4fdcc9de-c245-4549-8ec8-8b4c296e7d2c")


def test_login_token_authenticates_current_user(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword123",
    })
    assert response.status_code == 200
    current_user = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {response.json()['access_token']}",
    })
    assert current_user.status_code == 200
    assert current_user.json()["id"] == str(test_user.id)


@pytest.mark.parametrize("invalid_kind", ["expired", "wrong-key", "wrong-algorithm", "unsigned", "malformed"])
def test_invalid_tokens_cannot_authenticate_existing_user(client, test_user, invalid_kind):
    if invalid_kind == "expired":
        token = make_signed_token(test_user.id, expiration=1)
    elif invalid_kind == "wrong-key":
        token = make_signed_token(test_user.id, key="a-different-public-synthetic-test-key")
    elif invalid_kind == "wrong-algorithm":
        token = make_signed_token(test_user.id, algorithm="HS512")
    elif invalid_kind == "unsigned":
        token = make_signed_token(test_user.id, algorithm="none").rsplit(".", 1)[0] + "."
    else:
        token = "malformed-token"

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_excessive_urlencoded_fields(client):
    fields = {f"extra_{index}": "x" for index in range(1001)}
    fields.update(username="nobody@example.com", password="invalid-password")
    response = client.post("/api/v1/auth/login", data=fields)
    assert response.status_code == 400
    assert "Too many fields" in response.json()["detail"]


def test_registration_rejects_json_without_content_type(client, db_session):
    response = client.post("/api/v1/auth/register", content=json.dumps({
        "email": "missing-content-type@example.com",
        "password": "public-synthetic-password",
        "name": "Missing Content Type",
    }))
    assert 400 <= response.status_code < 500
    assert db_session.query(models.User).filter_by(email="missing-content-type@example.com").first() is None


@pytest.mark.parametrize("invisible", ["\u200b", "\u202e"])
def test_sanitize_html_rejects_disallowed_uri_with_invisible_character(invisible):
    html = f'<a href="javascript{invisible}:alert(1)">Click</a>'
    assert utils.sanitize_html(html) == "<a>Click</a>"


def test_sanitize_html_preserves_https_links_and_allowed_markup():
    html = '<p><strong>Plan</strong> <a href="https://example.com/trip" title="Trip">Open</a></p>'
    assert utils.sanitize_html(html) == html
