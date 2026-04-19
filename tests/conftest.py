"""Pytest configuration."""
import sys
import os

# Add project root to Python path so src/ can be imported
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Pre-import all src modules to make them patchable
# This ensures the modules exist as attributes on the src package
try:
    import src.data_fetcher
    import src.strategy
    import src.trade_engine
    import src.paper_trader
    import src.live_trader
    import src.main
except ImportError:
    pass  # Will be handled when tests actually run
