"""OpenRouter API client for making LLM requests."""

import json
import httpx
from typing import List, Dict, Any, Optional
from .config import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    TAVILY_API_KEY,
    TAVILY_API_URL,
)


async def tavily_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Execute a Tavily web search and return a compact result dict."""
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not configured"}

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max(1, min(int(max_results or 5), 10)),
        "search_depth": "basic",
        "include_answer": True,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(TAVILY_API_URL, json=payload)
            r.raise_for_status()
            data = r.json()
            return {
                "answer": data.get("answer"),
                "results": [
                    {
                        "title": x.get("title"),
                        "url": x.get("url"),
                        "content": x.get("content"),
                    }
                    for x in (data.get("results") or [])
                ],
            }
    except Exception as e:
        return {"error": f"tavily_search failed: {e}"}


async def _dispatch_tool_call(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool call and return a JSON string for the tool message."""
    if name == "tavily_search":
        result = await tavily_search(
            query=arguments.get("query", ""),
            max_results=arguments.get("max_results", 5),
        )
    else:
        result = {"error": f"unknown tool: {name}"}
    return json.dumps(result)[:60000]


async def query_model(
    model: str,
    messages: List[Dict[str, Any]],
    timeout: float = 180.0,
    tools: Optional[List[Dict[str, Any]]] = None,
    response_format: Optional[Dict[str, Any]] = None,
    max_tool_iterations: int = 6,
) -> Optional[Dict[str, Any]]:
    """Query a model via OpenRouter with optional tool-calling loop."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    working_messages = list(messages)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            for _ in range(max_tool_iterations):
                payload: Dict[str, Any] = {
                    "model": model,
                    "messages": working_messages,
                }
                if tools:
                    payload["tools"] = tools
                if response_format:
                    payload["response_format"] = response_format

                r = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                message = data["choices"][0]["message"]

                tool_calls = message.get("tool_calls") or []
                if not tool_calls:
                    return {
                        "content": message.get("content"),
                        "reasoning_details": message.get("reasoning_details"),
                    }

                working_messages.append({
                    "role": "assistant",
                    "content": message.get("content") or "",
                    "tool_calls": tool_calls,
                })

                for tc in tool_calls:
                    fn = tc.get("function", {}) or {}
                    name = fn.get("name", "")
                    try:
                        args = json.loads(fn.get("arguments") or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    tool_result = await _dispatch_tool_call(name, args)
                    working_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id"),
                        "content": tool_result,
                    })

            return {
                "content": "Error: tool-call loop exceeded max iterations.",
                "reasoning_details": None,
            }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_personalities_parallel(
    model: str,
    personalities: List[Dict[str, str]],
    user_messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    response_format: Optional[Dict[str, Any]] = None,
) -> Dict[str, Optional[Dict[str, Any]]]:
    """Query the same model with different personality system prompts in parallel."""
    import asyncio

    async def query_with_personality(personality):
        messages = [
            {"role": "system", "content": personality["system_prompt"]},
            *user_messages,
        ]
        return await query_model(
            personality.get("model") or model,
            messages,
            tools=tools,
            response_format=response_format,
        )

    tasks = [query_with_personality(p) for p in personalities]
    responses = await asyncio.gather(*tasks)
    return {p["id"]: response for p, response in zip(personalities, responses)}
