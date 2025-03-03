"""Debugging utilities for chart rendering and optimization."""

import sys
from functools import wraps
import time

# Global debug flag - set to True to enable detailed debug output
DEBUG = False


def set_debug(enabled=True):
    """Enable or disable detailed debugging"""
    global DEBUG
    DEBUG = enabled


def debug_print(msg, *args, **kwargs):
    """Print debug messages only if debug is enabled"""
    if DEBUG:
        print(f"[DEBUG] {msg}", *args, **kwargs)


def timed(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not DEBUG:
            return func(*args, **kwargs)

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        debug_print(f"{func.__name__} took {(end - start) * 1000:.2f}ms")
        return result
    return wrapper


def check_renderer_ready(canvas):
    """Check if a canvas's renderer is ready for operations like blitting"""
    try:
        if not hasattr(canvas, 'renderer'):
            debug_print("Canvas has no renderer yet")
            return False

        if canvas.renderer is None:
            debug_print("Canvas renderer is None")
            return False

        # Try accessing methods that would be needed for blitting
        if not hasattr(canvas.renderer, 'copy_from_bbox'):
            debug_print("Renderer doesn't support copy_from_bbox")
            return False

        return True
    except Exception as e:
        debug_print(f"Error checking renderer: {e}")
        return False
