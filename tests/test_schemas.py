import pytest
from pydantic import ValidationError

from app.api.v1.schemas import WebhookChatPayload


def test_chat_schema_ok():
    payload = WebhookChatPayload(
        user_id="u1",
        message="hola",
    )

    assert payload.user_id == "u1"
    assert payload.message == "hola"


def test_chat_schema_extra_field():
    with pytest.raises(ValidationError):
        WebhookChatPayload(
            user_id="u1",
            message="hola",
            extra="x",
        )
