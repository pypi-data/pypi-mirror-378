"""
Pyloid Server Adapter for FastAPI

This module provides a FastAPI adapter that enables seamless integration between Pyloid
applications and FastAPI web servers. It allows Pyloid applications to access their
context (including the Pyloid instance and current browser window) within FastAPI
route handlers through dependency injection or decorator-based injection.

The adapter handles:
- Pyloid instance management and window registration
- Automatic context creation from HTTP requests
- Multiple injection methods (decorator and dependency injection)
- Server lifecycle management (start/stop)

Key Components:
- PyloidContext: Data class holding Pyloid application and window context
- FastAPIAdapter: Main adapter class that manages the integration

Usage:
    adapter = FastAPIAdapter(app=app, start_function=start_server)
    adapter.pyloid = pyloid_instance  # Set the Pyloid instance
    # Use either decorator or dependency injection to access context
"""

from fastapi import FastAPI, Request
from .utils import get_free_port
import threading
from typing import Callable, Optional
from typing import TYPE_CHECKING
import inspect
from functools import wraps

# Type checking imports to avoid circular imports at runtime
if TYPE_CHECKING:
    from pyloid import Pyloid
    from pyloid.browser_window import BrowserWindow

# FastAPI specific Pydantic model
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PyloidContext(BaseModel):
    """
    Context class for FastAPI server integration with Pyloid applications.

    This class encapsulates the Pyloid application instance and the current browser
    window context, making them easily accessible within FastAPI route handlers.

    Attributes
    ----------
    pyloid : Pyloid
        The main Pyloid application instance.
    window : BrowserWindow
        The current browser window instance associated with the request.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    pyloid: Optional[Pyloid] = Field(default=None, description="The main Pyloid application instance")
    window: Optional[BrowserWindow] = Field(default=None, description="The current browser window instance")

class FastAPIAdapter:
    """
    FastAPI adapter for Pyloid application integration.
    
    This adapter class serves as the main integration point between Pyloid applications
    and FastAPI web servers. It provides multiple mechanisms for injecting Pyloid
    context into route handlers and manages the server lifecycle.
    
    The adapter supports two primary methods of context injection:
    1. Decorator-based injection using @adapter.pyloid_context
    2. Dependency injection using FastAPI's Depends() system
    
    Attributes
    ----------
    app : FastAPI
        The FastAPI application instance to integrate with.
    start_function : Callable[[FastAPI, str, int], None]
        Function to start the server with (app, host, port).
    """
    
    def __init__(self, app: FastAPI, start_function: Callable[[str, int], None]):
        """
        Initialize the FastAPI adapter.
        
        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance to integrate with.
        start_function : Callable[[FastAPI, str, int], None]
            Function that starts the server. Should accept (app, host, port) parameters.
        """
        self.app: FastAPI = app
        self.host: str = "127.0.0.1"
        self.port: int = get_free_port()
        self.start_function: Callable[[FastAPI, str, int], None] = start_function
        self.pyloid: Optional["Pyloid"] = None

    def get_pyloid_context(self, request: Request) -> PyloidContext:
        """
        Create PyloidContext from an HTTP request.
        
        This method extracts the window ID from the request headers and creates
        a PyloidContext instance with the appropriate Pyloid application and window.
        
        The method looks for the 'X-Pyloid-Window-Id' header in the request to
        determine which browser window the request is associated with. If the
        header is present, it attempts to retrieve the corresponding window from
        the Pyloid application. If the header is missing or the window is not found,
        the window attribute will be None.
        
        Parameters
        ----------
        request : Request
            The FastAPI Request object containing headers and metadata.
            
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
        # Validate that pyloid instance is set
        if self.pyloid is None:
            raise RuntimeError(
                "Pyloid instance is not set. Please call adapter.pyloid = your_pyloid_instance "
                "before processing requests. Frontend should use pyloid-js SDK's fetch method "
                "to automatically include the X-Pyloid-Window-Id header."
            )
        
        # Extract window ID from request headers
        # The X-Pyloid-Window-Id header contains the identifier of the browser window
        # making the request. This allows the server to associate requests with specific windows
        window_id = request.headers.get("X-Pyloid-Window-Id")
        
        # Initialize window as None - will be set if valid window_id is found
        window = None
        if window_id:
            # Attempt to retrieve the window instance from the Pyloid application
            # This method call may raise an exception if the window_id is invalid
            # or if the pyloid instance is not properly configured
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
        
        # Create and return PyloidContext with pyloid instance and resolved window
        # The pyloid instance should have been set via the pyloid property before
        # any requests are processed
        return PyloidContext(pyloid=self.pyloid, window=window)

    def pyloid_context_dependency(self) -> Callable[[Request], PyloidContext]:
        """
        Create a FastAPI dependency function for PyloidContext injection.
        
        This method returns a dependency function that can be used with FastAPI's
        Depends() system to automatically inject PyloidContext into route handlers.
        
        The returned function will be called by FastAPI's dependency injection system
        for each request, creating a fresh PyloidContext based on the request headers.
        
        Returns
        -------
        Callable[[Request], PyloidContext]
            A dependency function that returns PyloidContext.
            
        Examples
        --------
        ```python
        @app.get("/endpoint")
        async def handler(ctx: PyloidContext = Depends(adapter.pyloid_context_dependency())):
            # ctx is automatically injected
            pass
        ```
        
        Notes
        -----
        This is the recommended approach for FastAPI integration as it leverages
        FastAPI's built-in dependency injection system for better performance
        and cleaner code.
        """
        def _get_context(request: Request) -> PyloidContext:
            """
            Internal dependency function that creates PyloidContext from request.
            
            This function is called by FastAPI's dependency injection system for
            each request that depends on PyloidContext. It extracts context
            information from the request and creates a PyloidContext instance.
            
            Parameters
            ----------
            request : Request
                The current HTTP request object.
                
            Returns
            -------
            PyloidContext
                Context object for the current request.
            """
            return self.get_pyloid_context(request)
        
        return _get_context

    def pyloid_context(self, func: Callable) -> Callable:
        """
        Decorator that injects PyloidContext into functions with a 'ctx' parameter.
        
        This decorator inspects the decorated function's signature to check if it has
        a parameter named 'ctx'. If it does, the decorator creates a wrapper function
        that automatically injects a PyloidContext instance as the 'ctx' keyword argument.
        
        The decorator works by:
        1. Inspecting the function signature for a 'ctx' parameter
        2. If found, creating a wrapper that extracts the request from function arguments
        3. Creating PyloidContext from the request
        4. Injecting the context as 'ctx' keyword argument
        5. Calling the original function with the injected context
        
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
        @app.get("/test")
        @adapter.pyloid_context
        async def test_endpoint(ctx: PyloidContext):
            return {"pyloid": ctx.pyloid, "window": ctx.window}
        ```
        
        Function without ctx parameter - decorator does nothing:
        
        ```python
        @app.get("/health")
        @adapter.pyloid_context
        async def health_check():
            return {"status": "ok"}
        ```
        
        Notes
        -----
        - Only functions with a 'ctx' parameter in their signature will receive injection
        - The decorator attempts to find the Request object in the function arguments
        - If no Request is found, context injection is skipped
        - This approach is more flexible but less performant than dependency injection
        - Best used when you need conditional context injection or complex logic
        """
        # Inspect function signature to check for 'ctx' parameter
        # This allows the decorator to work with any function signature while only
        # injecting context when the 'ctx' parameter is present
        sig = inspect.signature(func)
        has_ctx_param = "ctx" in sig.parameters
        
        # If the function doesn't have a 'ctx' parameter, return the original function
        # This makes the decorator safe to use on any function without side effects
        if not has_ctx_param:
            return func
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            """
            Wrapper function that handles PyloidContext injection.
            
            This wrapper is responsible for:
            1. Finding the Request object in the function arguments
            2. Creating PyloidContext from the request
            3. Injecting the context into the function call
            
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
            # Attempt to find the Request object in function arguments
            # FastAPI automatically injects the Request object into route handlers,
            # so it should be available in the args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Handle case where request is not found in arguments
            # This can happen if the decorator is used incorrectly or if FastAPI's
            # dependency injection system is not working as expected
            if request is None:
                # In a properly configured FastAPI application, the request should
                # always be available. This code path should rarely be executed.
                # If it is, context injection will be skipped and the function
                # will be called without the ctx parameter
                pass
            
            # Create PyloidContext and inject it if request was found
            # The context is created fresh for each request, ensuring that each
            # request gets its own context with the correct window information
            if request:
                ctx = self.get_pyloid_context(request)
                kwargs["ctx"] = ctx
            
            # Call the original function with all arguments, including injected context
            # The function signature inspection ensures that 'ctx' is a valid parameter
            return await func(*args, **kwargs)
        
        return wrapper

    def start(self) -> None:
        """
        Start the FastAPI server.
        
        This method calls the configured start_function with the FastAPI app,
        host, and port. The start_function is responsible for actually starting
        the server (typically using uvicorn or similar ASGI server).
        
        The start_function should be a callable that accepts (app, host, port) parameters.
        
        Examples
        --------
        ```python
        def start_server(app: FastAPI, host: str, port: int) -> None:
            uvicorn.run(app, host=host, port=port)
        ```
        
        Notes
        -----
        This method will block if using a synchronous start function like uvicorn.run().
        For non-blocking operation, use the run() method instead.
        """
        self.start_function(self.app, self.host, self.port)

    def run(self) -> None:
        """
        Run the FastAPI server in a background thread.
        
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
        print(f"Running server")
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()