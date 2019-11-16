import pytest
from pydantic import ValidationError

from app.models.users import RegisterIn


def test_register_correct():
    RegisterIn(username="username", email="email@email.com", password="Abc@123!")


def test_register_password_no_lowercase():
    with pytest.raises(ValidationError):
        RegisterIn(username="username", email="email@email.com", password="ABC@123!")


def test_register_password_no_uppercase():
    with pytest.raises(ValidationError):
        RegisterIn(username="username", email="email@email.com", password="abc@123!")


def test_register_password_no_number():
    with pytest.raises(ValidationError):
        RegisterIn(username="username", email="email@email.com", password="Abc@abc!")


def test_register_password_no_special_char():
    with pytest.raises(ValidationError):
        RegisterIn(username="username", email="email@email.com", password="Abca123a")


def test_register_password_minimal_lenght():
    with pytest.raises(ValidationError):
        RegisterIn(username="username", email="email@email.com", password="Abc@123")
