import socket

def get_free_url() -> str:
    """
    Finds and returns an available random network url from the operating system.
    
    Returns
    -------
    str
        An available random network url
        
    Examples
    --------
    >>> from pyloid.utils import get_free_url
    >>> url = get_free_url()
    >>> print(f"Found available url: {url}")
    Found available url: http://127.0.0.1:49152
    """
    return f"http://127.0.0.1:{get_free_port()}"

def get_free_port() -> int:
    """
    Finds and returns an available random network port number from the operating system.

    This function creates a socket and binds it to port '0', allowing the operating system
    to allocate a random available port. It retrieves the port number and safely closes
    the socket afterward.

    Returns
    -------
    int
        An available network port number (typically in the range 1024-65535)

    Notes
    -----
    - Since this function closes the socket immediately after finding a port, there is a
      possibility that the port could be reassigned to another process.
    - It is recommended to use the port number quickly after receiving it.
    - This function interacts with the operating system's network stack, so its behavior
      may vary depending on firewall or network settings.

    Examples
    --------
    >>> from pyloid.utils import get_free_port
    >>> port = get_free_port()
    >>> print(f"Found available port: {port}")
    Found available port: 49152

    >>> # Web server example
    >>> import http.server
    >>> server = http.server.HTTPServer(('localhost', port), http.server.SimpleHTTPRequestHandler)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
