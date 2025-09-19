"""
AbstractMemory - PLACEHOLDER PROJECT

This is a placeholder package to reserve the 'AbstractMemory' name on PyPI.

AbstractMemory will be a memory system designed to transform stateless LLMs 
into stateful LLMs, with primary integration planned for AbstractLLM.

The actual implementation is currently part of AbstractLLM and will be 
modularized into this separate package in the future to enable:
- Cleaner separation of concerns
- Better evolution and maintenance over time
- Reusability across different LLM frameworks

WARNING: This is a placeholder. Do not use in production.
"""

__version__ = "0.0.1"
__author__ = "AbstractMemory Team"
__email__ = "contact@example.com"

# Placeholder exception to prevent accidental usage
class PlaceholderError(Exception):
    """Raised when attempting to use placeholder functionality."""
    pass

def placeholder_warning():
    """
    Warn users that this is a placeholder package.
    
    Raises:
        PlaceholderError: Always raised to prevent usage
    """
    raise PlaceholderError(
        "AbstractMemory is currently a placeholder package. "
        "The actual memory system implementation is part of AbstractLLM. "
        "This package reserves the name for future modularization."
    )

# Make it clear this is a placeholder
__all__ = ["placeholder_warning", "PlaceholderError", "__version__"]
