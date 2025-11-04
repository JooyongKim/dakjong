"""
Example usage of individual strategy modules.

This script demonstrates how to use each strategy independently.
"""

import json
from datetime import datetime, timedelta
from utils.data_loader import DataLoader
from strategies import (
    PanicBuyStrategy,
    RiskManagementStrategy,
    LeverageStrategy,
    SectorRotationStrategy,
    MACDVStrategy
)


def example_strategy_1():
    """
    Example: Strategy 1 - Market Panic Identification and Bottom Buying
    """
    print("\n=== Example: Strategy 1 - Panic Buy ===\n")

    # Initialize data loader (last 2 years)
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    data_loader = DataLoader(start_date=start_date)

    # Load required data
    spy_data = data_loader.load_market_index('SPY')
    nyse_breadth = data_loader.get_nyse_breadth_data()  # Note: Returns mock data

    # Initialize strategy with custom parameters
    strategy = PanicBuyStrategy(
        nl_threshold=0.45,  # Lower threshold for more signals
        stco_threshold=85,
        entry_logic='Delayed',
        delay_days=5
    )

    # Generate signals
    signals_df = strategy.generate_signals(
        nyse_breadth_data=nyse_breadth,
        market_data=spy_data
    )

    # Get latest signal
    latest = strategy.get_latest_signal()
    print(json.dumps(latest, indent=2))


def example_strategy_2():
    """
    Example: Strategy 2 - Risk Management
    """
    print("\n=== Example: Strategy 2 - Risk Management ===\n")

    # Initialize data loader
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    data_loader = DataLoader(start_date=start_date)

    # Load required data
    spy_data = data_loader.load_market_index('SPY')
    vix_data = data_loader.load_vix()

    # Initialize strategy
    strategy = RiskManagementStrategy(
        vix_std_threshold=0.90,  # Adjusted threshold
        drop_pct=0.07,  # 7% drop
        canary_days=20
    )

    # Generate signals
    signals_df = strategy.generate_signals(
        vix_data=vix_data,
        market_data=spy_data
    )

    # Get latest signal
    latest = strategy.get_latest_signal()
    print(json.dumps(latest, indent=2))


def example_strategy_3():
    """
    Example: Strategy 3 - Trend-Based Leverage
    """
    print("\n=== Example: Strategy 3 - Leverage ===\n")

    # Initialize data loader
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    data_loader = DataLoader(start_date=start_date)

    # Load required data
    spy_data = data_loader.load_market_index('SPY')

    # Initialize strategy
    strategy = LeverageStrategy(
        sma_period=200,
        leverage_multiple=2.0  # 2x leverage
    )

    # Generate signals
    signals_df = strategy.generate_signals(market_data=spy_data)

    # Get latest signal
    latest = strategy.get_latest_signal()
    print(json.dumps(latest, indent=2))


def example_strategy_4():
    """
    Example: Strategy 4 - Sector Rotation
    """
    print("\n=== Example: Strategy 4 - Sector Rotation ===\n")

    # Initialize data loader
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    data_loader = DataLoader(start_date=start_date)

    # Load required data
    spy_data = data_loader.load_market_index('SPY')
    sector_data = data_loader.load_sector_etfs()

    # Initialize strategy
    strategy = SectorRotationStrategy(
        momentum_period=3,  # 3 months
        top_n_sectors=5,  # Top 5 sectors
        weighting_method='IV',  # Inverse volatility weighting
        rebalance_frequency='Quarterly'
    )

    # Generate signals
    signals_df = strategy.generate_signals(
        sector_data=sector_data,
        market_data=spy_data
    )

    # Get latest signal
    latest = strategy.get_latest_signal()
    print(json.dumps(latest, indent=2))


def example_strategy_5():
    """
    Example: Strategy 5 - MACD-V Momentum
    """
    print("\n=== Example: Strategy 5 - MACD-V ===\n")

    # Initialize data loader
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    data_loader = DataLoader(start_date=start_date)

    # Load required data
    asset_universe = ['SPY', 'QQQ', 'TLT', 'GLD']
    asset_data = data_loader.load_asset_universe(asset_universe)

    # Initialize strategy with custom thresholds
    strategy = MACDVStrategy(
        ema_short=10,
        ema_long=20,
        atr_period=20,
        thresholds={
            'Overbought': 200,
            'Rallying': 75,
            'Ranging_Upper': 75,
            'Ranging_Lower': -75,
            'Reversing': -200,
            'Oversold': -200
        }
    )

    # Generate signals
    signals_df = strategy.generate_signals(asset_data=asset_data)

    # Get latest signal
    latest = strategy.get_latest_signal()
    print(json.dumps(latest, indent=2))


if __name__ == "__main__":
    print("="*80)
    print("Investment Strategy Signal Generators - Example Usage")
    print("="*80)

    # Run individual examples
    # Uncomment the strategy you want to test

    # example_strategy_1()
    # example_strategy_2()
    example_strategy_3()  # Simplest to test
    # example_strategy_4()
    # example_strategy_5()

    print("\n" + "="*80)
    print("Done!")
    print("="*80)
