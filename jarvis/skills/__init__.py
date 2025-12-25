#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jarvis AI Assistant - Skills Module
Sistema de skills modular e extensível.
"""

from .base_skill import (
    BaseSkill,
    SkillMetadata,
    SkillResponse,
    SkillPriority,
    SkillStatus
)

from .builtin import WeatherSkill

__all__ = [
    'BaseSkill',
    'SkillMetadata',
    'SkillResponse',
    'SkillPriority',
    'SkillStatus',
    'WeatherSkill',
]

__version__ = '1.0.0'
