"""Lowercase shim for Barcable SDK.

This module provides a lowercase import path for the Barcable SDK.
Users can import with either:
    import Barcable
    import barcable
"""

# Import everything from the main Barcable module
from Barcable import *

# Also make the version available
from Barcable.version import __version__