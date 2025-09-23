"""
BelArabyAI SDK for BelArabyAI AI Worker Platform

A Python SDK for creating and managing AI Workers with thread execution capabilities.
"""

__version__ = "0.1.0"

from .ba.ba import BASdk
from .ba.tools import AgentPressTools, MCPTools

# Main SDK class alias for better usability
BelArabyAI = BASdk

__all__ = ["BelArabyAI", "BASdk", "AgentPressTools", "MCPTools"]
