import logging
from asyncio import current_task
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
        current_task,
    )

    # !!!: Graceful shutdown doesn't work, connections don't close as expected :(
    async def dispose_engine(app):
        await engine.dispose()

    app = web.Application()
    app.on_cleanup.append(dispose_engine)

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
