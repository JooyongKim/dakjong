"""
Strategy 4: Quantamental Sector Rotation

Based on: Cain & Connors (2020); Giordano (2018)

Selects top-performing sectors based on momentum and volatility.
Applies market trend filter (200-day SMA).

Generates sector allocation signals or CASH signal when market is bearish.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import calendar

from .base_strategy import BaseStrategy
from utils.indicators import Indicators
from utils.visualizer import Visualizer
import matplotlib.pyplot as plt


class SectorRotationStrategy(BaseStrategy):
    """
    Strategy 4: Quantamental Sector Rotation.

    Combines momentum and volatility factors to select top sectors:
    1. Calculate momentum over specified period
    2. Calculate volatility over specified period
    3. Rank sectors by momentum (high) and volatility (low)
    4. Select top N sectors
    5. Apply market filter (SPY vs 200-day SMA)
    6. Generate allocation signals or CASH signal

    Rebalances on specified frequency (monthly or quarterly).
    """

    def __init__(self,
                 use_fundamentals: bool = False,
                 momentum_period: int = 6,
                 momentum_skip_months: int = 1,
                 volatility_period: int = 100,
                 top_n_sectors: int = 3,
                 weighting_method: str = 'EW',
                 market_filter_sma: int = 200,
                 rebalance_frequency: str = 'Monthly'):
        """
        Initialize Sector Rotation Strategy.

        Args:
            use_fundamentals: Use fundamental screening (not implemented)
            momentum_period: Momentum calculation period in months (default: 6)
            momentum_skip_months: Skip recent months for momentum (default: 1)
            volatility_period: Volatility calculation period in days (default: 100)
            top_n_sectors: Number of sectors to select (default: 3)
            weighting_method: 'EW' (equal weight) or 'IV' (inverse volatility) (default: 'EW')
            market_filter_sma: Market filter SMA period (default: 200)
            rebalance_frequency: 'Monthly' or 'Quarterly' (default: 'Monthly')
        """
        super().__init__(
            strategy_id="Strategy_4_Sector_Rotation",
            strategy_name="Quantamental Sector Rotation"
        )

        self.use_fundamentals = use_fundamentals
        self.momentum_period = momentum_period
        self.momentum_skip_months = momentum_skip_months
        self.volatility_period = volatility_period
        self.top_n_sectors = top_n_sectors
        self.weighting_method = weighting_method
        self.market_filter_sma = market_filter_sma
        self.rebalance_frequency = rebalance_frequency

    def _is_rebalance_date(self, date: datetime, prev_date: datetime = None) -> bool:
        """
        Check if date is a rebalancing date.

        Args:
            date: Current date
            prev_date: Previous date

        Returns:
            True if rebalancing should occur
        """
        if prev_date is None:
            return True

        if self.rebalance_frequency == 'Monthly':
            # Rebalance on last trading day of month
            return date.month != prev_date.month
        elif self.rebalance_frequency == 'Quarterly':
            # Rebalance on last trading day of quarter
            return (date.month - 1) // 3 != (prev_date.month - 1) // 3
        else:
            return False

    def generate_signals(self,
                        sector_data: Dict[str, pd.DataFrame],
                        market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate sector rotation signals.

        Args:
            sector_data: Dictionary of sector ETF DataFrames (11 sectors)
            market_data: Market index data (SPY) for trend filter

        Returns:
            DataFrame with rebalancing signals
        """
        try:
            # Validate input data
            if not sector_data or market_data.empty:
                raise ValueError("Input data cannot be empty")

            # Calculate market filter (200-day SMA)
            market_df = market_data.copy()

            # Flatten multi-index columns if present
            if isinstance(market_df.columns, pd.MultiIndex):
                market_df.columns = market_df.columns.get_level_values(0)

            close_series = market_df['Close']
            if isinstance(close_series, pd.DataFrame):
                close_series = close_series.iloc[:, 0]
            market_df['SMA_200'] = Indicators.sma(close_series, self.market_filter_sma)

            # Get common date range
            all_dates = market_df.index
            valid_dates = all_dates[self.market_filter_sma:]

            # Create results dataframe
            results = []

            prev_date = None
            for date in valid_dates:
                # Check if this is a rebalancing date
                if not self._is_rebalance_date(date, prev_date):
                    prev_date = date
                    continue

                date_str = date.strftime('%Y-%m-%d')

                # Check market filter
                market_price = market_df.loc[date, 'Close']
                if isinstance(market_price, pd.Series):
                    market_price = market_price.iloc[0]
                market_sma = market_df.loc[date, 'SMA_200']
                if isinstance(market_sma, pd.Series):
                    market_sma = market_sma.iloc[0]

                if market_price < market_sma:
                    # Bear market - go to cash
                    signal = self._create_signal_output(
                        date=date_str,
                        signal='CASH',
                        asset='CASH',
                        details={
                            'reason': 'Market_Below_SMA',
                            'market_price': round(market_price, 2),
                            'sma_200': round(market_sma, 2)
                        }
                    )
                    results.append(signal)
                    self.save_signal(signal)
                    prev_date = date
                    continue

                # Bull market - select sectors
                sector_scores = {}

                for ticker, data in sector_data.items():
                    if data.empty or date not in data.index:
                        continue

                    try:
                        # Flatten multi-index columns if present
                        sector_df = data.copy()
                        if isinstance(sector_df.columns, pd.MultiIndex):
                            sector_df.columns = sector_df.columns.get_level_values(0)

                        # Get Close series
                        close_series = sector_df['Close']
                        if isinstance(close_series, pd.DataFrame):
                            close_series = close_series.iloc[:, 0]

                        # Calculate momentum
                        # Lookback period: momentum_period months + skip month
                        momentum_days = 21 * (self.momentum_period + self.momentum_skip_months)
                        skip_days = 21 * self.momentum_skip_months

                        if len(sector_df.loc[:date]) < momentum_days:
                            continue

                        # Get prices
                        current_idx = sector_df.index.get_loc(date)
                        if current_idx < momentum_days:
                            continue

                        price_current = close_series.iloc[current_idx - skip_days]
                        price_past = close_series.iloc[current_idx - momentum_days]

                        momentum = (price_current / price_past) - 1

                        # Calculate volatility
                        returns = close_series.pct_change()
                        volatility = returns.loc[:date].iloc[-self.volatility_period:].std()

                        sector_scores[ticker] = {
                            'momentum': momentum,
                            'volatility': volatility
                        }

                    except Exception as e:
                        continue

                if len(sector_scores) < self.top_n_sectors:
                    # Not enough sectors with valid data
                    prev_date = date
                    continue

                # Rank sectors
                df_scores = pd.DataFrame(sector_scores).T

                # Rank by momentum (higher is better) and volatility (lower is better)
                df_scores['Rank_Momentum'] = df_scores['momentum'].rank(ascending=False)
                df_scores['Rank_Volatility'] = df_scores['volatility'].rank(ascending=True)

                # Combined rank (lower is better)
                df_scores['Total_Rank'] = df_scores['Rank_Momentum'] + df_scores['Rank_Volatility']

                # Select top N sectors
                top_sectors = df_scores.nsmallest(self.top_n_sectors, 'Total_Rank')

                # Calculate weights
                if self.weighting_method == 'EW':
                    weights = [1.0 / self.top_n_sectors] * self.top_n_sectors
                elif self.weighting_method == 'IV':
                    # Inverse volatility weighting
                    inverse_vol = 1.0 / top_sectors['volatility']
                    weights = (inverse_vol / inverse_vol.sum()).tolist()
                else:
                    weights = [1.0 / self.top_n_sectors] * self.top_n_sectors

                # Create signal
                selected_tickers = top_sectors.index.tolist()
                signal = self._create_signal_output(
                    date=date_str,
                    signal='HOLD_SECTORS',
                    asset='SECTORS',
                    details={
                        'reason': 'Sector_Rotation_Rebalance',
                        'sectors_list': selected_tickers,
                        'weights_list': [round(w, 4) for w in weights],
                        'momentum_values': {
                            ticker: round(top_sectors.loc[ticker, 'momentum'], 4)
                            for ticker in selected_tickers
                        },
                        'volatility_values': {
                            ticker: round(top_sectors.loc[ticker, 'volatility'], 4)
                            for ticker in selected_tickers
                        }
                    }
                )

                results.append(signal)
                self.save_signal(signal)
                prev_date = date

            # Convert to DataFrame
            if results:
                results_df = pd.DataFrame(results)
                return results_df
            else:
                return pd.DataFrame()

        except Exception as e:
            raise Exception(f"Error generating signals for {self.strategy_id}: {str(e)}")

    def get_latest_signal(self) -> Dict[str, Any]:
        """
        Get the most recent signal.

        Returns:
            Latest signal dictionary or CASH signal
        """
        if self.signals_history:
            return self.signals_history[-1]
        else:
            return self._create_signal_output(
                date=datetime.now().strftime('%Y-%m-%d'),
                signal='CASH',
                asset='CASH',
                details={'reason': 'No rebalancing data available'}
            )

    def reset_state(self):
        """Reset strategy state (for backtesting purposes)."""
        self.clear_history()

    def plot(self, sector_data: Dict[str, pd.DataFrame], market_data: pd.DataFrame, save_path: str = None):
        """
        Visualize sector rotation strategy indicators and signals.

        Args:
            sector_data: Dictionary of sector ETF DataFrames
            market_data: Market index data (SPY)
            save_path: Optional path to save the figure
        """
        # Generate signals
        df = self.generate_signals(sector_data, market_data)

        # Flatten market data
        market_df = market_data.copy()
        if isinstance(market_df.columns, pd.MultiIndex):
            market_df.columns = market_df.columns.get_level_values(0)

        close_series = market_df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        # Create figure with 3 subplots
        fig, axes = Visualizer.create_figure(n_subplots=3, figsize=(15, 12))

        # Subplot 1: Market filter (SPY vs 200-day SMA)
        ax1 = axes[0]
        sma_200 = Indicators.sma(close_series, self.market_filter_sma)

        ax1.plot(market_df.index, close_series, label='SPY Price', color='blue', linewidth=1.5)
        ax1.plot(market_df.index, sma_200, label='200-day SMA',
                color='orange', linewidth=2, linestyle='--')

        # Shade bull/bear periods
        bull_mask = close_series > sma_200
        ax1.fill_between(market_df.index, close_series.min(), close_series.max(),
                        where=bull_mask, alpha=0.1, color='green', label='Bull Market')
        bear_mask = close_series < sma_200
        ax1.fill_between(market_df.index, close_series.min(), close_series.max(),
                        where=bear_mask, alpha=0.1, color='red', label='Bear Market (CASH)')

        ax1.set_title('Strategy 4 - Market Filter (SPY vs 200-day SMA)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax1)

        # Subplot 2: Sector momentum comparison
        ax2 = axes[1]

        # Calculate 6-month momentum for each sector
        for ticker, data in sector_data.items():
            if data.empty:
                continue

            sector_df = data.copy()
            if isinstance(sector_df.columns, pd.MultiIndex):
                sector_df.columns = sector_df.columns.get_level_values(0)

            close_s = sector_df['Close']
            if isinstance(close_s, pd.DataFrame):
                close_s = close_s.iloc[:, 0]

            # Calculate 6-month momentum
            momentum = Indicators.momentum(close_s, period=126) * 100

            ax2.plot(sector_df.index, momentum, label=ticker, linewidth=1.2, alpha=0.7)

        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.set_title('Sector 6-Month Momentum Comparison', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Momentum (%)', fontsize=12)
        ax2.legend(loc='best', fontsize=8, ncol=2)
        ax2.grid(True, alpha=0.3)
        Visualizer.format_date_axis(ax2)

        # Subplot 3: Selected sectors over time
        ax3 = axes[2]

        if not df.empty:
            # Extract rebalance dates and selected sectors
            rebalance_dates = []
            selected_sectors_timeline = {}

            for idx, row in df.iterrows():
                if row['signal'] == 'HOLD_SECTORS':
                    date = pd.to_datetime(row['date'])
                    sectors = row['details']['sectors_list']
                    rebalance_dates.append(date)
                    selected_sectors_timeline[date] = sectors

            # Plot selected sectors as timeline
            all_sectors = list(sector_data.keys())
            sector_colors = plt.cm.tab10(range(len(all_sectors)))
            sector_to_color = {sector: color for sector, color in zip(all_sectors, sector_colors)}

            # Create timeline visualization
            for i, (date, sectors) in enumerate(selected_sectors_timeline.items()):
                # Find next rebalance date
                next_date = rebalance_dates[i+1] if i+1 < len(rebalance_dates) else market_df.index[-1]

                # Draw horizontal bars for each selected sector
                for j, sector in enumerate(sectors):
                    ax3.barh(j, (next_date - date).days, left=date, height=0.8,
                            color=sector_to_color.get(sector, 'gray'),
                            alpha=0.6, label=sector if i == 0 else '')

                # Mark rebalance date
                if i > 0:  # Skip first date
                    ax3.axvline(x=date, color='red', linestyle='--', alpha=0.5, linewidth=1)

            ax3.set_title('Selected Sectors Timeline (Rebalancing)', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Sector Rank', fontsize=12)
            ax3.set_xlabel('Date', fontsize=12)
            ax3.set_yticks(range(self.top_n_sectors))
            ax3.set_yticklabels([f'Top {i+1}' for i in range(self.top_n_sectors)])

            # Create custom legend with unique sectors
            handles = []
            labels = []
            seen_sectors = set()
            for sector in all_sectors:
                if sector not in seen_sectors:
                    handles.append(plt.Rectangle((0,0),1,1, fc=sector_to_color[sector], alpha=0.6))
                    labels.append(sector)
                    seen_sectors.add(sector)

            ax3.legend(handles, labels, loc='upper left', bbox_to_anchor=(1, 1),
                      fontsize=9, ncol=1)
            ax3.grid(True, alpha=0.3, axis='x')
            Visualizer.format_date_axis(ax3)
        else:
            ax3.text(0.5, 0.5, 'No sector rotation data available',
                    ha='center', va='center', fontsize=14, color='red')

        Visualizer.save_or_show(fig, save_path)
