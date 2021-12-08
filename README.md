# Arrival test task

## Project installation

> 0. Run postgres in docker
> 
> ```
> docker run -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=arrival -d --restart=unless-stopped postgres:12.6
> ```

1. Create `.env`-file, for example:
```
DB_NAME=arrival
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
```

2. Run:
```
alembic upgrade head

python main.py
```

3. Open: http://127.0.0.1:8080/graphql?query={}


## Development

Writing migrations
```
alembic revision --autogenerate -m "Migration message"
```

## Examples
### Query all vehicles and features
```qraphql 
{
  allVehicles {
    edges {
      node {
        pk
        name
        features {
          edges {
            node {
              pk
              name
            }
          }
        }
      }
    }
  }
  allFeatures {
    edges {
      node {
        pk
        name
      }
    }
  }
}
```
```json
{
  "data": {
    "allVehicles": {
      "edges": []
    },
    "allFeatures": {
      "edges": []
    }
  }
}
```

### Create new vehicle and feature
```graphql
mutation {
  createVehicle(name: "test vehicle 1") {
    ok
    vehicle {
      pk
      name
    }
  }
  createFeature(name: "test feature 1") {
    ok
    feature {
      pk
      name
    }
  }
}
```
```json
{
  "data": {
    "createVehicle": {
      "ok": true,
      "vehicle": {
        "pk": 1,
        "name": "test vehicle 1"
      }
    },
    "createFeature": {
      "ok": true,
      "feature": {
        "pk": 1,
        "name": "test feature 1"
      }
    }
  }
}
```

### Add feature to vehicle
```graphql
mutation {
  addFeature(vehicleId: 1, featureId: 1) {
    ok
    vehicle {
      pk
      name
      features {
        edges {
          node {
            pk
            name
          }
        }
      }
    }
  }
}
```
```json
{
  "data": {
    "addFeature": {
      "ok": true,
      "vehicle": {
        "pk": 1,
        "name": null,
        "features": {
          "edges": [
            {
              "node": {
                "pk": 1,
                "name": "test feature 1"
              }
            }
          ]
        }
      }
    }
  }
}
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
  - [x] Query, Create, Update Vehicles (need filters and update)
  - [x] Query, Create, Update Features (need filters and update)
  - [ ] ~~Query, Create, Update Groups~~
  - [ ] ~~Query, Create, Update Functions~~
  - [x] Adding Feature to Vehicle
- [x] Graceful shutdown (need improvement)
