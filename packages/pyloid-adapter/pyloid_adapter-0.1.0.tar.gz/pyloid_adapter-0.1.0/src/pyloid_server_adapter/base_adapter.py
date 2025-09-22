"""
Base adapter class for Pyloid server integration.

This module provides a common base class for all Pyloid server adapters,
containing shared functionality and interfaces.
"""

import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional, TYPE_CHECKING, Any

from .context import PyloidContext
from .utils import get_free_port

if TYPE_CHECKING:
    from pyloid import Pyloid
    from pyloid.browser_window import BrowserWindow


class BaseAdapter(ABC):
    """
    Base adapter class for Pyloid application integration.

    This abstract class provides common functionality for integrating Pyloid
    applications with web servers. It handles server lifecycle management,
    context creation, and provides a consistent interface across different
    web frameworks.

    Attributes
    ----------
    host : str
        Server host address. Defaults to "127.0.0.1".
    port : int
        Server port number. Automatically assigned a free port.
    url : str
        Server URL combining host and port.
    pyloid : Pyloid, optional
        The Pyloid application instance. Must be set before use.
    """

    def __init__(self, app: Any, start_function: Callable[[Any, str, int], None]):
        """
        Initialize the base adapter.

        Parameters
        ----------
        app : Any
            The web framework application instance.
        start_function : Callable[[Any, str, int], None]
            Function that starts the server.
        """
        self.app: Any = app
        self.host: str = "127.0.0.1"
        self.port: int = get_free_port()
        self.url: str = f"http://{self.host}:{self.port}"
        self.start_function: Callable[[Any, str, int], None] = start_function
        self.pyloid: Optional["Pyloid"] = None
        self.thread: Optional[threading.Thread] = None

    def get_pyloid_context(self, window_id: Optional[str] = None) -> PyloidContext:
        """
        Create PyloidContext from window ID.

        This method creates a PyloidContext instance with the appropriate
        Pyloid application and window based on the provided window ID.

        Parameters
        ----------
        window_id : str, optional
            The browser window ID to retrieve. If None, window will be None.

        Returns
        -------
        PyloidContext
            Context object containing Pyloid app and window instances.

        Raises
        ------
        RuntimeError
            If pyloid instance is not set before calling this method.
        """
        if self.pyloid is None:
            raise RuntimeError(
                "Pyloid instance is not set. Please call adapter.pyloid = your_pyloid_instance "
                "before processing requests. Frontend should use pyloid-js SDK's fetch method "
                "to automatically include the X-Pyloid-Window-Id header."
            )

        # Initialize window as None - will be set if valid window_id is found
        window: Optional["BrowserWindow"] = None
        if window_id:
            try:
                window = self.pyloid.get_window_by_id(window_id)
                if window is None:
                    print(f"Warning: Window with ID '{window_id}' not found in Pyloid application")
            except Exception as e:
                print(f"Error retrieving window '{window_id}': {e}")
                # Continue with window = None
        else:
            # Log when window_id header is missing
            print("Warning: X-Pyloid-Window-Id header not found in request. "
                  "Frontend should use pyloid-js SDK's fetch method to include this header. "
                  "Example: pyloid.fetch('/api/endpoint') instead of native fetch()")

        return PyloidContext(pyloid=self.pyloid, window=window)

    def start(self) -> None:
        """
        Start the server.

        This method calls the configured start_function to actually start
        the server. The start_function is responsible for the actual server startup.

        Notes
        -----
        This method will block if using a synchronous start function.
        For non-blocking operation, use the run() method instead.
        """
        self.start_function(self.app, self.host, self.port)

    def run(self) -> None:
        """
        Run the server in a background thread.

        This method creates a daemon thread that runs the server startup process.
        The server will run in the background, allowing the main application to
        continue executing.

        Notes
        -----
        - The thread is set as daemon=True, so it won't prevent program exit
        - Server logs and output will be printed to console
        - Use this for development; consider production servers for deployment
        """
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()

    @abstractmethod
    def setup_cors(self) -> None:
        """
        Set up CORS configuration for the web framework.

        This method should be implemented by subclasses to configure
        CORS settings appropriate for their web framework.
        """
        pass
