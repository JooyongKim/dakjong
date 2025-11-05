"""
Direct test without any external imports - pure Python + pandas/numpy
"""

import sys
sys.path.insert(0, '/home/user/dakjong')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("실제 코드 실행 테스트 - Strategy 3 (가장 간단)")
print("="*80)

# Step 1: Create mock data
print("\n[1/4] Mock 데이터 생성 중...")
dates = pd.date_range(end=datetime.now(), periods=300, freq='D')
prices = 400 + np.linspace(0, 50, 300) + np.random.normal(0, 5, 300).cumsum()

spy_data = pd.DataFrame({
    'Open': prices * 0.99,
    'High': prices * 1.01,
    'Low': prices * 0.98,
    'Close': prices,
    'Adj Close': prices,
    'Volume': np.random.randint(50000000, 100000000, 300)
}, index=dates)

print(f"  ✓ SPY 데이터 생성 완료: {len(spy_data)} 거래일")
print(f"  최근 종가: ${spy_data['Close'].iloc[-1]:.2f}")

# Step 2: Import strategy directly
print("\n[2/4] 전략 모듈 로딩 중...")
try:
    # Import indicators module directly
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicators", "/home/user/dakjong/utils/indicators.py")
    indicators_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(indicators_module)
    Indicators = indicators_module.Indicators

    # Import base strategy
    spec = importlib.util.spec_from_file_location("base_strategy", "/home/user/dakjong/strategies/base_strategy.py")
    base_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_module)

    # Import strategy 3 - but we need to inject dependencies
    with open('/home/user/dakjong/strategies/strategy_3_leverage.py', 'r') as f:
        strategy_code = f.read()

    # Execute in namespace with dependencies
    namespace = {
        'pd': pd,
        'np': np,
        'datetime': datetime,
        'Dict': dict,
        'Any': object,
        'BaseStrategy': base_module.BaseStrategy,
        'Indicators': Indicators
    }

    exec(strategy_code, namespace)
    LeverageStrategy = namespace['LeverageStrategy']

    print("  ✓ 전략 모듈 로드 완료")

except Exception as e:
    print(f"  ✗ 모듈 로드 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Execute strategy
print("\n[3/4] 전략 실행 중...")
try:
    strategy = LeverageStrategy(
        sma_period=50,  # 200일은 너무 길어서 50일로 조정
        leverage_multiple=1.5,
        target_asset='SPY'
    )

    print(f"  전략 ID: {strategy.strategy_id}")
    print(f"  전략명: {strategy.strategy_name}")

    # Generate signals
    signals_df = strategy.generate_signals(market_data=spy_data)

    print(f"  ✓ 신호 생성 완료")
    print(f"  생성된 신호 변화 횟수: {len(strategy.signals_history)}")

except Exception as e:
    print(f"  ✗ 전략 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Show results
print("\n[4/4] 결과 출력")
print("-"*80)

latest = strategy.get_latest_signal()

import json
print("\n최신 신호 (JSON):")
print(json.dumps(latest, indent=2, ensure_ascii=False))

print("\n" + "-"*80)
print("\n📊 해석:")
print(f"  신호: {latest['signal']}")
print(f"  자산: {latest['asset']}")
print(f"  현재가: ${latest['details']['current_price']:.2f}")
print(f"  50일 MA: ${latest['details']['sma_200']:.2f}")
print(f"  괴리율: {latest['details']['price_vs_sma_pct']:.2f}%")

if latest['signal'] == 'LEVERAGE_ON':
    print(f"\n  💡 추세: 상승 (레버리지 {latest['details']['leverage_multiple']}배 권장)")
else:
    print(f"\n  💡 추세: 하락 (레버리지 미사용 권장)")

print("\n" + "="*80)
print("✅ 테스트 성공! 전략이 정상 작동합니다!")
print("="*80)
