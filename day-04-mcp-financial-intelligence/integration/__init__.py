"""
Integration Connectors Package

Bridge connectors to integrate with the existing Day 1-3 applications:
- day1_connector.py: Market analysis and forecasting bridge
- day2_connector.py: Portfolio risk analytics bridge  
- day3_connector.py: Algorithmic trading platform bridge
"""

from .day1_connector import Day1Connector
from .day2_connector import Day2Connector
from .day3_connector import Day3Connector

__all__ = [
    "Day1Connector",
    "Day2Connector",
    "Day3Connector"
]
