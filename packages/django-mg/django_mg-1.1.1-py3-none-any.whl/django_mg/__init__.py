"""
Django Model Generator
======================

Simple Django model generator with slash-separated field codes.

:author: Mobin Hasanghasemi (mobin.hasanghasemi.m@gmail.com)
:version: 1.0.0
:license: MIT
"""

__version__ = "1.0.0"
__author__ = "Mobin Hasanghasemi"
__author_email__ = "mobin.hasanghasemi.m@gmail.com"
__license__ = "MIT"

from .management.commands.generate_model import Command

__all__ = ["Command"]