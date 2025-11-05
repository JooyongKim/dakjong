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
from utils.visualizer import Visualizer
import matplotlib.pyplot as plt


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

            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate 200-day SMA
            close_series = df['Close']
            if isinstance(close_series, pd.DataFrame):
                close_series = close_series.iloc[:, 0]
            df['SMA_200'] = Indicators.sma(close_series, self.sma_period)

            # Generate signals
            df['Signal'] = 'LEVERAGE_OFF'
            df['Price_vs_SMA'] = close_series - df['SMA_200']
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
                            'price_vs_sma_pct': round(((current_price / current_sma) - 1) * 100, 2),
                            'recommended_action': f"매수: SPXL (3배 레버리지 ETF) 또는 {self.target_asset}에 {self.leverage_multiple}배 레버리지 적용",
                            'action_en': f"BUY: SPXL (3x leveraged ETF) or apply {self.leverage_multiple}x leverage to {self.target_asset}"
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
                            'price_vs_sma_pct': round(((current_price / current_sma) - 1) * 100, 2),
                            'recommended_action': f"매도: 레버리지 포지션 청산 (SPXL 등), {self.target_asset} 1배로 전환 또는 현금/SHY 보유",
                            'action_en': f"SELL: Close leveraged positions (SPXL), switch to 1x {self.target_asset} or hold cash/SHY"
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

    def plot(self, market_data: pd.DataFrame, save_path: str = None):
        """
        Visualize strategy indicators and signals.

        Args:
            market_data: Market data used for signal generation
            save_path: Optional path to save the figure
        """
        # Generate signals if not already done
        df = self.generate_signals(market_data)

        # Create figure with 2 subplots
        fig, axes = Visualizer.create_figure(n_subplots=2, figsize=(15, 10))

        # Subplot 1: Price vs SMA with signals
        ax1 = axes[0]
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        sma_series = df['SMA_200']

        ax1.plot(df.index, close_series, label=f'{self.target_asset} Price',
                color='blue', linewidth=1.5, alpha=0.8)
        ax1.plot(df.index, sma_series, label=f'{self.sma_period}-day SMA',
                color='orange', linewidth=2, linestyle='--')

        # Mark LEVERAGE_ON and LEVERAGE_OFF signals
        leverage_on = df[df['Signal'] == 'LEVERAGE_ON']
        leverage_off = df[df['Signal'] == 'LEVERAGE_OFF']

        if not leverage_on.empty:
            # Show transitions to LEVERAGE_ON (not all points, just changes)
            transitions_on = leverage_on.index[0:1].tolist()
            for i in range(1, len(leverage_on)):
                if leverage_on.index[i] - leverage_on.index[i-1] > pd.Timedelta(days=10):
                    transitions_on.append(leverage_on.index[i])

            for date in transitions_on:
                price = close_series.loc[date]
                ax1.plot(date, price, '^', color='green', markersize=12,
                        label='LEVERAGE ON' if date == transitions_on[0] else '', zorder=5)

        if not leverage_off.empty:
            # Show transitions to LEVERAGE_OFF
            transitions_off = []
            prev_signal = None
            for date in df.index:
                current = df.loc[date, 'Signal']
                if current == 'LEVERAGE_OFF' and prev_signal == 'LEVERAGE_ON':
                    transitions_off.append(date)
                prev_signal = current

            for date in transitions_off:
                if date in close_series.index:
                    price = close_series.loc[date]
                    ax1.plot(date, price, 'v', color='red', markersize=12,
                            label='LEVERAGE OFF' if date == transitions_off[0] else '', zorder=5)

        # Shade bull/bear regions
        bull_mask = df['Signal'] == 'LEVERAGE_ON'
        ax1.fill_between(df.index, close_series.min(), close_series.max(),
                         where=bull_mask, alpha=0.1, color='green', label='Bull Regime')

        ax1.set_title(f'{self.strategy_name} - Price vs {self.sma_period}-day SMA',
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax1)

        # Subplot 2: Price vs SMA differential (%)
        ax2 = axes[1]
        price_vs_sma_pct = ((close_series / sma_series) - 1) * 100

        ax2.plot(df.index, price_vs_sma_pct, label='Price vs SMA (%)',
                color='purple', linewidth=1.5)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=2, label='SMA Level')
        ax2.fill_between(df.index, 0, price_vs_sma_pct,
                         where=(price_vs_sma_pct > 0), alpha=0.3, color='green',
                         label='Above SMA (Bull)')
        ax2.fill_between(df.index, 0, price_vs_sma_pct,
                         where=(price_vs_sma_pct < 0), alpha=0.3, color='red',
                         label='Below SMA (Bear)')

        ax2.set_title('Price vs SMA Differential', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Differential (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax2)

        Visualizer.save_or_show(fig, save_path)
