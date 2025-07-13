"""
Cross-Border Payment Settlement Engine

Core settlement infrastructure for multi-currency, multi-rail payment processing.
Supports traditional banking rails, stablecoin bridges, and direct crypto settlement.
"""

from .currency_converter import CurrencyConverter
from .stablecoin_bridge import StablecoinBridge
from .traditional_rails import TraditionalRails
from .settlement_optimizer import SettlementOptimizer
from .compliance_checker import ComplianceChecker

__version__ = "1.0.0"
__author__ = "FinTech AI Sparks"

__all__ = [
    "CurrencyConverter",
    "StablecoinBridge",
    "TraditionalRails",
    "SettlementOptimizer",
    "ComplianceChecker"
]
