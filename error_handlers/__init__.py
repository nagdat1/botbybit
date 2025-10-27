#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالجات الأخطاء الشاملة للبوت
"""

from .callback_error_handler import (
    handle_callback_error,
    UnknownCommandHandler
)

__all__ = [
    'handle_callback_error',
    'UnknownCommandHandler'
]

