from envparse import env

env.read_envfile(".env")


DB_URL = (
    "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
        DB_NAME=env.str("DB_NAME", default="arrival"),
        DB_HOST=env.str("DB_HOST", default="localhost"),
        DB_PORT=env.str("DB_PORT", default=5432),
        DB_USER=env.str("DB_USER", default="postgres"),
        DB_PASSWORD=env.str("DB_PASSWORD", default="postgres"),
    )
)
