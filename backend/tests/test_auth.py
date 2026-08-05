from datetime import timedelta

from jose import jwt

import auth
import crud
import schemas


def test_password_hash_is_not_plaintext_and_verifies_correctly():
    hashed = auth.get_password_hash("mysecretpassword")

    assert hashed != "mysecretpassword"
    assert auth.verify_password("mysecretpassword", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = auth.get_password_hash("mysecretpassword")

    assert auth.verify_password("wrongpassword", hashed) is False


def test_create_access_token_carries_expected_claims():
    token = auth.create_access_token(
        {"sub": "admin@warhammer.store", "user_id": 1, "is_admin": True},
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])

    assert payload["sub"] == "admin@warhammer.store"
    assert payload["user_id"] == 1
    assert payload["is_admin"] is True
    assert "exp" in payload


def test_authenticate_user_succeeds_with_correct_credentials(db_session):
    crud.create_user(
        db_session,
        schemas.UserCreate(email="user@example.com", password="correct-horse", full_name="Test User"),
    )

    user = auth.authenticate_user(db_session, "user@example.com", "correct-horse")

    assert user is not None
    assert user.email == "user@example.com"


def test_authenticate_user_fails_with_wrong_password(db_session):
    crud.create_user(
        db_session,
        schemas.UserCreate(email="user@example.com", password="correct-horse", full_name="Test User"),
    )

    user = auth.authenticate_user(db_session, "user@example.com", "wrong-password")

    assert user is None


def test_authenticate_user_fails_for_unknown_email(db_session):
    user = auth.authenticate_user(db_session, "nobody@example.com", "whatever")

    assert user is None
