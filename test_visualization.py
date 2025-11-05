"""
Test script for strategy visualizations.

Tests the plot() method for all 5 strategies.
"""

from utils.data_loader import DataLoader
from strategies import (
    PanicBuyStrategy,
    RiskManagementStrategy,
    LeverageStrategy,
    SectorRotationStrategy,
    MACDVStrategy
)


def test_strategy_1_visualization():
    """Test Strategy 1 (Panic Buy) visualization."""
    print("\n" + "="*80)
    print("Testing Strategy 1 Visualization (Panic Buy)")
    print("="*80)

    # Load data
    data_loader = DataLoader(start_date='2023-01-01')
    spy_data = data_loader.load_market_index('SPY')
    nyse_breadth = data_loader.get_nyse_breadth_data()

    # Initialize and visualize
    strategy = PanicBuyStrategy()
    strategy.plot(nyse_breadth_data=nyse_breadth, market_data=spy_data,
                 save_path='charts/strategy_1_panic_buy.png')

    print("[OK] Strategy 1 visualization completed")
    print("  Chart saved to: charts/strategy_1_panic_buy.png")


def test_strategy_2_visualization():
    """Test Strategy 2 (Risk Management) visualization."""
    print("\n" + "="*80)
    print("Testing Strategy 2 Visualization (Risk Management)")
    print("="*80)

    # Load data
    data_loader = DataLoader(start_date='2023-01-01')
    spy_data = data_loader.load_market_index('SPY')
    vix_data = data_loader.load_vix()

    # Initialize and visualize
    strategy = RiskManagementStrategy()
    strategy.plot(vix_data=vix_data, market_data=spy_data,
                 save_path='charts/strategy_2_risk_management.png')

    print("[OK] Strategy 2 visualization completed")
    print("  Chart saved to: charts/strategy_2_risk_management.png")


def test_strategy_3_visualization():
    """Test Strategy 3 (Leverage) visualization."""
    print("\n" + "="*80)
    print("Testing Strategy 3 Visualization (Leverage)")
    print("="*80)

    # Load data
    data_loader = DataLoader(start_date='2023-01-01')
    spy_data = data_loader.load_market_index('SPY')

    # Initialize and visualize
    strategy = LeverageStrategy(sma_period=200, leverage_multiple=1.5)
    strategy.plot(market_data=spy_data, save_path='charts/strategy_3_leverage.png')

    print("[OK] Strategy 3 visualization completed")
    print("  Chart saved to: charts/strategy_3_leverage.png")


def test_strategy_4_visualization():
    """Test Strategy 4 (Sector Rotation) visualization."""
    print("\n" + "="*80)
    print("Testing Strategy 4 Visualization (Sector Rotation)")
    print("="*80)

    # Load data
    data_loader = DataLoader(start_date='2023-01-01')
    spy_data = data_loader.load_market_index('SPY')
    sector_data = data_loader.load_sector_etfs()

    # Initialize and visualize
    strategy = SectorRotationStrategy()
    strategy.plot(sector_data=sector_data, market_data=spy_data,
                 save_path='charts/strategy_4_sector_rotation.png')

    print("[OK] Strategy 4 visualization completed")
    print("  Chart saved to: charts/strategy_4_sector_rotation.png")


def test_strategy_5_visualization():
    """Test Strategy 5 (MACD-V) visualization."""
    print("\n" + "="*80)
    print("Testing Strategy 5 Visualization (MACD-V)")
    print("="*80)

    # Load data
    data_loader = DataLoader(start_date='2023-01-01')
    asset_universe = ['SPY', 'TLT', 'GLD', 'DBC']
    asset_data = data_loader.load_asset_universe(asset_universe)

    # Initialize and visualize
    strategy = MACDVStrategy()
    strategy.plot(asset_data=asset_data, save_path='charts/strategy_5_macd_v.png')

    print("[OK] Strategy 5 visualization completed")
    print("  Chart saved to: charts/strategy_5_macd_v.png")


def main():
    """Run all visualization tests."""
    import os

    # Create charts directory if it doesn't exist
    if not os.path.exists('charts'):
        os.makedirs('charts')
        print("Created 'charts' directory for saving plots")

    print("\n" + "="*80)
    print("STRATEGY VISUALIZATION TESTS - ALL 5 STRATEGIES")
    print("="*80)
    print("\nThis script will generate visualization charts for all 5 strategies.")
    print("Charts will be saved in the 'charts/' directory.\n")

    try:
        # Test all strategies
        test_strategy_1_visualization()
        test_strategy_2_visualization()
        test_strategy_3_visualization()
        test_strategy_4_visualization()
        test_strategy_5_visualization()

        print("\n" + "="*80)
        print("ALL VISUALIZATIONS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nGenerated charts:")
        print("  1. charts/strategy_1_panic_buy.png")
        print("  2. charts/strategy_2_risk_management.png")
        print("  3. charts/strategy_3_leverage.png")
        print("  4. charts/strategy_4_sector_rotation.png")
        print("  5. charts/strategy_5_macd_v.png")
        print("\nYou can open these PNG files to view the strategy visualizations.")

    except Exception as e:
        print(f"\n[ERROR] Error during visualization: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
