"""
BasicAGI - Asterisk AGI Python Library

A Python library for creating Asterisk Gateway Interface (AGI) applications.
This library provides a simple and intuitive interface for interacting with
Asterisk PBX through the AGI protocol.

Basic usage:
    from basicagi import BasicAGI

    agi = BasicAGI()
    agi.answer()
    agi.stream_file("welcome")
    agi.hangup()
"""

from .basic_agi import BasicAGI

__version__ = "1.0.1"
__author__ = "Andrius Kairiukstis"
__email__ = "k@andrius.mobi"
__description__ = "A Python library for Asterisk Gateway Interface (AGI) applications"

__all__ = ["BasicAGI"]
