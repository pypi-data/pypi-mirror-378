# Middleware

Serving configures a small, focused middleware stack by default.

## Stack Overview

- `ExceptionMiddleware` — Converts 404s and exceptions into themed error pages
- `ServMiddleware` — Creates a request-scoped DI container branch and manages response headers/status/redirects
- `CSRFMiddleware` — Validates CSRF tokens for mutating HTTP methods

These are always enabled by Serving when constructing the Starlette app.

## ServMiddleware Behavior

- Opens a DI container branch per request and preloads `Request` and response accumulator
- Injects an `AsyncExitStack` into the branched container so request-scoped resources can register async cleanups. The stack is entered before the endpoint runs and is closed automatically when the response finishes.
- Lets helpers like `set_header()`, `set_status_code()`, `set_cookie()`, and `redirect()` affect the live response

## Application Exit Stack

- The application container registers an `AsyncExitStack` with qualifier `"app"`. Pull it via `container.get(AsyncExitStack, qualifier="app")` when you need to tie background tasks or long-lived resources (database pools, message consumers, etc.) to the Starlette app lifecycle.
- Serving wires the stack into Starlette's `shutdown` event, so anything you add with `push_async_callback` or `enter_async_context` is cleaned up automatically during graceful shutdown.

## CSRF

- Applies to `POST`, `PUT`, `PATCH`, and `DELETE`
- Reads `csrf_token` from form body and validates via your `CredentialProvider`
- Returns 400 if invalid

You must configure `auth.config.csrf_secret` in your YAML for CSRF to work. If using time-bound tokens, set `auth.config.csrf_ttl_seconds` to define the validity window.
