"""
Visualization utilities for strategy signals and indicators.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime


class Visualizer:
    """
    Utility class for visualizing strategy indicators and signals.
    """

    @staticmethod
    def setup_plot_style():
        """Set up consistent plot styling."""
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.figsize'] = (15, 10)
        plt.rcParams['font.size'] = 10

    @staticmethod
    def format_date_axis(ax):
        """Format date axis for better readability."""
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    @staticmethod
    def add_signal_markers(ax, dates: pd.DatetimeIndex, prices: pd.Series,
                          signals: pd.DataFrame, signal_type: str,
                          color: str = 'red', marker: str = '^',
                          label: str = 'Signal'):
        """
        Add signal markers to a price chart.

        Args:
            ax: Matplotlib axis
            dates: DatetimeIndex of all dates
            prices: Price series
            signals: DataFrame with signals
            signal_type: Type of signal to mark (e.g., 'BUY', 'RISK_OFF')
            color: Marker color
            marker: Marker style
            label: Legend label
        """
        if signals.empty:
            return

        signal_dates = pd.to_datetime(signals[signals['signal'] == signal_type]['date'])

        for sig_date in signal_dates:
            if sig_date in dates:
                idx = dates.get_loc(sig_date)
                ax.plot(sig_date, prices.iloc[idx], marker,
                       color=color, markersize=15, label=label, zorder=5)
                # Add vertical line
                ax.axvline(x=sig_date, color=color, linestyle='--',
                          alpha=0.3, linewidth=1)

    @staticmethod
    def save_or_show(fig, save_path: Optional[str] = None):
        """
        Save figure to file or show it.

        Args:
            fig: Matplotlib figure
            save_path: Path to save figure (if None, shows instead)
        """
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        else:
            plt.show()

    @staticmethod
    def plot_price_with_sma(ax, dates: pd.DatetimeIndex, prices: pd.Series,
                           sma: pd.Series, title: str = "Price vs SMA"):
        """
        Plot price with moving average.

        Args:
            ax: Matplotlib axis
            dates: DatetimeIndex
            prices: Price series
            sma: SMA series
            title: Chart title
        """
        ax.plot(dates, prices, label='Price', color='blue', linewidth=1.5)
        ax.plot(dates, sma, label=f'SMA', color='orange',
               linewidth=2, linestyle='--')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    @staticmethod
    def plot_indicator(ax, dates: pd.DatetimeIndex, indicator: pd.Series,
                      title: str, ylabel: str, color: str = 'green',
                      threshold: Optional[float] = None,
                      threshold_label: Optional[str] = None):
        """
        Plot a technical indicator.

        Args:
            ax: Matplotlib axis
            dates: DatetimeIndex
            indicator: Indicator series
            title: Chart title
            ylabel: Y-axis label
            color: Line color
            threshold: Horizontal threshold line
            threshold_label: Label for threshold
        """
        ax.plot(dates, indicator, label=ylabel, color=color, linewidth=1.5)

        if threshold is not None:
            ax.axhline(y=threshold, color='red', linestyle='--',
                      linewidth=2, label=threshold_label or f'Threshold ({threshold})')

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    @staticmethod
    def create_figure(n_subplots: int = 3, figsize: tuple = (15, 12)):
        """
        Create figure with subplots.

        Args:
            n_subplots: Number of subplots
            figsize: Figure size (width, height)

        Returns:
            fig, axes
        """
        fig, axes = plt.subplots(n_subplots, 1, figsize=figsize)
        if n_subplots == 1:
            axes = [axes]
        return fig, axes
