"""
Education Modules for Laura-bot Personal Learning Assistant
"""

from .math_module import MathModule
from .science_module import ScienceModule

__all__ = ['MathModule', 'ScienceModule']

# Module registry for easy access
AVAILABLE_MODULES = {
    'Math': MathModule,
    'Science': ScienceModule,
    'Mathematics': MathModule,  # Alternative name
    'Biology': ScienceModule,   # Science sub-topics
    'Chemistry': ScienceModule,
    'Physics': ScienceModule
}

def get_education_module(subject: str):
    """Get the appropriate education module for a subject"""
    if subject in AVAILABLE_MODULES:
        return AVAILABLE_MODULES[subject]()
    else:
        return None

def list_available_subjects():
    """Get list of all available subjects"""
    return list(set(AVAILABLE_MODULES.keys()))