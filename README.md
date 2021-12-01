# Arrival test task

## Project installation
Create `.env`-file:
```
DB_NAME=
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
```

Run:
```
alembic upgrade head

python main.py
```

Open: http://127.0.0.1:8080/graphql?query={}


## Development

Writing migrations
```
alembic revision --autogenerate -m "Migration message"
```

## References
1. https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
2. https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
3. https://github.com/graphql-python/graphql-core
4. https://github.com/graphql-python/graphql-server
5. https://github.com/graphql-python/graphql-server/blob/master/docs/aiohttp.md
6. https://github.com/gzzo/graphql-sqlalchemy
7. https://docs.graphene-python.org/projects/sqlalchemy/en/latest/
8. https://github.com/alexisrolland/flask-graphene-sqlalchemy
9. https://spec.graphql.org/October2021
10. https://github.com/jokull/python-ts-graphql-demo

## TODO
- [x] Describe database data structures (SQLAlchemy ORM)
- [x] Set up database migrations environment (alembic)
- [x] Set up http server (aiohttp)
- [ ] Implement API (GraphQL, Python-Graphene):
  - [x] Query, Create, Update Vehicles (not fully, need filters and update)
  - [x] Query, Create, Update Features (not fully, need filters and update)
  - [ ] Query, Create, Update Groups
  - [ ] Query, Create, Update Functions
  - [x] Adding Feature to Vehicle (need to fix read after write)
- [ ] Graceful shutdown (not working :c)
