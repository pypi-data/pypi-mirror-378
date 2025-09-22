from __future__ import annotations
import os, base64, mimetypes, warnings
from typing import Any, Dict, List, Optional, Tuple

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

class UserMessageBuilder:
    def __init__(self, prefer_upload: bool = True):
        self.prefer_upload = prefer_upload

    def _file_to_data_url(self, path: str) -> str:
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "application/octet-stream"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def _resolve_image(self, image_source: str) -> str:
        if image_source.startswith(("http://", "https://", "data:")):
            return image_source
        if not os.path.isfile(image_source):
            raise FileNotFoundError(f"Image not found: {image_source}")
        return self._file_to_data_url(image_source)

    def _resolve_file(self, file_source: str) -> Tuple[str, str]:
        if file_source.startswith(("http://", "https://")):
            return ("file_url", file_source)
        if not os.path.isfile(file_source):
            raise FileNotFoundError(f"File not found: {file_source}")
        if self.prefer_upload and OpenAI is not None:
            try:
                # make sure HTTP resources close immediately
                with OpenAI() as client:
                    with open(file_source, "rb") as f:
                        uploaded = client.files.create(file=f, purpose="assistants")
                return ("file_id", uploaded.id)
            except Exception as e:
                warnings.warn(f"Upload failed for {file_source}, using data:-URL fallback. Reason: {e}")
        return ("file_url", self._file_to_data_url(file_source))

    def build_user_parts(
        self,
        user_text: str,
        images: Optional[List[str]] = None,
        links: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        content: List[Dict[str, Any]] = []
        if user_text:
            content.append({"type": "input_text", "text": user_text})
        for img in images or []:
            url = self._resolve_image(img)
            content.append({"type": "input_image", "image_url": url})
        for link in links or []:
            mode, value = self._resolve_file(link)
            content.append({"type": "input_file", mode: value})
        return {"role": "user", "content": content}


def to_responses_parts(role: str, content: Any) -> List[Dict[str, Any]]:
    """
    Map plain strings or legacy parts to Responses API parts with the correct type per role:
      - user/system -> input_text
      - assistant   -> output_text
    """
    if role in ("user", "system"):
        text_type = "input_text"
    elif role == "assistant":
        text_type = "output_text"
    else:
        return []

    parts: List[Dict[str, Any]] = []

    if isinstance(content, str):
        parts.append({"type": text_type, "text": content})
        return parts

    if isinstance(content, list):
        for item in content:
            t = item.get("type")
            if t in ("input_text", "output_text", "text"):
                parts.append({"type": text_type, "text": item.get("text", "")})
            elif t == "input_image":
                if role in ("user", "system"):
                    parts.append({"type": "input_image", "image_url": item.get("image_url")})
            elif t == "input_file":
                if role in ("user", "system"):
                    part = {"type": "input_file"}
                    if "file_id" in item: part["file_id"] = item["file_id"]
                    if "file_url" in item: part["file_url"] = item["file_url"]
                    parts.append(part)
        return parts

    parts.append({"type": text_type, "text": str(content)})
    return parts


def to_chat_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert internal 'Responses-style' messages into Chat Completions messages.
    Supports:
      - role: system/user/assistant
      - text parts -> {"type":"text","text":...}
      - input_image -> {"type":"image_url","image_url": {"url": "..."}}
    Unsupported (will raise): input_file (file_id/file_url parts).
    """
    out: list[dict[str, Any]] = []
    for m in messages:
        role = m.get("role")
        content = m.get("content")

        # Simple string message
        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue

        # Multi-part message
        if isinstance(content, list):
            parts = []
            for p in content:
                t = p.get("type")
                if t in ("input_text", "output_text", "text"):
                    parts.append({"type": "text", "text": p.get("text", "")})
                elif t == "input_image":
                    url = p.get("image_url")
                    parts.append({"type": "image_url", "image_url": {"url": url}})
                elif t == "input_file":
                    # Chat Completions does not support arbitrary file input parts
                    raise ValueError("Chat Completions fallback not supported with 'input_file' parts. Use Responses API.")
            if not parts:
                parts = [{"type": "text", "text": ""}]
            out.append({"role": role, "content": parts})
            continue

        # Fallback
        out.append({"role": role, "content": str(content)})
    return out
