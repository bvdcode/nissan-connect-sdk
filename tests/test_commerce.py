from __future__ import annotations

from typing import cast

from aiohttp import ClientSession

from pynissan import (
    AddProductToCartInput,
    NissanClient,
    Tokens,
)

EXPECTED_OPERATIONS = {
    "ADD_PRODUCT_TO_NISSAN_STORE_CART": (
        "eed0e98dfe2cc937bc49082ee698ec7c5a160f7e1ede1aa0006f79cb5bfdd4af"
    ),
    "CANCEL_PENDING_SUBSCRIPTION": (
        "7c58341746585b1af72ceb9d106da15c99d9660016b35fab59cdf3b6ae27e20f"
    ),
    "CANCEL_SUBSCRIPTION": ("582a6770133943805e710c65e4b27ade68e9f81530f88b417e2623e9cac277d2"),
    "CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK": (
        "9c6c28d802fca574a547c921840ebb9397093a213d6f4dfd05c522e12757b990"
    ),
    "DIGITAL_WALLET_URL": ("6ebdf2e75a646b0905f99afa77af67e9e6b6b58461b0d2bce71be4bc072fd30e"),
    "NISSAN_PAY": "6f08f0f64f7bebe3ce087dcdda08ef0198d3f926dec70c43941dd54e84fc660b",
    "NISSAN_PAY_ORDER_HISTORY": (
        "03eceb4c138de1b971d5c1415b29327cd990c4ba5392a82504aa429ded0c96bb"
    ),
    "NISSAN_STORE_CHECKOUT_URL": (
        "814f25c745f3e438233e812c89e1a9dc67bdf8c7416b54e983c1e5f9a3872cfe"
    ),
    "PRODUCT_CATALOG": ("03e4214e129ea35a0a2d8255aaac2481373ef478c611cfb9684e7281d812f30f"),
    "UPSERT_NISSAN_PAY_ACCOUNT": (
        "f4483575cf435a5fa6693606a4915b97cb609fe110a74a58dbc162ba41feb0a4"
    ),
}


class FakeResponse:
    def __init__(self, field: str, value: object) -> None:
        self.status = 200
        self._payload = {"data": {field: value}}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def product_input() -> AddProductToCartInput:
    return AddProductToCartInput(
        product_id="product-id",
        quantity=1,
        vin="VIN",
        product_selling_model_id="selling-model-id",
        promotion_id=None,
    )
