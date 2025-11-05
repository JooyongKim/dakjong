"""
Final integration test - directly importing modules without data_loader
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("투자 전략 신호 발생기 최종 검증 테스트")
print("="*80)

# Import strategies and indicators directly
try:
    # Import indicators directly
    sys.path.insert(0, '/home/user/dakjong')
    from utils.indicators import Indicators

    # Import strategies directly
    from strategies.base_strategy import BaseStrategy
    from strategies.strategy_1_panic_buy import PanicBuyStrategy
    from strategies.strategy_2_risk_management import RiskManagementStrategy
    from strategies.strategy_3_leverage import LeverageStrategy
    from strategies.strategy_4_sector_rotation import SectorRotationStrategy
    from strategies.strategy_5_macd_v import MACDVStrategy

    print("\n✓ 모든 전략 모듈 import 성공")
    print(f"  - BaseStrategy: {BaseStrategy.__name__}")
    print(f"  - PanicBuyStrategy: {PanicBuyStrategy.__name__}")
    print(f"  - RiskManagementStrategy: {RiskManagementStrategy.__name__}")
    print(f"  - LeverageStrategy: {LeverageStrategy.__name__}")
    print(f"  - SectorRotationStrategy: {SectorRotationStrategy.__name__}")
    print(f"  - MACDVStrategy: {MACDVStrategy.__name__}")
    print(f"  - Indicators: {Indicators.__name__}\n")
except Exception as e:
    print(f"\n✗ Import 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def create_mock_market_data(days=500):
    """Create realistic mock market data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_price = 400
    trend = np.linspace(0, 50, days)
    noise = np.random.normal(0, 5, days).cumsum()
    prices = base_price + trend + noise

    return pd.DataFrame({
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Close': prices,
        'Adj Close': prices,
        'Volume': np.random.randint(50000000, 100000000, days)
    }, index=dates)


def create_mock_vix_data(days=500):
    """Create realistic VIX data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_vix = 15
    noise = np.random.normal(0, 3, days).cumsum()
    vix_values = np.clip(base_vix + noise, 8, 40)

    return pd.DataFrame({
        'Open': vix_values * 0.98,
        'High': vix_values * 1.05,
        'Low': vix_values * 0.95,
        'Close': vix_values,
        'Adj Close': vix_values,
        'Volume': np.random.randint(1000000, 5000000, days)
    }, index=dates)


def create_mock_nyse_breadth(days=500):
    """Create NYSE breadth data with panic events"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    df = pd.DataFrame({
        'NewLows_Ratio': np.random.uniform(0.05, 0.30, days),
        'UpVolume_Ratio': np.random.uniform(0.40, 0.65, days),
        'Advancing_Ratio': np.random.uniform(0.45, 0.60, days)
    }, index=dates)

    # Inject panic conditions
    panic_dates = np.random.choice(range(100, days-100), 3, replace=False)
    for pd_idx in panic_dates:
        df.iloc[pd_idx:pd_idx+5, 0] = np.random.uniform(0.50, 0.70, 5)
        df.iloc[pd_idx:pd_idx+5, 1] = np.random.uniform(0.20, 0.35, 5)
        df.iloc[pd_idx:pd_idx+5, 2] = np.random.uniform(0.25, 0.40, 5)

    return df


def create_mock_sector_data(tickers, days=500):
    """Create mock sector ETF data"""
    sector_data = {}
    for ticker in tickers:
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
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


print("\n" + "=" * 80)
print("개별 전략 테스트 시작")
print("=" * 80 + "\n")

test_results = []

