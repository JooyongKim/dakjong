"""
Data loader utility for fetching market data from various sources.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import warnings

warnings.filterwarnings('ignore')


class DataLoader:
    """
    Data loader for fetching market data using yfinance.

    Supports:
    - Market indices (S&P 500, NASDAQ, Dow Jones)
    - VIX data
    - Sector ETFs
    - Safe haven ETFs
    """

    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Initialize DataLoader with date range.

        Args:
            start_date: Start date in 'YYYY-MM-DD' format. Defaults to 5 years ago.
            end_date: End date in 'YYYY-MM-DD' format. Defaults to today.
        """
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date

        if start_date is None:
            start = datetime.now() - timedelta(days=5*365)
            self.start_date = start.strftime('%Y-%m-%d')
        else:
            self.start_date = start_date

    def load_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Load OHLCV data for a single ticker.

        Args:
            ticker: Ticker symbol (e.g., 'SPY', '^VIX')

        Returns:
            DataFrame with columns: Open, High, Low, Close, Adj Close, Volume

        Raises:
            Exception: If data loading fails
        """
        try:
            data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False,
                auto_adjust=False
            )

            if data.empty:
                raise Exception(f"No data retrieved for ticker: {ticker}")

            return data

        except Exception as e:
            raise Exception(f"Failed to load data for {ticker}: {str(e)}")

    def load_multiple_tickers(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load OHLCV data for multiple tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        result = {}

        for ticker in tickers:
            try:
                result[ticker] = self.load_ticker(ticker)
            except Exception as e:
                print(f"Warning: {e}")
                result[ticker] = pd.DataFrame()

        return result

    def load_market_index(self, index: str = 'SPY') -> pd.DataFrame:
        """
        Load market index data.

        Args:
            index: Index ticker ('SPY', '^GSPC', 'QQQ', '^NDX', 'DIA', '^DJI')

        Returns:
            DataFrame with OHLCV data
        """
        return self.load_ticker(index)

    def load_vix(self) -> pd.DataFrame:
        """
        Load VIX index data.

        Returns:
            DataFrame with VIX OHLCV data
        """
        return self.load_ticker('^VIX')

    def load_sector_etfs(self) -> Dict[str, pd.DataFrame]:
        """
        Load all 11 sector ETFs.

        Returns:
            Dictionary mapping sector ticker to DataFrame
        """
        sector_tickers = [
            'XLE',  # Energy
            'XLF',  # Financials
            'XLK',  # Technology
            'XLV',  # Health Care
            'XLI',  # Industrials
            'XLP',  # Consumer Staples
            'XLY',  # Consumer Discretionary
            'XLB',  # Materials
            'XLU',  # Utilities
            'XLRE', # Real Estate
            'XLC'   # Communication Services
        ]

        return self.load_multiple_tickers(sector_tickers)

    def load_safe_haven_etfs(self) -> Dict[str, pd.DataFrame]:
        """
        Load safe haven ETFs (short-term treasuries).

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        safe_haven_tickers = ['SHY', 'BIL', 'SHV']
        return self.load_multiple_tickers(safe_haven_tickers)

    def load_asset_universe(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load a custom universe of assets.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        return self.load_multiple_tickers(tickers)

    def get_nyse_breadth_data(self) -> pd.DataFrame:
        """
        Generate realistic mock NYSE breadth data based on SPY price movements.

        Note: NYSE breadth data (new lows, advance/decline ratios) is not available
        through yfinance and requires a separate data source (e.g., paid API or web scraping).

        This method creates mock data that correlates with market movements for
        demonstration purposes.

        Returns:
            DataFrame with mock NYSE breadth data
        """
        print("WARNING: NYSE breadth data requires a separate data source.")
        print("This method returns realistic mock data for demonstration purposes.")

        # Try to load SPY data to make mock data more realistic
        try:
            spy_data = self.load_market_index('SPY')

            # Flatten multi-index if present
            if isinstance(spy_data.columns, pd.MultiIndex):
                spy_data.columns = spy_data.columns.get_level_values(0)

            close_prices = spy_data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]

            # Calculate daily returns
            returns = close_prices.pct_change()

            # Calculate volatility
            volatility = returns.rolling(window=20).std()

            # Create mock NYSE breadth data that responds to market conditions
            # NewLows_Ratio: Higher when market drops sharply
            # Base value around 0.15, spikes to 0.50+ during selloffs
            newlows_base = 0.15
            newlows_ratio = newlows_base + np.maximum(0, -returns * 5) + volatility * 2
            newlows_ratio = np.clip(newlows_ratio, 0.05, 0.70)

            # UpVolume_Ratio: Lower during selloffs, higher during rallies
            # Base value around 0.55, drops to 0.30 during selloffs
            upvolume_base = 0.55
            upvolume_ratio = upvolume_base + returns * 2 - volatility
            upvolume_ratio = np.clip(upvolume_ratio, 0.25, 0.75)

            # Advancing_Ratio: Similar to UpVolume but slightly different pattern
            # Base value around 0.52
            advancing_base = 0.52
            advancing_ratio = advancing_base + returns * 2.5 - volatility * 0.5
            advancing_ratio = np.clip(advancing_ratio, 0.20, 0.80)

            # Add some noise for realism
            np.random.seed(42)
            noise_nl = np.random.normal(0, 0.02, len(newlows_ratio))
            noise_uv = np.random.normal(0, 0.03, len(upvolume_ratio))
            noise_ad = np.random.normal(0, 0.03, len(advancing_ratio))

            newlows_ratio += noise_nl
            upvolume_ratio += noise_uv
            advancing_ratio += noise_ad

            # Clip again after adding noise
            newlows_ratio = np.clip(newlows_ratio, 0.05, 0.70)
            upvolume_ratio = np.clip(upvolume_ratio, 0.25, 0.75)
            advancing_ratio = np.clip(advancing_ratio, 0.20, 0.80)

            mock_data = pd.DataFrame({
                'NewLows_Ratio': newlows_ratio,
                'UpVolume_Ratio': upvolume_ratio,
                'Advancing_Ratio': advancing_ratio
            }, index=spy_data.index)

        except Exception as e:
            # Fallback to simple mock data if SPY loading fails
            print(f"Could not load SPY data for realistic mock: {e}")
            date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')

            # Generate random but realistic-looking data
            np.random.seed(42)
            n_days = len(date_range)

            mock_data = pd.DataFrame({
                'NewLows_Ratio': np.clip(np.random.normal(0.15, 0.10, n_days), 0.05, 0.70),
                'UpVolume_Ratio': np.clip(np.random.normal(0.55, 0.08, n_days), 0.25, 0.75),
                'Advancing_Ratio': np.clip(np.random.normal(0.52, 0.08, n_days), 0.20, 0.80)
            }, index=date_range)

        return mock_data
