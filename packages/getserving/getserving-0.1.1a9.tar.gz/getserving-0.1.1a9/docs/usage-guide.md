# Usage Guide

Serving makes it easy to ship a dependency-injected Starlette application that is configured from a single YAML file and launched with one command. This guide shows how to set up a project, wire the required providers, run the app, and access the utilities that Serving exposes.

## 1. Install & Project Layout

```bash
pip install getserving
```

Create a layout like:

```
my-app/
├─ serving.dev.yaml        # configuration per environment
├─ serving.prod.yaml
├─ templates/              # optional Jinja templates
├─ static/                 # optional static assets
└─ myapp/
   ├─ __init__.py
   ├─ web.py               # routers
   └─ auth.py              # providers
```

Everything the app needs (routers, providers, templates) should live beside the `serving.<env>.yaml` files.

## 2. Configuration File Breakdown

Serving reads `serving.{environment}.yaml` from the working directory. The key sections are:

```yaml
environment: dev  # optional, descriptive only

auth:
  credential_provider: myapp.auth:DevCredentials
  config:
    csrf_secret: "dev-secret"

session:
  session_provider: serving.session:InMemorySessionProvider
  # session_type: optional override for the Session class

templates:
  directory: templates

static:
  mount: /static
  directory: static
  serve: true        # true in dev, omit or set false elsewhere

routers:
  - entrypoint: myapp.web:router
    prefix: "/"
```

**Auth** and **session** are required so Serving can create CSRF tokens and maintain sessions. Templates, static assets, and router metadata are optional but common.

## 3. Define Routers & Endpoints

Routers are plain Starlette routers exported from your package:

```python
# myapp/web.py
from serving.router import Router
from serving.types import JSON

router = Router()

@router.get("/")
async def home() -> JSON:
    return {"message": "Hello, Serving"}
```

When you need dependencies, just annotate them. Serving supports type hints (e.g. `Request`, `Session`) and the `Inject` helper for forms or qualified dependencies.

```python
from bevy import Inject
from serving.forms import Form

class Login(Form, template="login.html"):
    username: str

@router.post("/login")
async def login(form: Inject[Login]) -> JSON:
    # form was parsed and CSRF validated automatically
    return {"user": form.username}
```

## 4. Run the Application

Use the built-in CLI; it picks the configuration, sets up providers, and launches Uvicorn:

```bash
# Start the dev server with hot reload
serv -e dev --reload

# Explicit working directory and port
serv -d /path/to/my-app -e prod --host 0.0.0.0 --port 8080
```

Available flags:

- `-e/--env` – choose the environment (defaults to `prod`).
- `-d/--working-directory` – change directories before loading the config file.
- Any other options are passed straight to Uvicorn (e.g. `--workers`, `--log-level`).

## 5. Providers You Need to Define

### CredentialProvider (Authentication & CSRF)
Serving ships with two credential providers you can use immediately:

- `serving.auth:HMACCredentialProvider` – generates HMAC-signed CSRF & session tokens.
- `serving.auth:TimedHMACCredentialProvider` – adds timestamp + TTL enforcement for expiring CSRF tokens.

Implement the `CredentialProvider` protocol when you need custom behaviour (permissions, user lookup, external services).

```python
# myapp/auth.py
from serving.auth import CredentialProvider

class DevCredentials:
    def __init__(self, *, csrf_secret: str):
        self._secret = csrf_secret

    def has_credentials(self, permissions: set[str]) -> bool:
        return True  # always allow in dev

    def generate_csrf_token(self) -> str:
        return "dev-token"

    def validate_csrf_token(self, token: str) -> bool:
        return token == "dev-token"

    def create_session_token(self) -> str:
        return "session-token"

    def validate_session_token(self, token: str) -> bool:
        return token == "session-token"
```

Point to this class in `serving.dev.yaml` under `auth.credential_provider`. In production you would perform real permission checks and cryptographically secure token generation.

### SessionProvider
- `serving.session:InMemorySessionProvider` is built in and great for development/tests (data kept in-memory per process).
- Implement `SessionProvider` for production; the interface is fully async so you can back it with Redis, databases, etc.

```python
# myapp/session.py
from serving.session import SessionProvider

class RedisSessionProvider(SessionProvider):
    def __init__(self, client):
        self._client = client

    async def create_session(self) -> str:
        token = await self._client.generate_token()
        await self._client.write(token, {})
        return token

    async def update_session(self, token: str, values: dict[str, object]) -> None:
        await self._client.write(token, values)

    async def invalidate_session(self, token: str) -> None:
        await self._client.delete(token)

    async def get_session(self, token: str) -> dict[str, object] | None:
        return await self._client.read(token)
```

Expose it in configuration:

```yaml
session:
  session_provider: myapp.session:RedisSessionProvider
  config:
    url: redis://localhost
```

Inside routes, load and manipulate sessions as:

```python
from serving.session import Session
from serving.types import JSON

@router.get("/me")
async def profile(session: Session) -> JSON:
    user_id = session.get("user_id")
    session["last_seen"] = "just now"
    await session.save()
    return {"user_id": user_id}
```

### Other Providers
- **Templates** – set `templates.directory` and inject `Jinja2Templates` when you need them.
- **Static assets** – configure the `static` section to serve or mount assets.
- **Custom providers** – if you need to register additional services (database pools, HTTP clients), do it at startup inside `Serv.__init__` by calling `serv.container.add(...)` or `serv.registry.add_factory(...)` in your own bootstrap module.

