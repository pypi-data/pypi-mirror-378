from datetime import datetime, timedelta

from polymodel import Field, Model
from polymodel._compat import get_fields_set


def test_fields_set():
    class User(Model):
        username: str
        email: str = "test@test.com"
        last_updated: datetime = Field(default_factory=datetime.now)

    user = User(username="bob")
    assert get_fields_set(user) == {"username"}
    user = User(username="bob", email="bob@test.com")
    assert get_fields_set(user) == {"username", "email"}
    user = User(
        username="bob",
        email="bob@test.com",
        last_updated=datetime.now() - timedelta(days=1),
    )
    assert get_fields_set(user) == {"username", "email", "last_updated"}
