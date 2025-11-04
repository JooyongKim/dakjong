"""
Base class for all strategy modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime


class BaseStrategy(ABC):
    """
    Abstract base class for all investment strategy signal generators.

    All strategies must implement:
    - generate_signals(): Main signal generation logic
    - get_latest_signal(): Get the most recent signal
    """

    def __init__(self, strategy_id: str, strategy_name: str):
        """
        Initialize base strategy.

        Args:
            strategy_id: Unique identifier for the strategy
            strategy_name: Human-readable name
        """
        self.strategy_id = strategy_id
        self.strategy_name = strategy_name
        self.signals_history = []

    @abstractmethod
    def generate_signals(self, **kwargs) -> pd.DataFrame:
        """
        Generate trading signals based on strategy logic.

        Returns:
            DataFrame with signals and associated metadata
        """
        pass

    @abstractmethod
    def get_latest_signal(self) -> Dict[str, Any]:
        """
        Get the most recent signal in JSON format.

        Returns:
            Dictionary containing:
                - strategy_id: Strategy identifier
                - date: Signal date
                - signal: Signal type (BUY, SELL, RISK_OFF, etc.)
                - asset: Target asset
                - details: Additional signal details
        """
        pass

    def _create_signal_output(self, date: str, signal: str, asset: str,
                             details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create standardized signal output.

        Args:
            date: Signal date (YYYY-MM-DD)
            signal: Signal type
            asset: Target asset ticker
            details: Additional signal details

        Returns:
            Standardized signal dictionary
        """
        output = {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "date": date,
            "signal": signal,
            "asset": asset,
            "details": details if details else {}
        }

        return output

    def save_signal(self, signal: Dict[str, Any]):
        """
        Save signal to history.

        Args:
            signal: Signal dictionary
        """
        self.signals_history.append(signal)

    def get_signals_history(self) -> list:
        """
        Get all historical signals.

        Returns:
            List of signal dictionaries
        """
        return self.signals_history

    def clear_history(self):
        """Clear signal history."""
        self.signals_history = []
