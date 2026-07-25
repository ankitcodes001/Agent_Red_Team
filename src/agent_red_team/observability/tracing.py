"""Tracing setup — one trace per attack, one span per pipeline step.

Spans: bandit.pick, payload.gen, proxy.inject, target.think, target.tool_call,
eval. Each carries latency and token cost. The agents observe themselves; the
same stack that is the product's domain is its meta-layer.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


def init_tracing(service_name: str = "agent-red-team") -> None:
    """Configure the OpenTelemetry provider and Langfuse exporter."""
    raise NotImplementedError


@contextmanager
def span(name: str, **attributes: object) -> Iterator[None]:
    """Context manager that records a span for a pipeline step."""
    raise NotImplementedError
    yield  # pragma: no cover
