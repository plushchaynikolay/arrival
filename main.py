import asyncio
import logging

from aiohttp import web
from aiohttp_graphql.graphqlview import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker

from app import config
from app.schemas import schema

logging.basicConfig(level=logging.DEBUG)


async def app() -> web.Application:
    engine = create_async_engine(config.DB_URL)
    session = async_scoped_session(
        sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False),
        asyncio.current_task,
    )

    async def dispose_engine(app):
        for s in session.registry.registry.values():
            await s.close()
        await session.remove()
        await engine.dispose()

    app = web.Application(
        # TODO: close scoped session after every request
        # middlewares=[request_shutdown],
    )
    app.on_shutdown.append(dispose_engine)

    GraphQLView.attach(
        app,
        schema=schema,
        graphiql=True,
        enable_async=True,
        executor=AsyncioExecutor(),
        context={"session": session},
    )

    return app


if __name__ == "__main__":
    web.run_app(app())
