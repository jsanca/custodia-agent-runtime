from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from custodia.app.runtime import Runtime, build_runtime
from custodia.interfaces.api.middleware import RequestIdMiddleware
from custodia.interfaces.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.runtime = build_runtime()
    yield


def create_app(runtime: Runtime | None = None) -> FastAPI:
    app = FastAPI(title="Custodia", lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(router)

    if runtime is not None:
        # Allow tests to inject a pre-built runtime before lifespan runs.
        app.state.runtime = runtime

    return app


app = create_app()
