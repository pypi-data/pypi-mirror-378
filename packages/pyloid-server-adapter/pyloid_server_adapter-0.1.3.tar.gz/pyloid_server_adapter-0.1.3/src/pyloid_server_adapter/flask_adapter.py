"""
Pyloid Server Adapter for Flask

This module provides a Flask adapter that enables seamless integration between Pyloid
applications and Flask web servers. It allows Pyloid applications to access their
context (including the Pyloid instance and current browser window) within Flask
route handlers through decorator-based injection.

The adapter handles:
- Pyloid instance management and window registration
- Automatic context creation from HTTP requests
- Decorator-based context injection
- Server lifecycle management (start/stop)

Key Components:
- PyloidContext: Data class holding Pyloid application and window context
- FlaskAdapter: Main adapter class that manages the integration

Frontend Integration:
    Frontend applications should use pyloid-js SDK's fetch method instead of native fetch()
    to automatically include the X-Pyloid-Window-Id header. This ensures proper context
    injection in backend route handlers.

Usage:
    adapter = FlaskAdapter(app=app, start_function=start_server)
    adapter.pyloid = pyloid_instance  # Set the Pyloid instance
    # Use decorator to access context in routes
"""

from flask import Flask, request
from .utils import get_free_port
from typing import Callable, Optional
from typing import TYPE_CHECKING
import inspect
from functools import wraps
import threading

if TYPE_CHECKING:
    from pyloid import Pyloid
    
from .context import PyloidContext



