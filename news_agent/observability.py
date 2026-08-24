import logging

from fastapi import FastAPI
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from phoenix.otel import register

from news_agent.config import (
    ENABLE_OBSERVABILITY,
    PHOENIX_ENDPOINT,
    PHOENIX_PROJECT_NAME,
)

logger = logging.getLogger(__name__)

_instrumented = False


def setup_observability(app: FastAPI) -> None:
    """Wire up tracing to a local Phoenix instance (run separately via `phoenix serve`).

    Disabled entirely when NEWS_AGENT_ENABLE_OBSERVABILITY=false (tests/CI set this,
    since there's no Phoenix collector to send spans to there). When enabled, uses
    batched async export so a request never blocks waiting on the collector, even
    if Phoenix isn't running.
    """
    global _instrumented
    if _instrumented or not ENABLE_OBSERVABILITY:
        return

    tracer_provider = register(
        endpoint=PHOENIX_ENDPOINT,
        project_name=PHOENIX_PROJECT_NAME,
        batch=True,
        verbose=False,
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    _instrumented = True
    logger.info("Observability wired up, sending traces to %s", PHOENIX_ENDPOINT)
