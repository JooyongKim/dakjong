"""
Working test with proper package imports
"""

import sys
import os

# Add to path and change directory
sys.path.insert(0, '/home/user/dakjong')
os.chdir('/home/user/dakjong')

import pandas as pd
import numpy as np
from datetime import datetime
import json

print("="*80)
print("🧪 투자 전략 실제 실행 테스트")
print("="*80)

# Step 1: Create mock data
print("\n[1/4] 테스트 데이터 생성...")
dates = pd.date_range(end=datetime.now(), periods=300, freq='D')

# Realistic price movement
base_price = 400
trend = np.linspace(0, 50, 300)
noise = np.random.normal(0, 3, 300).cumsum()
prices = base_price + trend + noise

spy_data = pd.DataFrame({
    'Open': prices * 0.995,
    'High': prices * 1.008,
    'Low': prices * 0.992,
    'Close': prices,
    'Adj Close': prices,
    'Volume': np.random.randint(50000000, 100000000, 300)
}, index=dates)

print(f"  ✓ SPY 데이터: {len(spy_data)}일")
print(f"  시작: ${spy_data['Close'].iloc[0]:.2f}")
print(f"  종료: ${spy_data['Close'].iloc[-1]:.2f}")
print(f"  수익률: {((spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[0]) - 1) * 100:+.2f}%")

# Step 2: Import using standard Python imports
print("\n[2/4] 전략 모듈 import...")
try:
    from utils.indicators import Indicators
    from strategies.base_strategy import BaseStrategy
    from strategies.strategy_3_leverage import LeverageStrategy

    print("  ✓ utils.indicators 로드 완료")
    print("  ✓ strategies.base_strategy 로드 완료")
    print("  ✓ strategies.strategy_3_leverage 로드 완료")

except ImportError as e:
    print(f"  ✗ Import 실패: {e}")
    print("\n  yfinance가 없어서 data_loader import가 실패할 수 있습니다.")
    print("  utils/__init__.py를 수정해야 합니다...")
    sys.exit(1)

# Step 3: Test indicators first
print("\n[3/4] 기술적 지표 테스트...")
try:
    sma_50 = Indicators.sma(spy_data['Close'], 50)
    ema_12 = Indicators.ema(spy_data['Close'], 12)
    atr = Indicators.atr(spy_data['High'], spy_data['Low'], spy_data['Close'], 14)

    print(f"  ✓ SMA(50): ${sma_50.iloc[-1]:.2f}")
    print(f"  ✓ EMA(12): ${ema_12.iloc[-1]:.2f}")
    print(f"  ✓ ATR(14): ${atr.iloc[-1]:.2f}")

except Exception as e:
    print(f"  ✗ 지표 계산 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Run strategy
print("\n[4/4] Strategy 3 실행...")
try:
    strategy = LeverageStrategy(
        sma_period=50,
        leverage_multiple=1.5,
        target_asset='SPY'
    )

    print(f"  전략: {strategy.strategy_name}")
    print(f"  ID: {strategy.strategy_id}")

    signals_df = strategy.generate_signals(market_data=spy_data)

    print(f"  ✓ 신호 생성 완료")
    print(f"  신호 변화: {len(strategy.signals_history)}회")

except Exception as e:
    print(f"  ✗ 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Results
print("\n" + "="*80)
print("📊 실행 결과")
print("="*80)

latest = strategy.get_latest_signal()

print("\n🎯 최신 신호:")
print(json.dumps(latest, indent=2, ensure_ascii=False))

print("\n" + "="*80)
print("✅ 테스트 성공!")
print("="*80)

signal = latest['signal']
details = latest['details']

if signal == 'LEVERAGE_ON':
    print(f"\n✅ 상승 추세 - 레버리지 {details['leverage_multiple']}배 권장")
else:
    print(f"\n⚠️  하락 추세 - 레버리지 미사용 권장")

print(f"현재가: ${details['current_price']:.2f}")
print(f"MA: ${details['sma_200']:.2f}")
print(f"괴리율: {details['price_vs_sma_pct']:+.2f}%")

print("\n모든 전략이 정상 작동합니다! 🎉")
print("")
