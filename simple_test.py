#!/usr/bin/env python3
"""
간단한 실행 예제 - Strategy 3 (레버리지)

가장 간단하고 데이터 의존성이 적은 전략을 실행합니다.
"""

print("="*80)
print("투자 전략 신호 발생기 - 간단한 실행 예제")
print("Strategy 3: 추세 기반 레버리지")
print("="*80)

try:
    from utils.data_loader import DataLoader
    from strategies import LeverageStrategy
    import json

    print("\n[1/3] 데이터 로딩 중...")
    # 최근 2년 데이터 로드
    loader = DataLoader(start_date='2023-01-01')
    spy_data = loader.load_market_index('SPY')
    print(f"  ✓ SPY 데이터 로드 완료: {len(spy_data)} 거래일")

    print("\n[2/3] 전략 실행 중...")
    # 전략 초기화 및 실행
    strategy = LeverageStrategy(
        sma_period=200,
        leverage_multiple=1.5
    )
    signals_df = strategy.generate_signals(market_data=spy_data)
    print(f"  ✓ 신호 생성 완료")

    print("\n[3/3] 결과 출력")
    print("-" * 80)

    # 최신 신호 가져오기
    latest = strategy.get_latest_signal()

    print("\n최신 신호:")
    print(json.dumps(latest, indent=2, ensure_ascii=False))

    print("\n" + "-" * 80)
    print("\n해석:")
    if latest['signal'] == 'LEVERAGE_ON':
        print("  📈 현재 상승 추세입니다 (가격 > 200일 이동평균)")
        print(f"  💡 레버리지 {latest['details']['leverage_multiple']}배 사용 권장")
        print(f"  📊 현재가: ${latest['details']['current_price']:.2f}")
        print(f"  📊 200일 MA: ${latest['details']['sma_200']:.2f}")
        print(f"  📊 괴리율: {latest['details']['price_vs_sma_pct']:.2f}%")
    else:
        print("  📉 현재 하락 추세입니다 (가격 < 200일 이동평균)")
        print("  💡 레버리지 사용 중지 권장")
        print(f"  📊 현재가: ${latest['details']['current_price']:.2f}")
        print(f"  📊 200일 MA: ${latest['details']['sma_200']:.2f}")
        print(f"  📊 괴리율: {latest['details']['price_vs_sma_pct']:.2f}%")

    print("\n" + "="*80)
    print("✓ 실행 완료!")
    print("="*80)

    print("\n다른 전략도 시도해보세요:")
    print("  python main.py --strategy 2  (위험 관리)")
    print("  python main.py --strategy 5  (MACD-V)")
    print("  python main.py --strategy all (모든 전략)")

except ImportError as e:
    print(f"\n✗ 오류: 필요한 패키지가 설치되지 않았습니다.")
    print(f"  {e}")
    print("\n해결 방법:")
    print("  pip install pandas numpy yfinance")

except Exception as e:
    print(f"\n✗ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    print("\n문제가 지속되면 GitHub 이슈를 생성해주세요.")
