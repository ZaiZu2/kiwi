### KIWI interview task

### Frontend:

As the application is built as a RestAPI, FE interface was omitted. For manual testing purposes,
OpenAPI docs can be used under: `localhost:8000/docs` route.

### API

Application uses fully async FastAPI - as a bonus, it provides automatic API documentation. Provides
a full input/output validation using Pydantic. API
exposes 2 endpoints:

- `/countries` - allows for bulk importing of `Country name` to `ISO code` mapping, which will be
  fed into the database and used as a source of truth when filtering output in second endpoint
- `/match_country` - endpoint conforming to requirements - allowing to filter country names based on
  attached country code

### Persistance:

Application uses SQLite3 with async aiosqlite driver, but is mostly DB-agnostic. ISO codes and
country names are stored in 2 tables, connected with a many-to-one relationship, where each country
name references a proper ISO code. This is our source of truth.

### Logging:

Application logs requests/errors to stdout and files using a rotating file strategy. Logs into 2
files:
- requests.log - only webserver request data
- internal.log - full server logs - requests/manual logs/errors

### Tests:

Test are performed using Pytest with pytest-asyncio. Fixtures were written to support async test
cases which will be necessary in the future as FastAPI relies on running async code.

Multiple tests were written to check behavior of the endpoints in case of incorrect inputs but also
during expected, successful runs.

### Docker & CI/CD

Implemented Continuous Integration pipeline which runs linting and executes unit tests on every push
to remote. Additionally, on successful push to main, docker image will be built and push to
public [DockerHub](https://hub.docker.com/repository/docker/zaizu2/kiwi) repo.
