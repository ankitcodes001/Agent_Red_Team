"""MCP man-in-the-middle proxy.

Forwards tool *requests* untouched to the real server; poisons tool *results*
on the way back using ``injector.inject``. Also records every tool call so the
oracle can watch for forbidden calls. The target agent points its tool URL here
instead of at the real server — a one-line config change.
"""

from __future__ import annotations

from collections.abc import Callable

from agent_red_team.contracts import Payload


class MCPProxy:
    """Sits between the target agent and the real MCP tool server."""

    def __init__(self, upstream_url: str) -> None:
        self.upstream_url = upstream_url
        self._active_payload: Payload | None = None
        self._tool_calls: list[str] = []

    def arm(self, payload: Payload) -> None:
        """Set the payload to inject into the next matching tool result."""
        self._active_payload = payload

    @property
    def tool_calls(self) -> list[str]:
        """Tool names the agent called during the last attempt (for the oracle)."""
        return list(self._tool_calls)

    def serve(self, on_request: Callable[[str, dict[str, object]], str] | None = None) -> None:
        """Start the proxy server loop."""
        raise NotImplementedError
