import importlib
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass
from inspect import get_annotations
from pathlib import Path
from typing import Generator

import starlette.responses
from bevy import get_container, get_registry
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount, Route
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

import serving.types
from serving.auth import AuthConfig, AuthConfigurationError, CredentialProvider
from serving.config import Config, ConfigModel
from serving.error_handler import ErrorHandler
from serving.exception_handlers import http_exception_handler, general_exception_handler, not_found_handler
from serving.exception_middleware import ExceptionMiddleware
from serving.injectors import (
    handle_config_model_types,
    handle_cookie_types,
    handle_header_types,
    handle_path_param_types,
    handle_query_param_types,
    handle_form_types,
    handle_session_types,
    handle_session_param_types,
)
from serving.router import RouterConfig, Router
from serving.session import SessionConfig, SessionProvider, Session
from serving.serv_middleware import ServMiddleware
from serving.csrf_middleware import CSRFMiddleware
from serving.events import EventManager


APP_EXIT_STACK_QUALIFIER = "app"


@dataclass
class TemplatesConfig(ConfigModel, model_key="templates"):
    """Configuration for templates."""
    directory: str = "templates"


@dataclass
class StaticConfig(ConfigModel, model_key="static"):
    """Configuration for static asset serving in development.

    - mount: URL path prefix to mount static files under (e.g., "/static")
    - directory: Filesystem directory containing static assets
    - name: Route name used for `url_for(name, path=...)` compatibility (default: "static")
    """
    mount: str = "/static"
    directory: str = "static"
    name: str = "static"
    # Whether the app should serve assets itself. If None, defaults
    # to True in dev and False otherwise.
    serve: bool | None = None

    @classmethod
    def from_dict(cls, config: dict) -> "StaticConfig | None":
        # If the key is present with no options, treat as absent
        if not config:
            return None
        return cls(**config)


@dataclass
class ThemingConfig(ConfigModel, model_key="theming"):
    """Configuration for theming and custom error pages."""
    error_templates: dict[str, str] | None = None  # Maps error codes to template paths
    default_error_template: str | None = None  # Default template for all errors


class ConfigurationError(Exception):
    """Raised when configuration cannot be loaded."""
    def __init__(self, message: str, config_filename: str, working_directory: Path):
        super().__init__(message)
        self.config_filename = config_filename
        self.working_directory = working_directory


