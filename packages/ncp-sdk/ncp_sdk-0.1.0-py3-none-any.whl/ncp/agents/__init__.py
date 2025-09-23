"""NCP SDK Agents module.

This module provides the Agent class and related functionality for creating
AI agents in the NCP SDK. Agents are designed locally but executed remotely
on the NCP platform.
"""

from .base import Agent
from .config import ModelConfig

__all__ = ["Agent", "ModelConfig"]