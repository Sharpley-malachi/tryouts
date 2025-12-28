"""
DEPENDENCY PROVIDER
-------------------
This module exists to break the circular dependency between:
1. command_service (which needs TheGeneral instance)
2. main_governor (which defines TheGeneral class)

By instantiating the singleton here, we allow both modules to import it
without triggering an import loop.
"""
from .main_governor import TheGeneral

# Global Singleton Instance for The General
the_general = TheGeneral()