class Serv:
    def __init__(
        self,
        working_directory: str | Path | None = None,
        environment: str | None = None,
    ):
        """Initialize Serving application with configuration and dependency injection.
        
        Args:
            working_directory: Path to working directory where config files are located.
                - str: Path to the working directory
                - Path: Path object to working directory
                - None: Uses current working directory (default)
            environment: Environment name (e.g., 'dev', 'prod'). If not provided,
                        uses SERV_ENVIRONMENT env var, defaulting to 'prod'
        
        Raises:
            ConfigurationError: When config file cannot be found or loaded
        """
        self.registry = get_registry()

        # Register the config model handler
        handle_config_model_types.register_hook(self.registry)
        handle_cookie_types.register_hook(self.registry)
        handle_header_types.register_hook(self.registry)
        handle_path_param_types.register_hook(self.registry)
        handle_query_param_types.register_hook(self.registry)
        handle_form_types.register_hook(self.registry)
        handle_session_types.register_hook(self.registry)
        handle_session_param_types.register_hook(self.registry)

        self.container = self.registry.create_container()
        self.event_manager = EventManager(self.container)
        self._app_exit_stack = AsyncExitStack()
        self.container.add(AsyncExitStack, self._app_exit_stack, qualifier=APP_EXIT_STACK_QUALIFIER)
        self.container.add(EventManager, self.event_manager)
        with self.container:
            # Determine environment
            self.environment = self._get_environment(environment)
            self.working_directory = working_directory

            # Load configuration (will raise if not found)
            self._load_configuration(working_directory)

            # Configure authentication
            self._configure_auth()

            # Configure sessions (optional)
            self._configure_session()

            # Configure events (optional)
            self._configure_events()

            self.templates = Jinja2Templates(directory=self.container.get(TemplatesConfig).directory)
            self.container.add(self.templates)

            # Configure error handler with theming support
            try:
                theming_config = self.container.get(ThemingConfig)
            except (KeyError, TypeError):
                theming_config = None

            self.error_handler = ErrorHandler(
                theming_config=theming_config,
                templates=self.templates if theming_config else None
            )

            self.app = Starlette(
                routes=self._load_routes(),
                middleware=[
                    Middleware(ExceptionMiddleware, serv=self),
                    Middleware(ServMiddleware, serv=self),
                    Middleware(CSRFMiddleware),
                ],
                exception_handlers={
                    HTTPException: http_exception_handler,
                    404: not_found_handler,
                    500: general_exception_handler,
                },
            )

        self.app.add_event_handler("shutdown", self._app_exit_stack.aclose)

        # Store serv instance in app state for exception handlers
        self.app.state.serv = self

    def _configure_auth(self) -> None:
        """Configure authentication based on the configuration."""
        config_path = self.get_config_path(self.working_directory, self.environment)
        try:
            auth_config = self.container.get(AuthConfig)
        except TypeError as e:
            raise AuthConfigurationError(
                f"Authentication is not correctly configured", config_path
            ) from e
        except AuthConfigurationError as e:
            e.set_config_path(config_path)
            raise

        # Instantiate the credential provider with provider-specific config kwargs
        kwargs = auth_config.config or {}
        provider = self.container.call(auth_config.credential_provider, **kwargs)
        self.container.add(CredentialProvider, provider)

    def _configure_session(self) -> None:
        """Configure session provider and register session type (if configured)."""
        try:
            session_config = self.container.get(SessionConfig)
        except (KeyError, ValueError, TypeError):
            # No sessions configured
            return

        # Instantiate the session provider with provider-specific config kwargs.
        # Rely on DI for dependencies like CredentialProvider.
        kwargs = dict(session_config.config or {})
        provider = self.container.call(session_config.session_provider, **kwargs)
        self.container.add(SessionProvider, provider)

        # Session type will be provided on-demand via injector; no need to pre-register

    def _configure_events(self) -> None:
        """Configure application-level event handlers from configuration."""
        events_config = self.config.get("events") if hasattr(self, "config") else []
        handlers = EventManager.parse_config(events_config or [])
        for event, specs in handlers.items():
            for spec in specs:
                self.event_manager.register(event, spec)

    def _load_configuration(self, working_directory: str | Path | None) -> None:
        """Load configuration from the specified working directory or in the current working directory. Which config
        file is loaded is determined by the environment setting..
        
        Raises:
            ConfigurationError: When config file cannot be found or loaded
        """
        config_path = self.get_config_path(working_directory, self.environment)

        # Load the configuration
        try:
            self.config = Config.load_config(config_path.name, str(config_path.parent))
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from '{config_path}': {e}",
                config_path.name,
                config_path.parent,
            ) from e

        # Add Config to container for dependency injection
        self.container.add(self.config)

    def _load_routes(self) -> list[Route]:
        routes = []
        try:
            routers = self.container.get(list[RouterConfig])
        except (KeyError, ValueError):
            # No routers configured, return empty list
            routers = []

        # Add configured routers first
        for router in routers:
            if router.prefix:
                routes.append(Mount(router.prefix, routes=list(self._build_routes(router))))
            else:
                routes.extend(self._build_routes(router))

        # Always mount a named static route so url_for('static', ...) works in all envs.
        # In dev: serve files from disk. In other envs: mount an empty app as a placeholder
        # so that reverse proxies/CDNs can serve assets while templates still use url_for.
        try:
            static_config = self.container.get(StaticConfig)
        except KeyError:
            # No static section configured
            static_config = None

        if static_config and static_config.mount:
            is_dev = getattr(self, 'environment', 'prod') in ('dev', 'development')
            serve_assets = static_config.serve if static_config.serve is not None else is_dev

            # Resolve directory relative to working directory if needed
            directory = static_config.directory
            try:
                base_dir = self.get_config_path(self.working_directory, self.environment).parent
            except Exception:
                base_dir = Path.cwd()
            dir_path = Path(directory)
            if not dir_path.is_absolute():
                dir_path = base_dir / dir_path

            # When serving assets directly, set Cache-Control on all responses under the mount.
            static_app = StaticFiles(directory=str(dir_path)) if serve_assets else Starlette()
            routes.append(
                Mount(
                    static_config.mount,
                    app=static_app,
                    name=static_config.name,
                )
            )

        return routes

    def _build_routes(self, router_config: RouterConfig) -> Generator[Route, None, None]:
        router = self._import_router(*router_config.entrypoint.split(":", 1))
        route_configs = {
            route.path: route
            for route in router_config.routes
        }
        for route in router.routes:
            if isinstance(route, Route):
                route = Route(
                    route.path,
                    self._wrap_endpoint(route.endpoint, route_configs.get(route.path)),
                    methods=route.methods
                )

            yield route

    def _import_router(self, module_name: str, router_name: str) -> Router:
        module = importlib.import_module(module_name)
        return getattr(module, router_name)

    def _wrap_endpoint(self, endpoint, route_config):
        async def wrapped_endpoint(request):
            permissions = set() if route_config is None else route_config.permissions
            credential_provider = get_container().get(CredentialProvider)
            if not get_container().call(credential_provider.has_credentials, permissions):
                # Only show permission details in development mode
                details = None
                if hasattr(self, 'environment') and self.environment in ('dev', 'development'):
                    details = f"Required permissions: {permissions}" if permissions else "Authentication required"

                return self.error_handler.render_error(
                    request,
                    error_code=401,
                    error_message="Unauthorized",
                    details=details
                )

            result = await get_container().call(endpoint, **request.path_params)
            match get_annotations(endpoint)["return"]:
                case serving.types.PlainText:
                    return starlette.responses.PlainTextResponse(result)

                case serving.types.JSON:
                    return starlette.responses.JSONResponse(result)

                case serving.types.HTML:
                    return starlette.responses.HTMLResponse(result)

                case serving.types.Jinja2:
                    return self.templates.TemplateResponse(
                        request,
                        result[0],  # Template file
                        result[1],  # Context data
                    )

                case _ if isinstance(result, starlette.responses.Response):
                    return result

                case _:
                    raise ValueError(f"Unsupported return type: {type(result)}")

        return wrapped_endpoint

    @staticmethod
    def get_config_path(working_directory: str | Path | None, environment: str | None) -> Path:
        match working_directory:
            case str():
                working_directory = Path(working_directory)
            case Path():
                pass
            case None:
                working_directory = Path.cwd()
            case _:
                raise ValueError(f"Invalid working directory: {working_directory}")

        environment = Serv._get_environment(environment)
        config_filename = f"serving.{environment}.yaml"
        if not working_directory.exists():
            raise ConfigurationError(
                f"Configuration file '{config_filename}' not found, the working directory {working_directory} does not "
                f"exist or is not a valid path. Confirm that the working directory is set correctly and that it exists.",
                config_filename,
                working_directory,
            )

        config_path = working_directory / config_filename
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file '{config_path}' not found, confirm that the environment '{environment}' is set "
                f"correctly and that the file exists.",
                config_filename,
                working_directory,
            )

        return config_path

    @staticmethod
    def _get_environment(environment: str | None) -> str:
        """Determine the environment based on the provided environment name or SERV_ENVIRONMENT env var.

        Args:
            environment: Environment name (e.g., 'dev', 'prod'). If not provided, uses SERV_ENVIRONMENT env var,
                defaulting to 'prod'

        Returns:
            str: Environment name
        """
        if environment:
            return environment

        return os.environ.get("SERV_ENVIRONMENT", "prod")