## 6. Accessing Data via Injection

Serving’s injector understands a handful of request-scoped helpers out of the box:

| Inject this...                          | Type hint                                |
|----------------------------------------|------------------------------------------|
| Current request                        | `starlette.requests.Request`
| Response accumulator                   | `serving.response.ServResponse`
| Session                                | `serving.session.Session`
| Credential provider                    | `serving.auth.CredentialProvider`
| Config models                          | Subclass of `serving.config.ConfigModel`
| Form data                              | `Inject[MyForm]` where `MyForm` extends `Form`
| Cookie                                 | `Cookie[str]` (parameter name used by default) or `Annotated[str, Cookie("name")]`
| Header                                 | `Header[str]`
| Query/path params                      | `QueryParam[str]`, `PathParam[int]`, etc.

Examples:

```python
from serving.injectors import Cookie, Header, QueryParam
from serving.types import JSON

@router.get("/dashboard")
async def dashboard(
    session: Session,
    theme: Cookie[str],
    user_agent: Header[str],
    page: QueryParam[int] = 1,
) -> JSON:
    return {
        "user": session.get("user_id"),
        "theme": theme,
        "agent": user_agent,
        "page": page,
    }
```

## 7. Response Utilities

Import from `serving.response` to shape responses without returning new objects:

```python
from serving.response import (
    ServResponse,
    set_header,
    set_status_code,
    set_cookie,
    delete_cookie,
    redirect,
)

@router.post("/login")
async def login(...) -> JSON:
    set_cookie("token", "abc123")
    set_status_code(201)
    return {"ok": True}
```

`ServResponse` (injected automatically) also exposes `.cancel()` and `.response_override` if you need to short-circuit handler execution.

## 8. Events

Serving exposes an `EventManager` so you can broadcast domain events from anywhere in the app.

- Configure handlers under `events` in your YAML. Keys are event names and each value is a list (or single string) of handlers.
- Inject `EventManager` into routes or background tasks and call `await events.trigger("event.name", **payload)`.
- Register additional listeners programmatically with `events.register("event.name", handler, params={...})`.

```yaml
events:
  app.startup:
    - myapp.events:setup_metrics
    - handler: myapp.events:notify_admins
      params:
        channel: "ops"
  user.created:
    - myapp.events:send_welcome_email
```

```python
from serving.events import EventManager
from serving.types import JSON

@router.post("/users")
async def create_user(events: EventManager) -> JSON:
    user = {...}
    await events.trigger("user.created", user=user)
    return user
```

Request-level managers propagate events up to the application manager, so app-wide listeners declared in configuration always run.

## 9. Resource Cleanup with Exit Stacks

Serving manages two async exit stacks so you can register cleanups without wiring your own context managers:

- **Request scoped** – `ServMiddleware` pushes an `AsyncExitStack` into each request branch. Inject it as `AsyncExitStack` when you need to tie resources to the lifetime of the request (temporary files, streaming clients, etc.). Everything you add with `push_async_callback` or `enter_async_context` runs once the response finishes.

```python
from contextlib import AsyncExitStack

@router.post("/upload")
async def upload(stack: AsyncExitStack) -> JSON:
    temp = await stack.enter_async_context(make_tempfile())
    ...  # write to temp
    return {"stored": temp.name}
```

- **Application scoped** – the root container registers an `AsyncExitStack` under the qualifier `"app"`. Grab it once during startup to manage background workers or connections that should close on shutdown.

```python
from contextlib import AsyncExitStack
from serving.serv import APP_EXIT_STACK_QUALIFIER

serv = Serv(...)
app_stack = serv.container.get(AsyncExitStack, qualifier=APP_EXIT_STACK_QUALIFIER)
app_stack.push_async_callback(stop_background_worker)
```

## 10. Testing

- **End-to-end**: create a temporary directory, write a minimal `serving.test.yaml`, instantiate `Serv`, and drive it with `starlette.testclient.TestClient` or HTTPX.
- **Unit tests**: create a registry with `get_registry()`, add specific instances to a container branch, and call functions with `container.call` (sync) or `await container.call` (async).
- Remember to await session and form methods in tests, just like you do in routes.

## 11. Return Types & Rendering

Serving inspects the annotated return type of your endpoint and converts the result automatically. Import the shortcuts from `serving.types`:

```python
from serving.types import JSON, PlainText, HTML, Jinja2

@router.get("/status")
async def status() -> JSON:
    return {"ok": True}

@router.get("/plain")
async def plain() -> PlainText:
    return "All good"

@router.get("/welcome")
async def welcome() -> HTML:
    return "<h1>Hi!</h1>"

@router.get("/home")
async def home() -> Jinja2:
    return "home.html", {"title": "Home"}
```

If you need full control you can still return a Starlette `Response` (StreamingResponse, FileResponse, etc.) or raise an HTTPException.

## 12. Release Workflow (Optional)

1. Update the version in `pyproject.toml`.
2. Build artifacts locally if you want to inspect them (`python -m build`).
3. Push commits, tag (`git tag vX.Y.Z`) and publish a GitHub release. The provided workflow (`.github/workflows/release.yaml`) builds and publishes to PyPI using Trusted Publishing.

With these steps you can go from zero to a fully running Serving application, understand how to plug in your own providers, access request data through injection, and ship confidently.
