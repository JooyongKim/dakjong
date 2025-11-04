"""
Strategy 1: Market Panic Identification and Bottom Buying

Based on: Vince & Williams (2024); Diodato (2019)

Detects extreme panic selling conditions and generates BUY signals for market ETFs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from utils.data_loader import DataLoader


class PanicBuyStrategy(BaseStrategy):
    """
    Strategy 1: Market Panic Identification and Bottom Buying.

    Identifies extreme selling pressure through:
    - NYSE New Lows Ratio (3-day MA)
    - STCO (Short-Term Cumulative Oscillator)

    Generates BUY signals when both conditions are met.
    """

    def __init__(self,
                 nl_ma_period: int = 3,
                 nl_threshold: float = 0.50,
                 stco_ma_period: int = 10,
                 stco_threshold: float = 80,
                 signal_confirmation_days: int = 1,
                 entry_logic: str = 'Delayed',
                 delay_days: int = 10,
                 target_asset: str = 'SPY'):
        """
        Initialize Panic Buy Strategy.

        Args:
            nl_ma_period: New Lows moving average period (default: 3)
            nl_threshold: New Lows ratio threshold (default: 0.50 = 50%)
            stco_ma_period: STCO moving average period (default: 10)
            stco_threshold: STCO threshold (default: 80)
            signal_confirmation_days: Days to confirm signal (default: 1)
            entry_logic: 'Delayed' or 'Confirmed' (default: 'Delayed')
            delay_days: Days to wait for delayed entry (default: 10)
            target_asset: Target ETF to buy (default: 'SPY')
        """
        super().__init__(
            strategy_id="Strategy_1_Panic_Buy",
            strategy_name="Market Panic Identification and Bottom Buying"
        )

        self.nl_ma_period = nl_ma_period
        self.nl_threshold = nl_threshold
        self.stco_ma_period = stco_ma_period
        self.stco_threshold = stco_threshold
        self.signal_confirmation_days = signal_confirmation_days
        self.entry_logic = entry_logic
        self.delay_days = delay_days
        self.target_asset = target_asset

        # State tracking for delayed entry
        self.pending_signals = []

    def generate_signals(self,
                        nyse_breadth_data: pd.DataFrame,
                        market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate panic buy signals.

        Args:
            nyse_breadth_data: DataFrame with columns:
                - NewLows_Ratio
                - UpVolume_Ratio
                - Advancing_Ratio
            market_data: Market ETF price data (SPY/QQQ)

        Returns:
            DataFrame with signals
        """
        try:
            # Validate input data
            if nyse_breadth_data.empty or market_data.empty:
                raise ValueError("Input data cannot be empty")

            # Calculate indicators
            df = nyse_breadth_data.copy()

            # New Lows 3-day MA
            df['NewLows_3MA'] = df['NewLows_Ratio'].rolling(
                window=self.nl_ma_period
            ).mean()

            # STCO (Short-Term Cumulative Oscillator)
            # STCO = (10-day MA of Up Volume Ratio * 100) + (10-day MA of Advancing Ratio * 100)
            up_vol_ma = df['UpVolume_Ratio'].rolling(
                window=self.stco_ma_period
            ).mean()
            adv_ma = df['Advancing_Ratio'].rolling(
                window=self.stco_ma_period
            ).mean()

            df['STCO'] = (up_vol_ma * 100) + (adv_ma * 100)

            # Identify panic conditions
            df['Condition_NL'] = df['NewLows_3MA'] > self.nl_threshold
            df['Condition_STCO'] = df['STCO'] < self.stco_threshold

            # Combined condition
            df['Panic_Condition'] = df['Condition_NL'] & df['Condition_STCO']

            # Generate signals
            df['Signal'] = 'NONE'
            signals_list = []

            for i in range(len(df)):
                if i < max(self.nl_ma_period, self.stco_ma_period):
                    continue

                date = df.index[i]
                date_str = date.strftime('%Y-%m-%d')

                # Check for panic condition
                if df['Panic_Condition'].iloc[i]:
                    if self.entry_logic == 'Delayed':
                        # Schedule delayed entry
                        entry_date = date + timedelta(days=self.delay_days)
                        self.pending_signals.append({
                            'trigger_date': date_str,
                            'entry_date': entry_date.strftime('%Y-%m-%d'),
                            'nl_value': df['NewLows_3MA'].iloc[i],
                            'stco_value': df['STCO'].iloc[i]
                        })

                    elif self.entry_logic == 'Confirmed':
                        # Check for confirmation (Close > previous High)
                        if i > 0 and 'High' in market_data.columns:
                            market_idx = market_data.index.get_indexer([date], method='nearest')[0]
                            if market_idx > 0:
                                current_close = market_data['Close'].iloc[market_idx]
                                prev_high = market_data['High'].iloc[market_idx - 1]

                                if current_close > prev_high:
                                    signal = self._create_signal_output(
                                        date=date_str,
                                        signal='BUY',
                                        asset=self.target_asset,
                                        details={
                                            'reason': 'Panic_Confirmed',
                                            'NewLows_3MA': round(df['NewLows_3MA'].iloc[i], 4),
                                            'STCO': round(df['STCO'].iloc[i], 2)
                                        }
                                    )
                                    signals_list.append(signal)
                                    df.loc[date, 'Signal'] = 'BUY'

            # Process delayed entries
            if self.entry_logic == 'Delayed':
                for pending in self.pending_signals:
                    entry_date = pd.to_datetime(pending['entry_date'])
                    if entry_date in df.index:
                        signal = self._create_signal_output(
                            date=pending['entry_date'],
                            signal='BUY',
                            asset=self.target_asset,
                            details={
                                'reason': 'Panic_Delayed',
                                'trigger_date': pending['trigger_date'],
                                'NewLows_3MA': round(pending['nl_value'], 4),
                                'STCO': round(pending['stco_value'], 2)
                            }
                        )
                        signals_list.append(signal)
                        df.loc[entry_date, 'Signal'] = 'BUY'

            # Save signals to history
            for signal in signals_list:
                self.save_signal(signal)

            return df

        except Exception as e:
            raise Exception(f"Error generating signals for {self.strategy_id}: {str(e)}")

    def get_latest_signal(self) -> Dict[str, Any]:
        """
        Get the most recent signal.

        Returns:
            Latest signal dictionary or NONE signal
        """
        if self.signals_history:
            return self.signals_history[-1]
        else:
            return self._create_signal_output(
                date=datetime.now().strftime('%Y-%m-%d'),
                signal='NONE',
                asset=self.target_asset,
                details={'reason': 'No panic conditions detected'}
            )

    def reset_state(self):
        """Reset strategy state (for backtesting purposes)."""
        self.pending_signals = []
        self.clear_history()
