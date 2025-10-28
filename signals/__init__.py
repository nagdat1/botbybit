# Signals Module - أنظمة الإشارات
"""
هذا المجلد يحتوي على جميع أنظمة الإشارات
"""

# استيرادها مباشرة للاستخدام السهل
try:
    from .signal_executor import SignalExecutor, signal_executor
except ImportError:
    pass

try:
    from .signal_converter import convert_simple_signal
except ImportError:
    pass

try:
    from .signal_id_manager import get_position_id_from_signal, get_signal_id_manager
except ImportError:
    pass

try:
    from .signal_position_manager import signal_position_manager
except ImportError:
    pass

__all__ = [
    'SignalExecutor',
    'signal_executor',
    'convert_simple_signal',
    'signal_position_manager'
]
