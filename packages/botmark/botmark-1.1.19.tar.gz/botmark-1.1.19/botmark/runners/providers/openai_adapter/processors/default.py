from __future__ import annotations
import json, warnings
from typing import Any, Dict, List, Optional, Callable
from contextlib import AsyncExitStack

from botmark.runners import RunResponse, OutputType
from ..client import resolve_client, ClientContext, responses_create, responses_submit_tool_outputs
from ..messages import UserMessageBuilder, to_responses_parts
from ..tools import normalize_tools
from ..schema import JsonSchemaOutputValidator

# Fallback imports
from ..client import chat_completions_create
from ..messages import to_chat_messages


class DefaultProcessor:
    """
    Standard Responses API path (tools, MCP, optional JSON schema) — no local computer loop.
    Falls back to Chat Completions API with clear errors for unsupported features.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = dict(config or {})

    async def run(
        self,
        *,
        input_text: str,
        message_history: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str],
        tools: Optional[Any],
        output_type: Optional[OutputType],
        mcp_servers: Optional[List[Dict[str, Any]]],
        links: Optional[List[Dict[str, Any]]],
        images: Optional[List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> RunResponse:

        # Early exit for custom output
        custom_output_text = kwargs.pop("custom_output_text", None)
        if custom_output_text is not None:
            mh = message_history or []
            filtered_hist = [m for m in mh if isinstance(m, dict) and m.get("role") != "system"]
            all_messages: List[Dict[str, Any]] = []
            all_messages.extend(filtered_hist)
            all_messages.append({"role": "user", "content": input_text})
            all_messages.append({"role": "assistant", "content": custom_output_text})
            return RunResponse(output=custom_output_text, all_messages=all_messages)

        client = resolve_client(self.config)
        if client is None:
            raise RuntimeError("No valid configuration for OpenAI or Azure found!")

        async with AsyncExitStack() as stack:
            await stack.enter_async_context(ClientContext(client))

            # Build messages
            system_text = (system_prompt or self.config.get("system_prompt") or "").strip()
            input_messages: List[Dict[str, Any]] = []
            if system_text:
                input_messages.append({"role": "system", "content": to_responses_parts("system", system_text)})

            mh = message_history or []
            if not isinstance(mh, list):
                raise TypeError("message_history must be a list of messages or None")
            for m in mh:
                if not isinstance(m, dict):
                    continue
                role = m.get("role")
                if role not in ("user", "assistant"):
                    continue
                parts = to_responses_parts(role, m.get("content"))
                if parts:
                    input_messages.append({"role": role, "content": parts})

            builder = UserMessageBuilder(prefer_upload=True)
            user_msg = builder.build_user_parts(
                user_text=input_text,
                images=[i.get("src") for i in images] if images else [],
                links=[l.get("href") for l in links] if links else [],
            )
            input_messages.append(user_msg)

            # Tools + MCP
            tools_out: List[Dict[str, Any]] = []
            tool_registry: Dict[str, Callable[..., Any]] = {}

            local_tools, tool_registry = normalize_tools(tools)
            if local_tools:
                tools_out.extend(local_tools)

            for idx, entry in enumerate(mcp_servers or []):
                if not isinstance(entry, dict):
                    continue
                url = (entry.get("url") or entry.get("href") or "").strip()
                if not url:
                    continue
                tools_out.append({
                    "type": "mcp",
                    "server_label": entry.get("name") or f"mcp_{idx+1}",
                    "server_description": entry.get("description") or f"MCP server {idx+1}",
                    "server_url": url,
                    "require_approval": entry.get("require_approval", "never"),
                    "allowed_tools": entry.get("allowed_tools") or None,
                })

            # Structured outputs
            response_format = None
            output_validator = None
            json_schema_system_hint = None

            if isinstance(output_type, dict):
                response_format = {"type": "json_schema", "json_schema": {"name": "Schema", "schema": output_type, "strict": True}}
                output_validator = JsonSchemaOutputValidator(output_type, strict=True)
                json_schema_system_hint = (
                    "You MUST respond ONLY with JSON that strictly conforms to this JSON Schema:\n"
                    + json.dumps(output_type, ensure_ascii=False)
                )
            elif output_type is not None:
                try:
                    from pydantic import BaseModel as PydBaseModel
                except ImportError:
                    raise ImportError("Install pydantic to use a BaseModel as output_type: pip install pydantic")
                if isinstance(output_type, type) and issubclass(output_type, PydBaseModel):
                    schema = output_type.model_json_schema()  # type: ignore[attr-defined]
                    response_format = {"type": "json_schema", "json_schema": {"name": "Schema", "schema": schema, "strict": True}}
                    output_validator = JsonSchemaOutputValidator(schema, strict=True)
                    json_schema_system_hint = (
                        "You MUST respond ONLY with JSON that strictly conforms to this JSON Schema:\n"
                        + json.dumps(schema, ensure_ascii=False)
                    )
                else:
                    raise TypeError("output_type must be a dict (JSON Schema) or a Pydantic BaseModel class.")

            # Model & params
            model = self.config.get("model") or kwargs.pop("model", None)
            if not model:
                warnings.warn("No model specified; relying on server default.", RuntimeWarning)

            allowed_resp_params = {
                "temperature", "top_p", "max_output_tokens", "stop",
                "frequency_penalty", "presence_penalty", "seed", "user", "timeout", "metadata"
            }
            resp_kwargs = {k: v for k, v in kwargs.items() if k in allowed_resp_params}

            async def _responses_create_with_optional_schema():
                if response_format is not None:
                    try:
                        return await responses_create(
                            client,
                            model=model,
                            input=input_messages,
                            tools=tools_out if tools_out else None,
                            response_format=response_format,
                            **resp_kwargs,
                        )
                    except TypeError:
                        if json_schema_system_hint:
                            input_messages.insert(0, {"role": "system", "content": to_responses_parts("system", json_schema_system_hint)})
                return await responses_create(
                    client,
                    model=model,
                    input=input_messages,
                    tools=tools_out if tools_out else None,
                    **resp_kwargs,
                )

            # --- Try Responses API first ---
            try:
                resp = await _responses_create_with_optional_schema()
            except Exception as e:
                # Prepare Fallback if enabled (default True)
                fallback_enabled = self.config.get("fallback_to_chat_completions", True)
                if not fallback_enabled:
                    raise

                # Validate unsupported features for Chat Completions
                if any(t.get("type") == "mcp" for t in (tools_out or [])):
                    raise RuntimeError("Chat Completions fallback not supported: MCP tools are not available in Chat Completions.")
                if any(t.get("type") == "computer-preview" for t in (tools_out or [])):
                    raise RuntimeError("Chat Completions fallback not supported: computer-preview tools are not available.")
                # Guard against input_file parts
                for m in input_messages:
                    cont = m.get("content")
                    if isinstance(cont, list) and any(p.get("type") == "input_file" for p in cont):
                        raise RuntimeError("Chat Completions fallback not supported with file attachments. Use Responses API.")

                # Build Chat Completions messages
                chat_messages = to_chat_messages(input_messages)

                # Convert "function" tools to Chat Completions tools shape
                cc_tools = None
                if tools_out:
                    cc_tools = []
                    for t in tools_out:
                        if t.get("type") == "function":
                            cc_tools.append({
                                "type": "function",
                                "function": {
                                    "name": t["name"],
                                    "description": t.get("description", ""),
                                    "parameters": t.get("parameters", {"type": "object"}),
                                },
                            })

                # Map params for Chat Completions
                cc_kwargs = {k: v for k, v in kwargs.items() if k in {
                    "temperature", "top_p", "max_tokens", "stop", "frequency_penalty", "presence_penalty", "seed", "user"
                }}

                # Try with response_format if supported
                try:
                    cc_resp = await chat_completions_create(
                        client,
                        model=model,
                        messages=chat_messages,
                        tools=cc_tools,
                        response_format=(response_format if response_format else None),
                        **cc_kwargs
                    )
                except TypeError:
                    # Old SDK/model may not accept response_format: degrade to system-hint
                    if json_schema_system_hint:
                        chat_messages = [{"role": "system", "content": json_schema_system_hint}] + chat_messages
                    cc_resp = await chat_completions_create(
                        client,
                        model=model,
                        messages=chat_messages,
                        tools=cc_tools,
                        **cc_kwargs
                    )

                # Function-calling loop for local Python tools (if any)
                while True:
                    choice = cc_resp.choices[0]
                    msg = choice.message
                    tool_calls = getattr(msg, "tool_calls", None) or []
                    if not tool_calls:
                        break

                    tool_messages = []
                    for tc in tool_calls:
                        name = tc.function.name
                        raw_args = tc.function.arguments or "{}"
                        try:
                            args = json.loads(raw_args)
                        except Exception:
                            args = {}
                        fn = tool_registry.get(name or "")
                        if not fn:
                            output = {"error": f"Tool '{name}' not registered."}
                        else:
                            try:
                                output = fn(**args)
                            except Exception as ex:
                                output = {"error": f"{type(ex).__name__}: {ex}"}
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(output, ensure_ascii=False)
                        })

                    # Continue the chat with tool outputs
                    msgs_plus_tools = chat_messages + [
                        {"role": "assistant", "content": msg.content, "tool_calls": [tc.to_dict() for tc in tool_calls]}
                    ] + tool_messages

                    cc_resp = await chat_completions_create(
                        client,
                        model=model,
                        messages=msgs_plus_tools,
                        tools=cc_tools,
                        **cc_kwargs
                    )

                # Final answer
                final_text = cc_resp.choices[0].message.content or ""
                if output_validator is not None and final_text:
                    output_validator.validate(final_text)

                # Flatten transcript (simple)
                simple_messages: List[Dict[str, Any]] = []
                for m in chat_messages:
                    # Only include plain string contents for the simple transcript
                    content = m.get("content")
                    if isinstance(content, str):
                        simple_messages.append({"role": m.get("role"), "content": content})
                    else:
                        simple_messages.append({"role": m.get("role"), "content": ""})
                simple_messages.append({"role": "assistant", "content": final_text})
                return RunResponse(output=final_text, all_messages=simple_messages)

            # Local python tool loop (Responses API)
            while getattr(resp, "status", None) == "requires_action":
                required = getattr(resp, "required_action", None) or {}
                if required.get("type") != "submit_tool_outputs":
                    break
                tool_calls = (required.get("submit_tool_outputs", {}) or {}).get("tool_calls", []) or []
                tool_outputs: List[Dict[str, str]] = []
                for call in tool_calls:
                    tc_id = call.get("id")
                    fn_info = (call.get("function") or {})
                    name = fn_info.get("name")
                    raw_args = fn_info.get("arguments") or "{}"
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                    fn = tool_registry.get(name or "")
                    if not fn:
                        out = {"error": f"Tool '{name}' not registered."}
                    else:
                        try:
                            out = fn(**args)
                        except Exception as e:
                            out = {"error": f"{type(e).__name__}: {e}"}
                    tool_outputs.append({"tool_call_id": tc_id, "output": json.dumps(out, ensure_ascii=False)})
                resp = await responses_submit_tool_outputs(
                    client,
                    response_id=resp.id,
                    tool_outputs=tool_outputs
                )

            final_text = getattr(resp, "output_text", None) or ""

            if output_validator is not None and final_text:
                output_validator.validate(final_text or "")

            # flatten
            def _as_string_content(m: Dict[str, Any]) -> str:
                c = m.get("content")
                if isinstance(c, str): return c
                if isinstance(c, list):
                    parts = []
                    for item in c:
                        t = item.get("type")
                        if t in ("input_text", "output_text"): parts.append(item.get("text", ""))
                        elif t == "input_image": parts.append(f"[image: {item.get('image_url','')}]")
                        elif t == "input_file":
                            if "file_id" in item: parts.append(f"[file_id: {item['file_id']}]")
                            elif "file_url" in item: parts.append(f"[file_url: {item['file_url']}]")
                    return "\n".join([p for p in parts if p])
                return str(c)

            simple_messages: List[Dict[str, Any]] = []
            for m in input_messages:
                role = m.get("role", "user")
                simple_messages.append({"role": role, "content": _as_string_content(m)})
            simple_messages.append({"role": "assistant", "content": final_text})

            return RunResponse(output=final_text, all_messages=simple_messages)
