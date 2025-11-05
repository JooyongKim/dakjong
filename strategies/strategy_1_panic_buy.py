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
from utils.visualizer import Visualizer
import matplotlib.pyplot as plt


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

    def plot(self, nyse_breadth_data: pd.DataFrame, market_data: pd.DataFrame, save_path: str = None):
        """
        Visualize strategy indicators and signals.

        Args:
            nyse_breadth_data: NYSE breadth data
            market_data: Market data (SPY)
            save_path: Optional path to save the figure
        """
        # Generate signals
        df = self.generate_signals(nyse_breadth_data, market_data)

        # Flatten multi-index if present
        market_df = market_data.copy()
        if isinstance(market_df.columns, pd.MultiIndex):
            market_df.columns = market_df.columns.get_level_values(0)

        close_series = market_df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        # Create figure with 4 subplots
        fig, axes = Visualizer.create_figure(n_subplots=4, figsize=(15, 14))

        # Subplot 1: Market Price
        ax1 = axes[0]
        ax1.plot(market_df.index, close_series, label=f'{self.target_asset} Price',
                color='blue', linewidth=1.5)

        # Mark BUY signals
        buy_signals = df[df['Signal'] == 'BUY']
        if not buy_signals.empty:
            for date in buy_signals.index:
                if date in close_series.index:
                    price = close_series.loc[date]
                    ax1.plot(date, price, '^', color='green', markersize=15,
                            label='BUY Signal' if date == buy_signals.index[0] else '', zorder=5)
                    ax1.axvline(x=date, color='green', linestyle='--', alpha=0.3, linewidth=1)

        ax1.set_title(f'Strategy 1 - Market Panic Buy Signals', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax1)

        # Subplot 2: NYSE New Lows Ratio
        ax2 = axes[1]
        if 'NL_MA' in df.columns:
            ax2.plot(df.index, df['NL_MA'], label=f'New Lows {self.nl_ma_period}D MA',
                    color='red', linewidth=1.5)
            ax2.axhline(y=self.nl_threshold, color='darkred', linestyle='--',
                       linewidth=2, label=f'Threshold ({self.nl_threshold})')

            # Mark when threshold is breached
            breach_mask = df['NL_MA'] > self.nl_threshold
            ax2.fill_between(df.index, 0, df['NL_MA'], where=breach_mask,
                            alpha=0.3, color='red', label='Panic Level')

            ax2.set_title('NYSE New Lows Ratio (Panic Indicator)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('New Lows Ratio', fontsize=12)
            ax2.legend(loc='best', fontsize=10)
            ax2.grid(True, alpha=0.3)
            Visualizer.format_date_axis(ax2)
        else:
            ax2.text(0.5, 0.5, 'NYSE Breadth Data Not Available\n(Using Mock Data)',
                    ha='center', va='center', fontsize=14, color='red')
            ax2.set_title('NYSE New Lows Ratio', fontsize=14, fontweight='bold')

        # Subplot 3: STCO (Short-Term Cumulative Oscillator)
        ax3 = axes[2]
        if 'STCO' in df.columns:
            ax3.plot(df.index, df['STCO'], label='STCO',
                    color='purple', linewidth=1.5)
            ax3.axhline(y=self.stco_threshold, color='darkred', linestyle='--',
                       linewidth=2, label=f'Threshold ({self.stco_threshold})')

            # Mark when threshold is breached
            breach_mask = df['STCO'] > self.stco_threshold
            ax3.fill_between(df.index, 0, df['STCO'], where=breach_mask,
                            alpha=0.3, color='purple', label='Oversold')

            ax3.set_title('STCO - Short-Term Cumulative Oscillator', fontsize=14, fontweight='bold')
            ax3.set_ylabel('STCO Value', fontsize=12)
            ax3.legend(loc='best', fontsize=10)
            ax3.grid(True, alpha=0.3)
            Visualizer.format_date_axis(ax3)

        # Subplot 4: Panic Conditions Summary
        ax4 = axes[3]
        if 'Panic_Condition' in df.columns:
            panic_values = df['Panic_Condition'].astype(int)
            ax4.fill_between(df.index, 0, panic_values, where=(panic_values > 0),
                            step='post', alpha=0.4, color='orange', label='Panic Condition Met')

            # Mark confirmed BUY signals
            if not buy_signals.empty:
                for date in buy_signals.index:
                    if date in df.index:
                        ax4.axvline(x=date, color='green', linestyle='-',
                                   linewidth=2, alpha=0.7)

            ax4.set_title('Panic Condition Timeline', fontsize=14, fontweight='bold')
            ax4.set_ylabel('Condition Met', fontsize=12)
            ax4.set_xlabel('Date', fontsize=12)
            ax4.set_ylim(-0.1, 1.5)
            ax4.legend(loc='best', fontsize=10)
            ax4.grid(True, alpha=0.3)
            Visualizer.format_date_axis(ax4)

        Visualizer.save_or_show(fig, save_path)
