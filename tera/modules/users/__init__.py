"""Users module package placeholder.

Exposes the `setup` entrypoint so the modules `fix` mechanism can call
into the users module without changing the existing routers (which remain
under `tera.routers.users` for backwards compatibility).
"""
from . import setup
