"""Tool registry: maps tool name -> callable.

In a larger factory, this would auto-discover modules. For v1, we
import the finance module and expose its TOOL_REGISTRY.
"""
from tools.finance import TOOL_REGISTRY

# Re-export under a stable name so callers don't depend on tools.finance directly.
ALL_TOOLS = TOOL_REGISTRY
