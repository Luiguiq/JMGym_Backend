import json
import hmac
import hashlib
from typing import Optional

import httpx

from app.core.config import (
    FLOW_API_KEY,
    FLOW_SECRET_KEY,
    FLOW_API_URL,
    FLOW_URL_RETURN,
    FLOW_URL_CONFIRMATION,
)


def _sign_params(params: dict, secret_key: str) -> str:
    keys = sorted(params.keys())
    to_sign = "".join(f"{key}{params[key]}" for key in keys)
    return hmac.new(
        secret_key.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_flow_payment(
    commerce_order: str,
    amount: int,
    email: str,
    subject: str,
    optional: Optional[dict] = None,
    timeout: int = 1800,
) -> dict:
    params = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": commerce_order,
        "currency": "PEN",
        "urlConfirmation": FLOW_URL_CONFIRMATION,
        "urlReturn": FLOW_URL_RETURN,
        "email": email,
        "subject": subject[:100],
        "amount": amount,
    }

    if optional:
        params["optional"] = json.dumps(optional, ensure_ascii=False)
    if timeout:
        params["timeout"] = timeout

    signature = _sign_params(params, FLOW_SECRET_KEY)
    params["s"] = signature

    with httpx.Client() as client:
        response = client.post(
            f"{FLOW_API_URL}/payment/create",
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            raise Exception(
                f"Flow API error ({response.status_code}): {response.text[:500]}"
            )
        return response.json()


def get_flow_payment_status(token: str) -> dict:
    params = {
        "apiKey": FLOW_API_KEY,
        "token": token,
    }

    signature = _sign_params(params, FLOW_SECRET_KEY)
    params["s"] = signature

    with httpx.Client() as client:
        response = client.post(
            f"{FLOW_API_URL}/payment/getStatus",
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()
