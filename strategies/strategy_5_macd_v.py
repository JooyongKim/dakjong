"""
Strategy 5: Volatility-Normalized Momentum (MACD-V)

Based on: Spiroglou (2022)

Calculates MACD-V indicator for asset universe and classifies momentum states.
Generates trend signals based on SPY's MACD-V and market regime.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from .base_strategy import BaseStrategy
from utils.indicators import Indicators


class MACDVStrategy(BaseStrategy):
    """
    Strategy 5: Volatility-Normalized Momentum (MACD-V).

    Calculates MACD-V for multiple assets:
    - MACD-V = ((EMA_Short - EMA_Long) / ATR) * 100

    Classifies assets into momentum states:
    - Overbought, Rallying, Ranging (Upper/Lower), Reversing, Oversold

    Generates SPY trend signals based on:
    - Market regime (Bull/Bear via 200-day SMA)
    - MACD-V value relative to thresholds
    """

    def __init__(self,
                 ema_short: int = 12,
                 ema_long: int = 26,
                 atr_period: int = 26,
                 market_filter_sma: int = 200,
                 thresholds: Dict[str, float] = None):
        """
        Initialize MACD-V Strategy.

        Args:
            ema_short: Short EMA period (default: 12)
            ema_long: Long EMA period (default: 26)
            atr_period: ATR period (default: 26)
            market_filter_sma: Market filter SMA period (default: 200)
            thresholds: MACD-V classification thresholds
        """
        super().__init__(
            strategy_id="Strategy_5_MACD_V",
            strategy_name="Volatility-Normalized Momentum (MACD-V)"
        )

        self.ema_short = ema_short
        self.ema_long = ema_long
        self.atr_period = atr_period
        self.market_filter_sma = market_filter_sma

        # Default thresholds
        if thresholds is None:
            self.thresholds = {
                'Overbought': 150,
                'Rallying': 50,
                'Ranging_Upper': 50,
                'Ranging_Lower': -50,
                'Reversing': -150,
                'Oversold': -150
            }
        else:
            self.thresholds = thresholds

    def _classify_macd_v(self, macd_v_value: float) -> str:
        """
        Classify MACD-V value into momentum state.

        Args:
            macd_v_value: MACD-V value

        Returns:
            Momentum state classification
        """
        if pd.isna(macd_v_value):
            return 'Unknown'

        if macd_v_value > self.thresholds['Overbought']:
            return 'Overbought'
        elif macd_v_value > self.thresholds['Rallying']:
            return 'Rallying'
        elif macd_v_value > self.thresholds['Ranging_Upper']:
            return 'Ranging_Upper'
        elif macd_v_value > self.thresholds['Ranging_Lower']:
            return 'Ranging_Lower'
        elif macd_v_value > self.thresholds['Reversing']:
            return 'Reversing'
        else:
            return 'Oversold'

    def _determine_spy_trend(self, macd_v: float, market_regime: str) -> str:
        """
        Determine SPY trend signal based on MACD-V and market regime.

        Args:
            macd_v: SPY MACD-V value
            market_regime: 'Bull' or 'Bear'

        Returns:
            Trend signal
        """
        if market_regime == 'Bull':
            if macd_v > self.thresholds['Rallying']:
                return 'Strong_Up'
            else:
                return 'Weakening_Up'
        else:  # Bear
            if macd_v < self.thresholds['Reversing']:
                return 'Strong_Down'
            else:
                return 'Weakening_Down'

    def generate_signals(self,
                        asset_data: Dict[str, pd.DataFrame],
                        spy_data: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate MACD-V signals for asset universe.

        Args:
            asset_data: Dictionary of asset DataFrames (must include 'SPY')
            spy_data: Optional separate SPY data (if not in asset_data)

        Returns:
            DataFrame with MACD-V values and classifications
        """
        try:
            # Validate input
            if not asset_data:
                raise ValueError("Asset data cannot be empty")

            # Ensure SPY is included
            if 'SPY' not in asset_data:
                if spy_data is not None:
                    asset_data['SPY'] = spy_data
                else:
                    raise ValueError("SPY data must be included")

            # Calculate MACD-V for all assets
            macd_v_results = {}
            asset_status = {}

            for ticker, data in asset_data.items():
                if data.empty:
                    continue

                # Calculate MACD-V
                macd_v = Indicators.macd_v(
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    ema_short=self.ema_short,
                    ema_long=self.ema_long,
                    atr_period=self.atr_period
                )

                macd_v_results[ticker] = macd_v

                # Classify momentum status
                status = macd_v.apply(self._classify_macd_v)
                asset_status[ticker] = status

            # Calculate SPY market regime
            spy_df = asset_data['SPY'].copy()
            spy_df['SMA_200'] = Indicators.sma(spy_df['Close'], self.market_filter_sma)
            spy_df['Market_Regime'] = spy_df.apply(
                lambda row: 'Bull' if row['Close'] > row['SMA_200'] else 'Bear',
                axis=1
            )

            # Generate signals based on SPY
            spy_macd_v = macd_v_results['SPY']
            signals_list = []

            valid_dates = spy_df.index[self.market_filter_sma:]

            for date in valid_dates:
                if date not in spy_macd_v.index:
                    continue

                date_str = date.strftime('%Y-%m-%d')

                macd_v_value = spy_macd_v.loc[date]
                market_regime = spy_df.loc[date, 'Market_Regime']

                # Determine SPY trend
                spy_trend = self._determine_spy_trend(macd_v_value, market_regime)

                # Get all asset statuses for this date
                current_asset_status = {}
                for ticker in asset_status.keys():
                    if date in asset_status[ticker].index:
                        current_asset_status[ticker] = asset_status[ticker].loc[date]

                # Create signal
                signal = self._create_signal_output(
                    date=date_str,
                    signal=spy_trend,
                    asset='SPY',
                    details={
                        'reason': f'{market_regime}_Market_MACD_V',
                        'market_regime': market_regime,
                        'spy_macd_v': round(macd_v_value, 2) if not pd.isna(macd_v_value) else None,
                        'spy_status': self._classify_macd_v(macd_v_value),
                        'asset_status': current_asset_status,
                        'macd_v_values': {
                            ticker: round(macd_v_results[ticker].loc[date], 2)
                            if date in macd_v_results[ticker].index and not pd.isna(macd_v_results[ticker].loc[date])
                            else None
                            for ticker in macd_v_results.keys()
                        }
                    }
                )

                signals_list.append(signal)

            # Save signals (only save when trend changes to reduce clutter)
            if signals_list:
                prev_signal = None
                for signal in signals_list:
                    if signal['signal'] != prev_signal:
                        self.save_signal(signal)
                        prev_signal = signal['signal']

            # Convert to DataFrame
            if signals_list:
                results_df = pd.DataFrame(signals_list)
                return results_df
            else:
                return pd.DataFrame()

        except Exception as e:
            raise Exception(f"Error generating signals for {self.strategy_id}: {str(e)}")

    def get_latest_signal(self) -> Dict[str, Any]:
        """
        Get the most recent signal.

        Returns:
            Latest signal dictionary or default signal
        """
        if self.signals_history:
            return self.signals_history[-1]
        else:
            return self._create_signal_output(
                date=datetime.now().strftime('%Y-%m-%d'),
                signal='Unknown',
                asset='SPY',
                details={
                    'reason': 'No data available',
                    'market_regime': 'Unknown'
                }
            )

    def reset_state(self):
        """Reset strategy state (for backtesting purposes)."""
        self.clear_history()
