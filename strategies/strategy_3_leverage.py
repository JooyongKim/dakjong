"""
Strategy 3: Trend-Based Leverage

Based on: Gayed & Bilello (2016)

Uses S&P 500 long-term trend (200-day SMA) to determine leverage usage.

Generates LEVERAGE_ON/LEVERAGE_OFF signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime

from .base_strategy import BaseStrategy
from utils.indicators import Indicators


class LeverageStrategy(BaseStrategy):
    """
    Strategy 3: Trend-Based Leverage.

    Simple trend-following strategy:
    - LEVERAGE_ON when price > 200-day SMA
    - LEVERAGE_OFF when price < 200-day SMA

    Designed to use leverage during bull markets and avoid it during bear markets.
    """

    def __init__(self,
                 sma_period: int = 200,
                 leverage_multiple: float = 1.5,
                 target_asset: str = 'SPY'):
        """
        Initialize Leverage Strategy.

        Args:
            sma_period: Moving average period (default: 200)
            leverage_multiple: Leverage multiplier (default: 1.5)
            target_asset: Target ETF (default: 'SPY')
        """
        super().__init__(
            strategy_id="Strategy_3_Leverage",
            strategy_name="Trend-Based Leverage"
        )

        self.sma_period = sma_period
        self.leverage_multiple = leverage_multiple
        self.target_asset = target_asset

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate leverage signals based on trend.

        Args:
            market_data: Market ETF data (SPY) with OHLCV

        Returns:
            DataFrame with signals
        """
        try:
            # Validate input data
            if market_data.empty:
                raise ValueError("Input data cannot be empty")

            df = market_data.copy()

            # Calculate 200-day SMA
            df['SMA_200'] = Indicators.sma(df['Close'], self.sma_period)

            # Generate signals
            df['Signal'] = 'LEVERAGE_OFF'
            df['Price_vs_SMA'] = df['Close'] - df['SMA_200']
            df['Trend'] = 'Bear'

            signals_list = []

            for i in range(self.sma_period, len(df)):
                date = df.index[i]
                date_str = date.strftime('%Y-%m-%d')

                current_price = df['Close'].iloc[i]
                current_sma = df['SMA_200'].iloc[i]

                if current_price > current_sma:
                    # Bull trend - use leverage
                    signal_type = 'LEVERAGE_ON'
                    df.loc[date, 'Signal'] = signal_type
                    df.loc[date, 'Trend'] = 'Bull'

                    signal = self._create_signal_output(
                        date=date_str,
                        signal=signal_type,
                        asset=self.target_asset,
                        details={
                            'reason': 'Price_Above_SMA',
                            'leverage_multiple': self.leverage_multiple,
                            'current_price': round(current_price, 2),
                            'sma_200': round(current_sma, 2),
                            'price_vs_sma_pct': round(((current_price / current_sma) - 1) * 100, 2)
                        }
                    )
                else:
                    # Bear trend - avoid leverage
                    signal_type = 'LEVERAGE_OFF'
                    df.loc[date, 'Signal'] = signal_type

                    signal = self._create_signal_output(
                        date=date_str,
                        signal=signal_type,
                        asset=self.target_asset,
                        details={
                            'reason': 'Price_Below_SMA',
                            'leverage_multiple': 1.0,
                            'current_price': round(current_price, 2),
                            'sma_200': round(current_sma, 2),
                            'price_vs_sma_pct': round(((current_price / current_sma) - 1) * 100, 2)
                        }
                    )

                signals_list.append(signal)

            # Save only the most recent signals (to avoid clutter)
            # In practice, you might want to save only when signal changes
            if signals_list:
                # Save signal changes only
                prev_signal = None
                for signal in signals_list:
                    if signal['signal'] != prev_signal:
                        self.save_signal(signal)
                        prev_signal = signal['signal']

            return df

        except Exception as e:
            raise Exception(f"Error generating signals for {self.strategy_id}: {str(e)}")

    def get_latest_signal(self) -> Dict[str, Any]:
        """
        Get the most recent signal.

        Returns:
            Latest signal dictionary or default LEVERAGE_OFF
        """
        if self.signals_history:
            return self.signals_history[-1]
        else:
            return self._create_signal_output(
                date=datetime.now().strftime('%Y-%m-%d'),
                signal='LEVERAGE_OFF',
                asset=self.target_asset,
                details={
                    'reason': 'No data available',
                    'leverage_multiple': 1.0
                }
            )

    def reset_state(self):
        """Reset strategy state (for backtesting purposes)."""
        self.clear_history()
