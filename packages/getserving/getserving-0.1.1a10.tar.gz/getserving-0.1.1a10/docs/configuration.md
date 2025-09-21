# Configuration

Serving loads a single YAML file named `serving.{environment}.yaml` from your working directory. The environment defaults to `prod` but can be set via `SERV_ENVIRONMENT` or the CLI `-e/--env` flag.

## File Location

- Working directory: current process directory or `--working-directory` (`-d`) passed to `serv`
- Filename pattern: `serving.dev.yaml`, `serving.prod.yaml`, etc.

## Top-Level Keys

- `environment`: Optional descriptive value inside your YAML
- `templates`: Configure template directory for Jinja2
- `theming`: Configure error page templates
- `auth`: Configure authentication and CSRF
- `session`: Configure session provider and mapping type
- `routers`: Declaratively wire routers and permissions
 - `static`: Configure static asset serving (dev only)

## Templates

```yaml
templates:
  directory: templates  # default
```

## Theming (Error Pages)

```yaml
theming:
  # Map specific codes to template files under your templates dir
  error_templates:
    "404": errors/404.html
    "500": errors/500.html
  # Fallback template used when a specific code template is not provided
  default_error_template: errors/error.html
```

See [Error Handling & Theming](error-handling.md) for details and the fallback template used by Serving.

## Authentication

```yaml
auth:
  credential_provider: myapp.auth:MyProvider  # module:ClassName or module:attribute
  config:
    csrf_secret: "change-me-long-random-string"
    csrf_ttl_seconds: 3600                     # optional; TTL for time-bound CSRF tokens
```

- `credential_provider` must resolve to a class implementing the `CredentialProvider` protocol (see ./authentication.md)
- `config` (optional) is a dictionary passed through to the provider constructor as keyword args
- For built-in CSRF providers, set `csrf_secret` (required) and optionally `csrf_ttl_seconds` under `auth.config`

## Routers

## Sessions

```yaml
session:
  session_provider: serving.session:InMemorySessionProvider
  session_type: serving.session:Session  # optional
  config: {}
```

- `session_provider` must implement the `SessionProvider` protocol
- `session_type` defaults to the built-in `Session` mapping
- `config` is passed as keyword args to your provider constructor

See [Sessions](sessions.md) for details.

## Events

Register event handlers that the `EventManager` will invoke when you trigger an event.

```yaml
events:
  app.startup:
    - handler: myapp.events:log_startup
      params:
        label: "startup"
  app.shutdown:
    - handler: myapp.events:log_shutdown
      params:
        label: "shutdown"
  user.created:
    - myapp.events:send_welcome_email
  request.finish:
    - handler: myapp.events:collect_metrics
      params:
        label: "finish"
```

- Entries are keyed by event name; each value can be a list of handlers or a single handler string.
- Each handler may be a string (`module:callable`) or a mapping with `handler` and optional `params` for keyword arguments.
- Built-in events emitted by Serving:
  - `app.startup` — fired during the Starlette startup sequence.
  - `app.shutdown` — fired during the shutdown sequence before exit stacks close.
  - `request.start` — fired before a request handler begins execution.
  - `request.finish` — fired after a response is produced (response may be `None` if an error occurs).

Read the usage guide for examples of triggering events from within routes.

## Static Assets (Dev)

Serving mounts a named static route so you can use Starlette’s `url_for('static', path='...')` in templates across all environments.

```yaml
static:
  mount: /static       # URL path prefix
  directory: static    # folder on disk (relative to working dir)
  name: static         # route name for url_for; default "static"
  serve: true          # if omitted: true in dev, false otherwise
```

- In `dev`/`development`, files are served from disk by default (`serve: true`)
- In other environments, `serve` defaults to `false` (URL generation only); set `serve: true` to have the app serve files
- Regardless of `serve`, the named route is mounted so `url_for('static', ...)` always works

```yaml
routers:
  - entrypoint: myapp.web:app  # module:variable pointing to a serving.router.Router instance
    prefix: "/api"            # optional, mounts routes under this path
    routes:
      - path: "/users/{user_id}"
        method: GET            # optional, defaults to GET in code when declaring
        permissions:           # optional, required permissions checked by your provider
          - admin
      - path: "/"
```

- `entrypoint` points to a Python module and attribute (a `Router` instance)
- `routes` allow adding per-path metadata (e.g., permissions); methods are taken from your decorator when you register

## Multiple Routers

You can declare more than one router. Serving will mount each, honoring optional `prefix` values, and wrap endpoints with authentication and response handling.

## Validation & Errors

- If the working directory does not exist, a `ConfigurationError` is raised
- If the file for the chosen environment is missing, a `ConfigurationError` is raised
- If `auth` is missing or invalid, an `AuthConfigurationError` is raised during startup
