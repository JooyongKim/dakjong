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
from utils.visualizer import Visualizer
import matplotlib.pyplot as plt


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

            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate VIX standard deviation
            vix_close = vix_data['Close']
            if isinstance(vix_close, pd.DataFrame):
                vix_close = vix_close.iloc[:, 0]
            vix_std = vix_close.rolling(window=self.vix_std_period).std()

            # Calculate 52-week high
            high_series = df['High']
            if isinstance(high_series, pd.DataFrame):
                high_series = high_series.iloc[:, 0]
            df['High_52W'] = high_series.rolling(window=252).max()

            # Calculate percentage drop from 52-week high
            close_series = df['Close']
            if isinstance(close_series, pd.DataFrame):
                close_series = close_series.iloc[:, 0]
            df['Pct_Drop'] = (close_series - df['High_52W']) / df['High_52W']

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

    def plot(self, vix_data: pd.DataFrame, market_data: pd.DataFrame, save_path: str = None):
        """
        Visualize strategy indicators and signals.

        Args:
            vix_data: VIX data
            market_data: Market data
            save_path: Optional path to save the figure
        """
        # Generate signals
        df = self.generate_signals(vix_data, market_data)

        # Prepare VIX data
        vix_close = vix_data['Close']
        if isinstance(vix_close, pd.DataFrame):
            vix_close = vix_close.iloc[:, 0]
        vix_std = vix_close.rolling(window=self.vix_std_period).std()

        # Create figure with 3 subplots
        fig, axes = Visualizer.create_figure(n_subplots=3, figsize=(15, 12))

        # Subplot 1: Price, 52W High, and 200-day SMA
        ax1 = axes[0]
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        ax1.plot(df.index, close_series, label='SPY Price', color='blue', linewidth=1.5)
        ax1.plot(df.index, df['High_52W'], label='52-Week High', color='green',
                linewidth=1.5, linestyle='--', alpha=0.7)
        ax1.plot(df.index, df['SMA_200'], label='200-day SMA', color='orange',
                linewidth=2, linestyle='--')

        # Mark RISK_OFF signals
        risk_off = df[df['Signal'] == 'RISK_OFF']
        if not risk_off.empty:
            for date in risk_off.index:
                price = close_series.loc[date]
                ax1.plot(date, price, 'v', color='red', markersize=12,
                        label='RISK OFF' if date == risk_off.index[0] else '', zorder=5)

        # Shade warning periods
        warning_mask = df['Risk_Level'] == 'WARNING'
        ax1.fill_between(df.index, close_series.min(), close_series.max(),
                         where=warning_mask, alpha=0.1, color='yellow', label='Warning Period')

        risk_mask = df['Risk_Level'] == 'RISK_OFF'
        ax1.fill_between(df.index, close_series.min(), close_series.max(),
                         where=risk_mask, alpha=0.2, color='red', label='Risk-Off Period')

        ax1.set_title('Risk Management - Price, 52W High, and 200-day SMA', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax1)

        # Subplot 2: VIX Standard Deviation
        ax2 = axes[1]
        ax2.plot(vix_std.index, vix_std, label=f'VIX {self.vix_std_period}D StdDev',
                color='purple', linewidth=1.5)
        ax2.axhline(y=self.vix_std_threshold, color='red', linestyle='--',
                   linewidth=2, label=f'Threshold ({self.vix_std_threshold})')

        # Mark VIX warnings
        vix_warnings = df[df['Warning_VIX'] == True]
        if not vix_warnings.empty:
            for date in vix_warnings.index:
                if date in vix_std.index:
                    ax2.plot(date, vix_std.loc[date], 'o', color='red', markersize=6,
                            alpha=0.5)

        ax2.set_title('VIX Standard Deviation (Low Volatility Warning)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('VIX StdDev', fontsize=12)
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax2)

        # Subplot 3: Percentage Drop from 52W High and Days to Drop
        ax3 = axes[2]
        pct_drop = df['Pct_Drop'] * 100

        ax3.plot(df.index, pct_drop, label='% Drop from 52W High', color='darkred', linewidth=1.5)
        ax3.axhline(y=-self.drop_pct * 100, color='red', linestyle='--',
                   linewidth=2, label=f'{self.drop_pct*100}% Drop Threshold')

        # Mark canary warnings
        canary_warnings = df[df['Warning_Canary'] == True]
        if not canary_warnings.empty:
            for date in canary_warnings.index:
                ax3.plot(date, pct_drop.loc[date], 'o', color='orange', markersize=6,
                        alpha=0.5, label='Canary Warning' if date == canary_warnings.index[0] else '')

        ax3.fill_between(df.index, 0, pct_drop, where=(pct_drop < -self.drop_pct * 100),
                        alpha=0.2, color='red', label='Below Threshold')

        ax3.set_title('Market Decline Speed (Canary Signal)', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Drop from 52W High (%)', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.legend(loc='best', fontsize=10)
        ax3.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax3)

        Visualizer.save_or_show(fig, save_path)
