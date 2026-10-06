"""vendor_risk: third-party and supply chain risk scoring for small and mid-sized organizations."""

from .engine import assess, load_model, load_vendors, parse_vendors

__version__ = "0.1.0"
__all__ = ["assess", "load_model", "load_vendors", "parse_vendors", "__version__"]
