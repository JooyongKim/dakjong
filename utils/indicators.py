"""
Common technical indicators for strategy modules.
"""

import pandas as pd
import numpy as np
from typing import Optional


class Indicators:
    """
    Technical indicators commonly used across strategies.
    """

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average.

        Args:
            data: Price series
            period: Moving average period

        Returns:
            SMA series
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average.

        Args:
            data: Price series
            period: EMA period

        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range.

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period

        Returns:
            ATR series
        """
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Average True Range
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def macd_v(high: pd.Series, low: pd.Series, close: pd.Series,
               ema_short: int = 12, ema_long: int = 26, atr_period: int = 26) -> pd.Series:
        """
        MACD-V (Volatility-Normalized MACD) as per Spiroglou (2022).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            ema_short: Short EMA period
            ema_long: Long EMA period
            atr_period: ATR period

        Returns:
            MACD-V series
        """
        ema_short_series = Indicators.ema(close, ema_short)
        ema_long_series = Indicators.ema(close, ema_long)
        atr_series = Indicators.atr(high, low, close, atr_period)

        # Avoid division by zero
        atr_series = atr_series.replace(0, np.nan)

        macd_v = ((ema_short_series - ema_long_series) / atr_series) * 100

        return macd_v

    @staticmethod
    def rolling_high(data: pd.Series, period: int) -> pd.Series:
        """
        Rolling maximum (highest high over period).

        Args:
            data: Price series
            period: Lookback period

        Returns:
            Rolling high series
        """
        return data.rolling(window=period).max()

    @staticmethod
    def rolling_low(data: pd.Series, period: int) -> pd.Series:
        """
        Rolling minimum (lowest low over period).

        Args:
            data: Price series
            period: Lookback period

        Returns:
            Rolling low series
        """
        return data.rolling(window=period).min()

    @staticmethod
    def volatility(returns: pd.Series, period: int) -> pd.Series:
        """
        Rolling volatility (standard deviation of returns).

        Args:
            returns: Return series
            period: Rolling window period

        Returns:
            Volatility series
        """
        return returns.rolling(window=period).std()

    @staticmethod
    def momentum(prices: pd.Series, period: int) -> pd.Series:
        """
        Price momentum (rate of change).

        Args:
            prices: Price series
            period: Lookback period

        Returns:
            Momentum series (as percentage change)
        """
        return (prices / prices.shift(period)) - 1
