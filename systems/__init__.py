# Systems Module - الأنظمة المحسنة
"""
هذا المجلد يحتوي على جميع الأنظمة المحسنة
"""

try:
    from .simple_enhanced_system import SimpleEnhancedSystem, simple_enhanced_system
except ImportError:
    pass

try:
    from .enhanced_portfolio_manager import EnhancedPortfolioManager, portfolio_factory
except ImportError:
    pass

try:
    from .integrated_signal_system import IntegratedSignalSystem, integrated_signal_system
except ImportError:
    pass

__all__ = [
    'SimpleEnhancedSystem',
    'simple_enhanced_system',
    'EnhancedPortfolioManager',
    'portfolio_factory',
    'IntegratedSignalSystem',
    'integrated_signal_system'
]
