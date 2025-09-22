"""
Flask LTFI-WSAP Integration

Flask extension for integrating LTFI-WSAP (Layered Transformer Framework Intelligence - 
Web System Alignment Protocol) into Flask applications.
"""

__version__ = "2.0.0"

from .extension import WSAP
from .views import wsap_blueprint

__all__ = ['WSAP', 'wsap_blueprint']