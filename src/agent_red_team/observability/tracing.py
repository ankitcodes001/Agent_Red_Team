"""Tracing setup — one trace per attack, one span per pipeline step.

Spans: bandit.pick, payload.gen, proxy.inject, target.think, target.tool_call,
eval. Each carries latency and token cost. The agents observe themselves; the
same stack that is the product's domain is its meta-layer.

Tracing is best-effort: ``span`` always works (an unconfigured OpenTelemetry
falls back to a no-op span), and ``init_tracing`` never raises — a telemetry
problem must never break a campaign.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from opentelemetry import trace


def init_tracing(service_name: str = "agent-red-team") -> None:
    """Configure the OpenTelemetry provider and OTLP (Langfuse) exporter.

    No-op unless ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set — so a plain local run
    stays silent (no collector to connect to) instead of spamming export
    errors. Point that env var at your Langfuse/OTLP endpoint to enable it.
    Any setup failure is swallowed — telemetry is optional.
    """
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
    except Exception:  # pragma: no cover - telemetry is best-effort
        pass


@contextmanager
def span(name: str, **attributes: object) -> Iterator[None]:
    """Context manager that records a span for a pipeline step."""
    tracer = trace.get_tracer("agent-red-team")
    with tracer.start_as_current_span(name) as current:
        for key, value in attributes.items():
            current.set_attribute(key, str(value))
        yield
