import sys
from unittest.mock import MagicMock

# Must be set before any test module is imported, because orchestrator.py
# imports compass.storage at module level (storage module not yet merged).
sys.modules.setdefault('compass.storage', MagicMock())
sys.modules.setdefault('compass.storage.analysis_context_store', MagicMock())
