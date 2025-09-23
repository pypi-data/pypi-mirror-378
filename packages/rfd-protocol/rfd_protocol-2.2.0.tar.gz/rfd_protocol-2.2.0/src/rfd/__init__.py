"""
RFD Protocol - Reality-First Development

A protocol that prevents AI hallucination in software development by enforcing
concrete reality checkpoints.
"""

__version__ = "2.2.0"
__author__ = "RFD Team"
__email__ = "team@rfd-protocol.dev"
__description__ = "Reality-First Development Protocol"

from .rfd import RFD
from .build import BuildEngine
from .validation import ValidationEngine  
from .spec import SpecEngine
from .session import SessionManager

__all__ = [
    "RFD",
    "BuildEngine", 
    "ValidationEngine",
    "SpecEngine",
    "SessionManager"
]