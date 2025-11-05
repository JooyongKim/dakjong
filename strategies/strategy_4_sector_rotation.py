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
                        # Calculate momentum
                        # Lookback period: momentum_period months + skip month
                        momentum_days = 21 * (self.momentum_period + self.momentum_skip_months)
                        skip_days = 21 * self.momentum_skip_months

                        if len(data.loc[:date]) < momentum_days:
                            continue

                        # Get prices
                        current_idx = data.index.get_loc(date)
                        if current_idx < momentum_days:
                            continue

                        price_current = data['Close'].iloc[current_idx - skip_days]
                        price_past = data['Close'].iloc[current_idx - momentum_days]

                        momentum = (price_current / price_past) - 1

                        # Calculate volatility
                        returns = data['Close'].pct_change()
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
