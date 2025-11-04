"""
Data loader utility for fetching market data from various sources.
"""

import yfinance as yf
import pandas as pd
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
        Placeholder for NYSE breadth data.

        Note: NYSE breadth data (new lows, advance/decline ratios) is not available
        through yfinance and requires a separate data source (e.g., paid API or web scraping).

        Returns:
            Empty DataFrame with expected columns
        """
        print("WARNING: NYSE breadth data requires a separate data source.")
        print("This method returns mock data for demonstration purposes.")

        # Create mock data structure
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        mock_data = pd.DataFrame({
            'NewLows_Ratio': 0.15,  # Mock value
            'UpVolume_Ratio': 0.55,  # Mock value
            'Advancing_Ratio': 0.52  # Mock value
        }, index=date_range)

        return mock_data
