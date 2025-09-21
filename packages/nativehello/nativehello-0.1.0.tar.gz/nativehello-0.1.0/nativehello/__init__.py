"""
Hello World in All Native Languages package.
"""

from .greetings import get_greeting, list_languages, greet_all

# package's version string
__version__ = '0.1.0'

# package's public API : from native_hello import *
__all__ = ['get_greeting', 'list_languages', 'greet_all']