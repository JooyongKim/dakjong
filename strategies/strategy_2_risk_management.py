"""
Strategy 2: Volatility/Decline Speed Based Risk Management

Based on: Thrasher (2017 & 2023)

Identifies increased market risk through:
- VIX standard deviation
- Speed of market decline (Canary signal)
- 200-day SMA crossover confirmation

Generates RISK_OFF signals when risk conditions are confirmed.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from utils.indicators import Indicators


class RiskManagementStrategy(BaseStrategy):
    """
    Strategy 2: Volatility/Decline Speed Based Risk Management.

    Monitors market risk through:
    1. Low VIX volatility (warning signal)
    2. Rapid decline from 52-week high (canary signal)
    3. Break below 200-day SMA (confirmation)

    Generates RISK_OFF signals when warnings are confirmed.
    """

    def __init__(self,
                 vix_std_period: int = 20,
                 vix_std_threshold: float = 0.86,
                 drop_pct: float = 0.05,
                 canary_days: int = 15,
                 confirmation_window: int = 42,
                 sma_period: int = 200,
                 confirmation_days: int = 2):
        """
        Initialize Risk Management Strategy.

        Args:
            vix_std_period: VIX standard deviation period (default: 20)
            vix_std_threshold: VIX std threshold (default: 0.86)
            drop_pct: Decline percentage threshold (default: 0.05 = 5%)
            canary_days: Days to reach drop threshold (default: 15)
            confirmation_window: Warning validity period (default: 42)
            sma_period: Long-term moving average period (default: 200)
            confirmation_days: Consecutive days below SMA (default: 2)
        """
        super().__init__(
            strategy_id="Strategy_2_Risk_Management",
            strategy_name="Volatility/Decline Speed Based Risk Management"
        )

        self.vix_std_period = vix_std_period
        self.vix_std_threshold = vix_std_threshold
        self.drop_pct = drop_pct
        self.canary_days = canary_days
        self.confirmation_window = confirmation_window
        self.sma_period = sma_period
        self.confirmation_days = confirmation_days

        # State tracking
        self.warning_vix = None  # (date, expiry_date)
        self.warning_canary = None  # (date, expiry_date)

    def generate_signals(self,
                        vix_data: pd.DataFrame,
                        market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate risk management signals.

        Args:
            vix_data: VIX index data (must have 'Close' column)
            market_data: Market ETF data (SPY, must have OHLCV)

        Returns:
            DataFrame with signals
        """
        try:
            # Validate input data
            if vix_data.empty or market_data.empty:
                raise ValueError("Input data cannot be empty")

            # Prepare market data
            df = market_data.copy()

            # Calculate VIX standard deviation
            vix_std = vix_data['Close'].rolling(window=self.vix_std_period).std()

            # Calculate 52-week high
            df['High_52W'] = df['High'].rolling(window=252).max()

            # Calculate percentage drop from 52-week high
            df['Pct_Drop'] = (df['Close'] - df['High_52W']) / df['High_52W']

            # Calculate days to reach 5% drop
            df['Days_To_Drop'] = 0

            for i in range(252, len(df)):
                # Find when the 52-week high was set
                high_52w_date_idx = df['High'].iloc[i-252:i+1].idxmax()
                high_52w_idx = df.index.get_loc(high_52w_date_idx)

                # Calculate days from high to current drop level
                if df['Pct_Drop'].iloc[i] <= -self.drop_pct:
                    days_diff = i - high_52w_idx
                    df.iloc[i, df.columns.get_loc('Days_To_Drop')] = days_diff

            # Calculate 200-day SMA
            df['SMA_200'] = Indicators.sma(df['Close'], self.sma_period)

            # Initialize signal column
            df['Signal'] = 'NONE'
            df['Warning_VIX'] = False
            df['Warning_Canary'] = False
            df['Risk_Level'] = 'NORMAL'

            signals_list = []

            # Iterate through data to generate signals
            for i in range(self.sma_period, len(df)):
                date = df.index[i]
                date_str = date.strftime('%Y-%m-%d')

                # Align VIX data
                if date in vix_std.index:
                    current_vix_std = vix_std.loc[date]
                else:
                    continue

                # Check for warning signals
                # Warning 1: Low VIX volatility
                if current_vix_std < self.vix_std_threshold:
                    if self.warning_vix is None:
                        self.warning_vix = (date, date + timedelta(days=self.confirmation_window))
                        df.loc[date, 'Warning_VIX'] = True

                # Check if VIX warning has expired
                if self.warning_vix and date > self.warning_vix[1]:
                    self.warning_vix = None

                # Warning 2: Fast drop (Canary signal)
                if df['Days_To_Drop'].iloc[i] > 0 and df['Days_To_Drop'].iloc[i] <= self.canary_days:
                    if self.warning_canary is None:
                        self.warning_canary = (date, date + timedelta(days=self.confirmation_window))
                        df.loc[date, 'Warning_Canary'] = True

                # Check if Canary warning has expired
                if self.warning_canary and date > self.warning_canary[1]:
                    self.warning_canary = None

                # Update warning flags for display
                if self.warning_vix:
                    df.loc[date, 'Warning_VIX'] = True
                if self.warning_canary:
                    df.loc[date, 'Warning_Canary'] = True

                # Risk confirmation: Check if below 200-day SMA for consecutive days
                if (self.warning_vix or self.warning_canary):
                    df.loc[date, 'Risk_Level'] = 'WARNING'

                    # Check consecutive days below SMA
                    below_sma_count = 0
                    for j in range(self.confirmation_days):
                        if i - j >= 0:
                            if df['Close'].iloc[i-j] < df['SMA_200'].iloc[i-j]:
                                below_sma_count += 1
                            else:
                                break

                    if below_sma_count >= self.confirmation_days:
                        # Generate RISK_OFF signal
                        reason = []
                        if self.warning_vix:
                            reason.append('VIX_Low')
                        if self.warning_canary:
                            reason.append('Fast_Drop')

                        signal = self._create_signal_output(
                            date=date_str,
                            signal='RISK_OFF',
                            asset='SPY',
                            details={
                                'reason': 'Confirmed_' + '_'.join(reason),
                                'VIX_StdDev_20D': round(current_vix_std, 4),
                                'Days_To_5pct_Drop': int(df['Days_To_Drop'].iloc[i]),
                                'Below_SMA_200_Days': int(below_sma_count),
                                'Current_Price': round(df['Close'].iloc[i], 2),
                                'SMA_200': round(df['SMA_200'].iloc[i], 2)
                            }
                        )

                        signals_list.append(signal)
                        df.loc[date, 'Signal'] = 'RISK_OFF'
                        df.loc[date, 'Risk_Level'] = 'RISK_OFF'

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
                asset='SPY',
                details={'reason': 'No risk conditions detected'}
            )

    def reset_state(self):
        """Reset strategy state (for backtesting purposes)."""
        self.warning_vix = None
        self.warning_canary = None
        self.clear_history()
