"""WhatsApp Cloud API operations — the only Meta-aware service interface."""
from typing import Any

from app.core.logging import get_logger, log_event
from app.services.integrations.meta.client import MetaGraphClient

logger = get_logger("app.meta.whatsapp")


class WhatsAppService:
    """High-level WhatsApp operations for a single tenant's credentials.

    Construct with the decrypted access token plus the WABA / phone-number IDs.
    Returns plain dicts shaped close to the Meta payloads so callers can map
    them onto local models.
    """

    def __init__(self, *, access_token: str, waba_id: str, phone_number_id: str):
        self._client = MetaGraphClient(access_token)
        self._waba_id = waba_id
        self._phone_number_id = phone_number_id

    async def get_phone_numbers(self) -> list[dict[str, Any]]:
        """List phone numbers registered under the WABA."""
        fields = "id,display_phone_number,verified_name,quality_rating,status,messaging_limit_tier"
        data = await self._client.get(
            f"{self._waba_id}/phone_numbers", params={"fields": fields}
        )
        return data.get("data", [])

    async def get_templates(self) -> list[dict[str, Any]]:
        """List message templates defined on the WABA."""
        fields = "id,name,language,category,status,components"
        data = await self._client.get(
            f"{self._waba_id}/message_templates",
            params={"fields": fields, "limit": 200},
        )
        return data.get("data", [])

    async def send_template(
        self,
        *,
        recipient: str,
        template_name: str,
        language: str,
        variables: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Send a template message. Returns the Meta send response."""
        components = _build_components(variables or {})
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": _normalize_recipient(recipient),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }
        if components:
            payload["template"]["components"] = components

        result = await self._client.post(f"{self._phone_number_id}/messages", json=payload)
        log_event(
            logger, "info", "Template sent",
            template=template_name, recipient=_mask(recipient),
        )
        return result


def _normalize_recipient(recipient: str) -> str:
    """Meta expects digits only, no leading '+'."""
    return recipient.strip().lstrip("+").replace(" ", "")


def _build_components(variables: dict[str, str]) -> list[dict]:
    """Map an ordered variable dict to body parameters {{1}}, {{2}}, ..."""
    if not variables:
        return []
    params = [{"type": "text", "text": str(v)} for v in variables.values()]
    return [{"type": "body", "parameters": params}]


def _mask(number: str) -> str:
    return number[:4] + "***" + number[-2:] if len(number) > 6 else "***"
