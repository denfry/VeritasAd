"""Tests for bcrypt password hashing (thesis sec. 3.4)."""
import pytest

pytest.importorskip("bcrypt")

from app.core.security import hash_password, verify_password


def test_hash_is_not_plaintext():
    hashed = hash_password("s3cret-password")
    assert hashed != "s3cret-password"
    assert hashed.startswith("$2")  # bcrypt prefix


def test_verify_correct_password():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("wrong password", hashed) is False


def test_verify_empty_hash():
    assert verify_password("anything", "") is False
