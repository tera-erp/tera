"""Company module package placeholder.

This module integrates the existing company functionality into the modules
system by providing configuration and a setup entrypoint. The actual
API endpoints remain in `tera.routers.companies` to preserve backward
compatibility.
"""
from . import setup  # expose setup for modules.fix invocation
