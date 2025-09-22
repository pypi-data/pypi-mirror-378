from __future__ import annotations

import os
import warnings
import asyncio
import inspect
from typing import Any, Dict, Optional

try:
    from openai import AsyncOpenAI, AsyncAzureOpenAI, OpenAI, AzureOpenAI
except Exception as e:
    raise ImportError("The openai package is required. Install with: pip install -U openai") from e


def resolve_client(cfg: Dict[str, Any]) -> Optional[object]:
    """
    Returns a client instance. If cfg['client'] is provided, it's returned as-is,
    with a warning when it's not an async client (still supported via wrappers).
    Otherwise builds an AsyncOpenAI / AsyncAzureOpenAI from cfg or environment.
    """
    # If user already passed a client object, return it (warn if unexpected type)
    if "client" in cfg and cfg["client"] is not None:
        if not isinstance(cfg["client"], (AsyncOpenAI, AsyncAzureOpenAI, OpenAI, AzureOpenAI)):
            warnings.warn(
                f"resolve_client: Unexpected client type {type(cfg['client']).__name__}. "
                "Expected AsyncOpenAI, AsyncAzureOpenAI, OpenAI or AzureOpenAI. Returning anyway."
            )
        return cfg["client"]

    required_openai = ["api_key"]
    required_azure = ["api_key", "api_version", "azure_endpoint", "azure_deployment"]

    def is_complete(d: Dict[str, Any], required: list[str]) -> bool:
        return all(d.get(k) for k in required)

    # Prefer Azure when fully specified in cfg
    if is_complete(cfg, required_azure):
        return AsyncAzureOpenAI(
            api_key=cfg["api_key"],
            api_version=cfg["api_version"],
            azure_endpoint=cfg["azure_endpoint"],
            azure_deployment=cfg["azure_deployment"],
        )

    # OpenAI (non-Azure) from cfg
    if is_complete(cfg, required_openai):
        return AsyncOpenAI(
            api_key=cfg["api_key"],
            base_url=cfg.get("base_url", "https://api.openai.com/v1"),
        )

    # OpenAI from environment
    env_openai = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    }
    if is_complete(env_openai, required_openai):
        return AsyncOpenAI(**env_openai)

    # Azure from environment
    env_azure = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    }
    if is_complete(env_azure, required_azure):
        return AsyncAzureOpenAI(**env_azure)

    return None


# ---------- Async-safe wrappers that accept sync OR async clients ----------
def _is_async_client(client: object) -> bool:
    return isinstance(client, (AsyncOpenAI, AsyncAzureOpenAI))

async def responses_create(client: object, **kwargs):
    """
    Awaitable wrapper:
      - Async clients: await client.responses.create(...)
      - Sync clients: run client.responses.create(...) in a thread
    """
    if _is_async_client(client):
        return await client.responses.create(**kwargs)
    return await asyncio.to_thread(client.responses.create, **kwargs)

async def responses_submit_tool_outputs(client: object, **kwargs):
    """
    Awaitable wrapper for submit_tool_outputs with same sync/async handling.
    """
    if _is_async_client(client):
        return await client.responses.submit_tool_outputs(**kwargs)
    return await asyncio.to_thread(client.responses.submit_tool_outputs, **kwargs)
# --------------------------------------------------------------------------


# ---------- Chat Completions (fallback) ----------
async def chat_completions_create(client: object, **kwargs):
    """
    Awaitable wrapper for chat.completions.create with sync/async clients.
    """
    if _is_async_client(client):
        # AsyncOpenAI / AsyncAzureOpenAI
        return await client.chat.completions.create(**kwargs)
    # Sync OpenAI / AzureOpenAI
    return await asyncio.to_thread(client.chat.completions.create, **kwargs)


class ClientContext:
    """
    Async context wrapper to ensure the SDK’s HTTP client is closed while the loop is alive.
    Works with both async and sync clients (close() may be awaitable or not).
    """
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        try:
            close = getattr(self.client, "close", None)
            if not close:
                return
            result = close()
            if inspect.isawaitable(result):
                await result
            # if not awaitable: it's already closed synchronously
        except Exception:
            pass
