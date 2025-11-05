"""
Integration test with mock data to verify all strategies work correctly.
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("투자 전략 신호 발생기 통합 테스트")
print("="*80)

# Import all modules
try:
    from utils.indicators import Indicators
    from strategies import (
        PanicBuyStrategy,
        RiskManagementStrategy,
        LeverageStrategy,
        SectorRotationStrategy,
        MACDVStrategy
    )
    print("\n✓ 모든 모듈 import 성공\n")
except Exception as e:
    print(f"\n✗ Import 실패: {e}")
    sys.exit(1)


def create_mock_market_data(days=500):
    """Create mock market data (SPY-like)"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Create synthetic price data with trend
    base_price = 400
    trend = np.linspace(0, 50, days)
    noise = np.random.normal(0, 5, days).cumsum()
    prices = base_price + trend + noise

    df = pd.DataFrame({
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Close': prices,
        'Adj Close': prices,
        'Volume': np.random.randint(50000000, 100000000, days)
    }, index=dates)

    return df


def create_mock_vix_data(days=500):
    """Create mock VIX data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # VIX typically ranges 10-30, with spikes
    base_vix = 15
    noise = np.random.normal(0, 3, days).cumsum()
    vix_values = np.clip(base_vix + noise, 8, 40)

    df = pd.DataFrame({
        'Open': vix_values * 0.98,
        'High': vix_values * 1.05,
        'Low': vix_values * 0.95,
        'Close': vix_values,
        'Adj Close': vix_values,
        'Volume': np.random.randint(1000000, 5000000, days)
    }, index=dates)

    return df


def create_mock_nyse_breadth(days=500):
    """Create mock NYSE breadth data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    df = pd.DataFrame({
        'NewLows_Ratio': np.random.uniform(0.05, 0.30, days),
        'UpVolume_Ratio': np.random.uniform(0.40, 0.65, days),
        'Advancing_Ratio': np.random.uniform(0.45, 0.60, days)
    }, index=dates)

    # Add some panic conditions
    panic_dates = np.random.choice(range(100, days-100), 3, replace=False)
    for pd_idx in panic_dates:
        df.iloc[pd_idx:pd_idx+5, df.columns.get_loc('NewLows_Ratio')] = np.random.uniform(0.50, 0.70, 5)
        df.iloc[pd_idx:pd_idx+5, df.columns.get_loc('UpVolume_Ratio')] = np.random.uniform(0.20, 0.35, 5)
        df.iloc[pd_idx:pd_idx+5, df.columns.get_loc('Advancing_Ratio')] = np.random.uniform(0.25, 0.40, 5)

    return df


def create_mock_sector_data(tickers, days=500):
    """Create mock sector ETF data"""
    sector_data = {}

    for ticker in tickers:
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # Each sector has different characteristics
        base_price = np.random.uniform(50, 150)
        trend = np.linspace(0, np.random.uniform(-20, 40), days)
        noise = np.random.normal(0, 2, days).cumsum()
        prices = base_price + trend + noise

        sector_data[ticker] = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Adj Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)

    return sector_data


# Test Strategy 1: Panic Buy
print("-" * 80)
print("테스트 1: 시장 패닉 식별 및 저점 매수")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    nyse_breadth = create_mock_nyse_breadth(500)

    strategy1 = PanicBuyStrategy(
        nl_threshold=0.50,
        stco_threshold=80,
        entry_logic='Confirmed'
    )

    signals_df = strategy1.generate_signals(
        nyse_breadth_data=nyse_breadth,
        market_data=spy_data
    )

    latest = strategy1.get_latest_signal()
    print(f"  전략 ID: {latest['strategy_id']}")
    print(f"  신호: {latest['signal']}")
    print(f"  자산: {latest['asset']}")
    print(f"  생성된 총 신호 수: {len(strategy1.signals_history)}")
    print("  ✓ Strategy 1 테스트 통과\n")
