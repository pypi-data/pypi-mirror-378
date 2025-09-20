"""High-level public interface for the LLM detector."""

from .api import classify_text
from .runtime import DetectionResult, DetectorRuntime

__version__ = "0.1.1"
__all__ = ["DetectorRuntime", "DetectionResult", "classify_text"]
