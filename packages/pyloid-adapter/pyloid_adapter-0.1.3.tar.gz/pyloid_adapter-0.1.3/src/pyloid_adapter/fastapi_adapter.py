from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from .base_adapter import BaseAdapter
from .context import PyloidContext
from typing import Callable, Annotated

class FastAPIAdapter(BaseAdapter):
    """
    FastAPI adapter for Pyloid application integration.

    This adapter class serves as the main integration point between Pyloid applications
    and FastAPI web servers. It provides FastAPI dependency injection for Pyloid
    context and manages the server lifecycle.

    The adapter automatically configures CORS to allow all origins by default for
    seamless integration with web applications.

    The adapter supports FastAPI's dependency injection system for context injection.
    """

    def __init__(self, app: FastAPI, start_function: Callable[[FastAPI, str, int], None]):
        """
        Initialize the FastAPI adapter.

        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance to integrate with.
        start_function : Callable[[FastAPI, str, int], None]
            Function that starts the server. Should handle app, host, port parameters.
        """
        super().__init__(app, start_function)
        
        self.app: FastAPI = app
        
        # Add CORS middleware with default settings (allow all origins)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins by default
            allow_credentials=True,
            allow_methods=["*"],  # Allow all methods
            allow_headers=["*"],  # Allow all headers
        )
            
    def get_pyloid_context(self, request: Request) -> PyloidContext:
        """
        Create PyloidContext from an HTTP request.

        This method extracts the window ID from the request headers and creates
        a PyloidContext instance with the appropriate Pyloid application and window.

        Parameters
        ----------
        request : Request
            The FastAPI Request object containing headers and metadata.

        Returns
        -------
        PyloidContext
            Context object containing Pyloid app and window instances.
        """
        window_id = request.headers.get("X-Pyloid-Window-Id")
        return super().get_pyloid_context(window_id)

    def pyloid_context(self, request: Request) -> PyloidContext:
        """
        FastAPI dependency function for PyloidContext injection.

        This function can be used directly with FastAPI's Depends() system
        to automatically inject PyloidContext into route handlers.

        Usage:
        ```python
        @app.get("/endpoint")
        async def handler(ctx: PyloidContext = Depends(adapter.get_pyloid_dependency)):
            # ctx is automatically injected
            pass
        ```

        This approach leverages FastAPI's built-in dependency injection system
        for better performance and cleaner code.
        """
        return self.get_pyloid_context(request)

    def setup_cors(self) -> None:
        """CORS is already set up in __init__, so this is a no-op."""
        pass