class FlaskAdapter:
    """
    Flask adapter for Pyloid application integration.
    
    This adapter class serves as the main integration point between Pyloid applications
    and Flask web servers. It provides decorator-based mechanisms for injecting Pyloid
    context into route handlers.
    
    The adapter supports context injection using @adapter.pyloid_context decorator.
    
    Attributes
    ----------
    app : Flask
        The Flask application instance to integrate with.
    host : str
        Server host address. Defaults to "127.0.0.1".
    port : int
        Server port number. Automatically assigned a free port.
    start_function : Callable[[str, int], None]
        Function to start the server with (app, host, port).
    pyloid : Pyloid, optional
        The Pyloid application instance. Must be set before use.
    
    Examples
    --------
    ```python
    adapter = FlaskAdapter(app=my_app, start_function=start_server)
    adapter.pyloid = pyloid_app
    # Now ready to use context injection in routes
    ```
    """
    
    def __init__(self, app: Flask, start_function: Callable[[str, int], None]):
        """
        Initialize the Flask adapter.
        
        Parameters
        ----------
        app : Flask
            The Flask application instance to integrate with.
        start_function : Callable[[str, int], None]
            Function that starts the server. Should accept (app, host, port) parameters.
        """
        self.app: Flask = app
        self.host: str = "127.0.0.1"
        self.port: int = get_free_port()
        self.start_function: Callable[[str, int], None] = start_function
        
        # Pyloid-related attributes for context management
        self.pyloid: Optional["Pyloid"] = None

    def get_pyloid_context(self) -> PyloidContext:
        """
        Create PyloidContext from current Flask request.
        
        This method extracts the window ID from the current request headers and creates
        a PyloidContext instance with the appropriate Pyloid application and window.
        
        The method looks for the 'X-Pyloid-Window-Id' header in the request to
        determine which browser window the request is associated with. If the
        header is present, it attempts to retrieve the corresponding window from
        the Pyloid application. If the header is missing or the window is not found,
        the window attribute will be None.
        
        Returns
        -------
        PyloidContext
            Context object containing Pyloid app and window instances.
            
        Raises
        ------
        RuntimeError
            If pyloid instance is not set before calling this method.
            
        Notes
        -----
        - Requires pyloid attribute to be set before calling
        - Window lookup is performed via pyloid.get_window_by_id()
        - If window_id header is missing, window will be None
        - If window_id is invalid, window will be None (method may raise exception)
        - Frontend should use pyloid-js SDK's fetch method to include X-Pyloid-Window-Id header
        """
        if self.pyloid is None:
            raise RuntimeError(
                "Pyloid instance is not set. Please call adapter.pyloid = your_pyloid_instance "
                "before processing requests. Frontend should use pyloid-js SDK's fetch method "
                "to automatically include the X-Pyloid-Window-Id header."
            )
        
        # Extract window ID from request headers
        window_id = request.headers.get("X-Pyloid-Window-Id")
        
        # Initialize window as None - will be set if valid window_id is found
        window = None
        if window_id:
            try:
                window = self.pyloid.get_window_by_id(window_id)
                if window is None:
                    print(f"Warning: Window with ID '{window_id}' not found in Pyloid application")
            except Exception as e:
                print(f"Error retrieving window '{window_id}': {e}")
        else:
            # Log when window_id header is missing
            print("Warning: X-Pyloid-Window-Id header not found in request. "
                  "Frontend should use pyloid-js SDK's fetch method to include this header. "
                  "Example: pyloid.fetch('/api/endpoint') instead of native fetch()")
        
        return PyloidContext(pyloid=self.pyloid, window=window)

    def pyloid_context(self, func: Callable) -> Callable:
        """
        Decorator that injects PyloidContext into functions with a 'ctx' parameter.
        
        This decorator inspects the decorated function's signature to check if it has
        a parameter named 'ctx'. If it does, the decorator creates a wrapper function
        that automatically injects a PyloidContext instance as the 'ctx' keyword argument.
        
        The decorator works by:
        1. Inspecting the function signature for a 'ctx' parameter
        2. If found, creating PyloidContext from the current request
        3. Injecting the context as 'ctx' keyword argument
        4. Calling the original function with the injected context
        
        Parameters
        ----------
        func : Callable
            The function to decorate. Should have a 'ctx' parameter
            if context injection is desired.
        
        Returns
        -------
        Callable
            The decorated function with context injection capability.
        
        Examples
        --------
        Basic usage with ctx parameter:
        
        ```python
        @app.route("/test")
        @adapter.pyloid_context
        def test_endpoint(ctx: PyloidContext):
            return {"pyloid": ctx.pyloid, "window": ctx.window}
        ```
        
        Function without ctx parameter - decorator does nothing:
        
        ```python
        @app.route("/health")
        @adapter.pyloid_context
        def health_check():
            return {"status": "ok"}
        ```
        
        Notes
        -----
        - Only functions with a 'ctx' parameter in their signature will receive injection
        - Context is created fresh for each request using get_pyloid_context()
        - This approach is clean and doesn't rely on Flask's g object
        """
        # Inspect function signature to check for 'ctx' parameter
        sig = inspect.signature(func)
        has_ctx_param = "ctx" in sig.parameters
        
        # If the function doesn't have a 'ctx' parameter, return the original function
        if not has_ctx_param:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that handles PyloidContext injection.
            
            This wrapper is responsible for:
            1. Creating PyloidContext from the current request
            2. Injecting the context into the function call
            
            The wrapper preserves the original function's behavior while adding
            context injection capability.
            
            Parameters
            ----------
            *args
                Positional arguments passed to the original function.
            **kwargs
                Keyword arguments passed to the original function.
            
            Returns
            -------
            Any
                The result of the original function call.
            """
            # Create PyloidContext from current request
            ctx = self.get_pyloid_context()
            
            # Inject context as keyword argument
            kwargs["ctx"] = ctx
            
            # Call the original function with all arguments, including injected context
            return func(*args, **kwargs)
        
        return wrapper

    def start(self) -> None:
        """
        Start the Flask server.
        
        This method calls the configured start_function with the Flask app,
        host, and port. The start_function is responsible for actually starting
        the server.
        
        The start_function should be a callable that accepts (app, host, port) parameters.
        
        Examples
        --------
        ```python
        def start_server(app: Flask, host: str, port: int):
            app.run(host=host, port=port, debug=True)
        ```
        
        Notes
        -----
        This method will block if using a synchronous start function like app.run().
        For non-blocking operation, use the run() method instead.
        """
        self.start_function(self.app, self.host, self.port)

    def run(self) -> None:
        """
        Run the Flask server in a background thread.
        
        This method creates a daemon thread that runs the server startup process.
        The server will run in the background, allowing the main application to
        continue executing. This is useful for development and testing scenarios.
        
        The method:
        1. Creates a daemon thread with the start() method as target
        2. Starts the thread, which begins server startup
        3. Returns control to the main program
        
        Notes
        -----
        - The thread is set as daemon=True, so it won't prevent program exit
        - Server logs and output will be printed to console
        - Use this for development; consider production WSGI servers for deployment
        """
        print("Running Flask server")
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()