# Strategy 1
print("[ 1/5 ] Strategy 1: 시장 패닉 식별 및 저점 매수")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    nyse_breadth = create_mock_nyse_breadth(500)

    s1 = PanicBuyStrategy(nl_threshold=0.50, stco_threshold=80, entry_logic='Confirmed')
    signals = s1.generate_signals(nyse_breadth_data=nyse_breadth, market_data=spy_data)
    latest = s1.get_latest_signal()

    print(f"✓ 전략 ID: {latest['strategy_id']}")
    print(f"✓ 신호: {latest['signal']}")
    print(f"✓ 자산: {latest['asset']}")
    print(f"✓ 총 신호 수: {len(s1.signals_history)}\n")
    test_results.append(("Strategy 1", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Strategy 1", "FAIL"))

# Strategy 2
print("[ 2/5 ] Strategy 2: 변동성/하락 속도 기반 위험 관리")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    vix_data = create_mock_vix_data(500)

    s2 = RiskManagementStrategy(vix_std_threshold=0.86, drop_pct=0.05)
    signals = s2.generate_signals(vix_data=vix_data, market_data=spy_data)
    latest = s2.get_latest_signal()

    print(f"✓ 전략 ID: {latest['strategy_id']}")
    print(f"✓ 신호: {latest['signal']}")
    print(f"✓ 자산: {latest['asset']}")
    print(f"✓ 총 신호 수: {len(s2.signals_history)}\n")
    test_results.append(("Strategy 2", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Strategy 2", "FAIL"))

# Strategy 3
print("[ 3/5 ] Strategy 3: 추세 기반 레버리지")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)

    s3 = LeverageStrategy(sma_period=200, leverage_multiple=1.5)
    signals = s3.generate_signals(market_data=spy_data)
    latest = s3.get_latest_signal()

    print(f"✓ 전략 ID: {latest['strategy_id']}")
    print(f"✓ 신호: {latest['signal']}")
    print(f"✓ 자산: {latest['asset']}")
    print(f"✓ 레버리지 배수: {latest['details'].get('leverage_multiple', 'N/A')}")
    print(f"✓ 총 신호 수: {len(s3.signals_history)}\n")
    test_results.append(("Strategy 3", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Strategy 3", "FAIL"))

# Strategy 4
print("[ 4/5 ] Strategy 4: 섹터 로테이션")
print("-" * 80)
try:
    spy_data = create_mock_market_data(500)
    sectors = ['XLE', 'XLF', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLU', 'XLRE', 'XLC']
    sector_data = create_mock_sector_data(sectors, 500)

    s4 = SectorRotationStrategy(momentum_period=6, top_n_sectors=3, weighting_method='EW')
    signals = s4.generate_signals(sector_data=sector_data, market_data=spy_data)
    latest = s4.get_latest_signal()

    print(f"✓ 전략 ID: {latest['strategy_id']}")
    print(f"✓ 신호: {latest['signal']}")
    if latest['signal'] == 'HOLD_SECTORS' and 'sectors_list' in latest['details']:
        print(f"✓ 선정 섹터: {', '.join(latest['details']['sectors_list'])}")
    print(f"✓ 총 신호 수: {len(s4.signals_history)}\n")
    test_results.append(("Strategy 4", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Strategy 4", "FAIL"))

# Strategy 5
print("[ 5/5 ] Strategy 5: MACD-V 변동성 정규화 모멘텀")
print("-" * 80)
try:
    assets = ['SPY', 'TLT', 'GLD', 'DBC']
    asset_data = create_mock_sector_data(assets, 500)

    s5 = MACDVStrategy(ema_short=12, ema_long=26, atr_period=26)
    signals = s5.generate_signals(asset_data=asset_data)
    latest = s5.get_latest_signal()

    print(f"✓ 전략 ID: {latest['strategy_id']}")
    print(f"✓ 신호: {latest['signal']}")
    print(f"✓ 시장 체제: {latest['details'].get('market_regime', 'N/A')}")
    print(f"✓ 총 신호 수: {len(s5.signals_history)}\n")
    test_results.append(("Strategy 5", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Strategy 5", "FAIL"))

# Test Indicators
print("\n[ 보너스 ] 기술적 지표 테스트")
print("-" * 80)
try:
    test_data = create_mock_market_data(300)

    sma = Indicators.sma(test_data['Close'], 50)
    print("✓ SMA 계산 완료")

    ema = Indicators.ema(test_data['Close'], 50)
    print("✓ EMA 계산 완료")

    atr = Indicators.atr(test_data['High'], test_data['Low'], test_data['Close'], 14)
    print("✓ ATR 계산 완료")

    macd_v = Indicators.macd_v(test_data['High'], test_data['Low'], test_data['Close'])
    print("✓ MACD-V 계산 완료\n")

    test_results.append(("Indicators", "PASS"))
except Exception as e:
    print(f"✗ 실패: {e}\n")
    test_results.append(("Indicators", "FAIL"))

# Summary
print("\n" + "=" * 80)
print("테스트 결과 요약")
print("=" * 80)
for name, result in test_results:
    status = "✓ PASS" if result == "PASS" else "✗ FAIL"
    print(f"{status} - {name}")

passed = sum(1 for _, r in test_results if r == "PASS")
total = len(test_results)

print("\n" + "=" * 80)
if passed == total:
    print(f"✓✓✓ 전체 테스트 성공! ({passed}/{total}) ✓✓✓")
else:
    print(f"일부 테스트 실패: {passed}/{total}")
print("=" * 80)

if passed == total:
    print("\n시스템이 정상적으로 동작합니다!")
    print("\n실제 사용 시:")
    print("  1. pip install pandas numpy yfinance")
    print("  2. python main.py --strategy all  (모든 전략)")
    print("  3. python main.py --strategy 3    (개별 전략)")
    print("\nPython 코드에서:")
    print("  from strategies import LeverageStrategy")
    print("  strategy = LeverageStrategy()")
    print("  signals = strategy.generate_signals(market_data)")
print("")