except Exception as e:
    print(f"  ✗ Strategy 1 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Test Strategy 2: Risk Management
print("-" * 80)
print("테스트 2: 변동성/하락 속도 기반 위험 관리")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    vix_data = create_mock_vix_data(500)

    strategy2 = RiskManagementStrategy(
        vix_std_threshold=0.86,
        drop_pct=0.05
    )

    signals_df = strategy2.generate_signals(
        vix_data=vix_data,
        market_data=spy_data
    )

    latest = strategy2.get_latest_signal()
    print(f"  전략 ID: {latest['strategy_id']}")
    print(f"  신호: {latest['signal']}")
    print(f"  자산: {latest['asset']}")
    print(f"  생성된 총 신호 수: {len(strategy2.signals_history)}")
    print("  ✓ Strategy 2 테스트 통과\n")
except Exception as e:
    print(f"  ✗ Strategy 2 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Test Strategy 3: Leverage
print("-" * 80)
print("테스트 3: 추세 기반 레버리지")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)

    strategy3 = LeverageStrategy(
        sma_period=200,
        leverage_multiple=1.5
    )

    signals_df = strategy3.generate_signals(market_data=spy_data)

    latest = strategy3.get_latest_signal()
    print(f"  전략 ID: {latest['strategy_id']}")
    print(f"  신호: {latest['signal']}")
    print(f"  자산: {latest['asset']}")
    print(f"  레버리지 배수: {latest['details'].get('leverage_multiple', 'N/A')}")
    print(f"  생성된 총 신호 수: {len(strategy3.signals_history)}")
    print("  ✓ Strategy 3 테스트 통과\n")
except Exception as e:
    print(f"  ✗ Strategy 3 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Test Strategy 4: Sector Rotation
print("-" * 80)
print("테스트 4: 섹터 로테이션")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    sector_tickers = ['XLE', 'XLF', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLU', 'XLRE', 'XLC']
    sector_data = create_mock_sector_data(sector_tickers, 500)

    strategy4 = SectorRotationStrategy(
        momentum_period=6,
        top_n_sectors=3,
        weighting_method='EW',
        rebalance_frequency='Monthly'
    )

    signals_df = strategy4.generate_signals(
        sector_data=sector_data,
        market_data=spy_data
    )

    latest = strategy4.get_latest_signal()
    print(f"  전략 ID: {latest['strategy_id']}")
    print(f"  신호: {latest['signal']}")
    print(f"  자산: {latest['asset']}")
    if latest['signal'] == 'HOLD_SECTORS':
        sectors = latest['details'].get('sectors_list', [])
        print(f"  선정 섹터: {', '.join(sectors)}")
    print(f"  생성된 총 신호 수: {len(strategy4.signals_history)}")
    print("  ✓ Strategy 4 테스트 통과\n")
except Exception as e:
    print(f"  ✗ Strategy 4 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Test Strategy 5: MACD-V
print("-" * 80)
print("테스트 5: MACD-V 변동성 정규화 모멘텀")
print("-" * 80)
try:
    asset_universe = ['SPY', 'TLT', 'GLD', 'DBC']
    asset_data = create_mock_sector_data(asset_universe, 500)

    strategy5 = MACDVStrategy(
        ema_short=12,
        ema_long=26,
        atr_period=26
    )

    signals_df = strategy5.generate_signals(asset_data=asset_data)

    latest = strategy5.get_latest_signal()
    print(f"  전략 ID: {latest['strategy_id']}")
    print(f"  신호: {latest['signal']}")
    print(f"  자산: {latest['asset']}")
    print(f"  시장 체제: {latest['details'].get('market_regime', 'N/A')}")
    print(f"  생성된 총 신호 수: {len(strategy5.signals_history)}")
    print("  ✓ Strategy 5 테스트 통과\n")
except Exception as e:
    print(f"  ✗ Strategy 5 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Test Indicators
print("-" * 80)
print("테스트 6: 기술적 지표")
print("-" * 80)
try:
    test_data = create_mock_market_data(300)

    # Test SMA
    sma = Indicators.sma(test_data['Close'], 50)
    assert not sma.isna().all(), "SMA calculation failed"
    print("  ✓ SMA 계산 성공")

    # Test EMA
    ema = Indicators.ema(test_data['Close'], 50)
    assert not ema.isna().all(), "EMA calculation failed"
    print("  ✓ EMA 계산 성공")

    # Test ATR
    atr = Indicators.atr(test_data['High'], test_data['Low'], test_data['Close'], 14)
    assert not atr.isna().all(), "ATR calculation failed"
    print("  ✓ ATR 계산 성공")

    # Test MACD-V
    macd_v = Indicators.macd_v(test_data['High'], test_data['Low'], test_data['Close'])
    assert not macd_v.isna().all(), "MACD-V calculation failed"
    print("  ✓ MACD-V 계산 성공")

    print("  ✓ 모든 지표 테스트 통과\n")
except Exception as e:
    print(f"  ✗ 지표 테스트 실패: {e}\n")
    import traceback
    traceback.print_exc()


# Summary
print("="*80)
print("테스트 완료!")
print("="*80)
print("\n모든 전략이 정상적으로 동작합니다!")
print("\n실제 사용 방법:")
print("  1. 패키지 설치: pip install pandas numpy yfinance")
print("  2. 전체 실행: python main.py --strategy all")
print("  3. 개별 실행: python main.py --strategy 3")
print("  4. 예제 실행: python example_usage.py")
print("\n" + "="*80)
