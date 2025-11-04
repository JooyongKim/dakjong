"""
Main execution script for independent investment strategy signal generators.

Allows running each strategy independently or all strategies together.
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

from utils.data_loader import DataLoader
from strategies import (
    PanicBuyStrategy,
    RiskManagementStrategy,
    LeverageStrategy,
    SectorRotationStrategy,
    MACDVStrategy
)


def run_strategy_1(data_loader: DataLoader) -> Dict[str, Any]:
    """
    Run Strategy 1: Market Panic Identification and Bottom Buying.

    Args:
        data_loader: DataLoader instance

    Returns:
        Latest signal dictionary
    """
    print("\n" + "="*80)
    print("STRATEGY 1: Market Panic Identification and Bottom Buying")
    print("="*80)

    try:
        # Load data
        print("Loading data...")
        spy_data = data_loader.load_market_index('SPY')
        nyse_breadth = data_loader.get_nyse_breadth_data()

        # Initialize strategy
        strategy = PanicBuyStrategy(
            nl_ma_period=3,
            nl_threshold=0.50,
            stco_ma_period=10,
            stco_threshold=80,
            signal_confirmation_days=1,
            entry_logic='Delayed',
            delay_days=10,
            target_asset='SPY'
        )

        # Generate signals
        print("Generating signals...")
        signals_df = strategy.generate_signals(
            nyse_breadth_data=nyse_breadth,
            market_data=spy_data
        )

        # Get latest signal
        latest_signal = strategy.get_latest_signal()

        print(f"\nLatest Signal:")
        print(json.dumps(latest_signal, indent=2))

        return latest_signal

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"strategy_id": "Strategy_1_Panic_Buy", "error": str(e)}


def run_strategy_2(data_loader: DataLoader) -> Dict[str, Any]:
    """
    Run Strategy 2: Volatility/Decline Speed Based Risk Management.

    Args:
        data_loader: DataLoader instance

    Returns:
        Latest signal dictionary
    """
    print("\n" + "="*80)
    print("STRATEGY 2: Volatility/Decline Speed Based Risk Management")
    print("="*80)

    try:
        # Load data
        print("Loading data...")
        spy_data = data_loader.load_market_index('SPY')
        vix_data = data_loader.load_vix()

        # Initialize strategy
        strategy = RiskManagementStrategy(
            vix_std_period=20,
            vix_std_threshold=0.86,
            drop_pct=0.05,
            canary_days=15,
            confirmation_window=42,
            sma_period=200,
            confirmation_days=2
        )

        # Generate signals
        print("Generating signals...")
        signals_df = strategy.generate_signals(
            vix_data=vix_data,
            market_data=spy_data
        )

        # Get latest signal
        latest_signal = strategy.get_latest_signal()

        print(f"\nLatest Signal:")
        print(json.dumps(latest_signal, indent=2))

        return latest_signal

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"strategy_id": "Strategy_2_Risk_Management", "error": str(e)}


def run_strategy_3(data_loader: DataLoader) -> Dict[str, Any]:
    """
    Run Strategy 3: Trend-Based Leverage.

    Args:
        data_loader: DataLoader instance

    Returns:
        Latest signal dictionary
    """
    print("\n" + "="*80)
    print("STRATEGY 3: Trend-Based Leverage")
    print("="*80)

    try:
        # Load data
        print("Loading data...")
        spy_data = data_loader.load_market_index('SPY')

        # Initialize strategy
        strategy = LeverageStrategy(
            sma_period=200,
            leverage_multiple=1.5,
            target_asset='SPY'
        )

        # Generate signals
        print("Generating signals...")
        signals_df = strategy.generate_signals(market_data=spy_data)

        # Get latest signal
        latest_signal = strategy.get_latest_signal()

        print(f"\nLatest Signal:")
        print(json.dumps(latest_signal, indent=2))

        return latest_signal

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"strategy_id": "Strategy_3_Leverage", "error": str(e)}


def run_strategy_4(data_loader: DataLoader) -> Dict[str, Any]:
    """
    Run Strategy 4: Quantamental Sector Rotation.

    Args:
        data_loader: DataLoader instance

    Returns:
        Latest signal dictionary
    """
    print("\n" + "="*80)
    print("STRATEGY 4: Quantamental Sector Rotation")
    print("="*80)

    try:
        # Load data
        print("Loading data...")
        spy_data = data_loader.load_market_index('SPY')
        sector_data = data_loader.load_sector_etfs()

        # Initialize strategy
        strategy = SectorRotationStrategy(
            use_fundamentals=False,
            momentum_period=6,
            momentum_skip_months=1,
            volatility_period=100,
            top_n_sectors=3,
            weighting_method='EW',
            market_filter_sma=200,
            rebalance_frequency='Monthly'
        )

        # Generate signals
        print("Generating signals...")
        signals_df = strategy.generate_signals(
            sector_data=sector_data,
            market_data=spy_data
        )

        # Get latest signal
        latest_signal = strategy.get_latest_signal()

        print(f"\nLatest Signal:")
        print(json.dumps(latest_signal, indent=2))

        return latest_signal

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"strategy_id": "Strategy_4_Sector_Rotation", "error": str(e)}


def run_strategy_5(data_loader: DataLoader) -> Dict[str, Any]:
    """
    Run Strategy 5: Volatility-Normalized Momentum (MACD-V).

    Args:
        data_loader: DataLoader instance

    Returns:
        Latest signal dictionary
    """
    print("\n" + "="*80)
    print("STRATEGY 5: Volatility-Normalized Momentum (MACD-V)")
    print("="*80)

    try:
        # Load data
        print("Loading data...")
        asset_universe = ['SPY', 'TLT', 'GLD', 'DBC']
        asset_data = data_loader.load_asset_universe(asset_universe)

        # Initialize strategy
        strategy = MACDVStrategy(
            ema_short=12,
            ema_long=26,
            atr_period=26,
            market_filter_sma=200,
            thresholds={
                'Overbought': 150,
                'Rallying': 50,
                'Ranging_Upper': 50,
                'Ranging_Lower': -50,
                'Reversing': -150,
                'Oversold': -150
            }
        )

        # Generate signals
        print("Generating signals...")
        signals_df = strategy.generate_signals(asset_data=asset_data)

        # Get latest signal
        latest_signal = strategy.get_latest_signal()

        print(f"\nLatest Signal:")
        print(json.dumps(latest_signal, indent=2))

        return latest_signal

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"strategy_id": "Strategy_5_MACD_V", "error": str(e)}


def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(
        description='Investment Strategy Signal Generators'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['1', '2', '3', '4', '5', 'all'],
        default='all',
        help='Strategy to run (1-5 or "all")'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date (YYYY-MM-DD). Default: 5 years ago'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date (YYYY-MM-DD). Default: today'
    )

    args = parser.parse_args()

    # Initialize data loader
    print("Initializing data loader...")
    data_loader = DataLoader(start_date=args.start_date, end_date=args.end_date)

    # Strategy execution mapping
    strategy_runners = {
        '1': run_strategy_1,
        '2': run_strategy_2,
        '3': run_strategy_3,
        '4': run_strategy_4,
        '5': run_strategy_5
    }

    # Execute strategies
    results = {}

    if args.strategy == 'all':
        for strategy_id, runner in strategy_runners.items():
            results[strategy_id] = runner(data_loader)
    else:
        results[args.strategy] = strategy_runners[args.strategy](data_loader)

    # Summary
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    print(f"\nTotal strategies executed: {len(results)}")
    print(f"\nAll signals (JSON format):")
    print(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    main()
