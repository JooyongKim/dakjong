"""
Script to add recommended_action fields to all strategy signal outputs.
"""

# Strategy 1: Panic Buy
strategy_1_updates = {
    'BUY': {
        'recommended_action': "매수: SPY 또는 QQQ 매수 (포트폴리오의 10-20%), 목표 수익률 +10-15%, 손절 -5%",
        'action_en': "BUY: SPY or QQQ (10-20% of portfolio), target +10-15%, stop-loss -5%"
    },
    'NONE': {
        'recommended_action': "대기: 패닉 조건 미달, 기존 포지션 유지 또는 관망",
        'action_en': "HOLD: No panic conditions, maintain existing positions or wait"
    }
}

# Strategy 2: Risk Management
strategy_2_updates = {
    'RISK_OFF': {
        'recommended_action': "매도: 모든 주식 포지션 청산, 안전자산(SHY, BIL) 또는 현금 100% 전환",
        'action_en': "SELL: Close all equity positions, move 100% to safe assets (SHY, BIL) or cash"
    },
    'NONE': {
        'recommended_action': "유지: 정상 시장 환경, 기존 포지션 유지",
        'action_en': "HOLD: Normal market conditions, maintain existing positions"
    }
}

# Strategy 4: Sector Rotation
strategy_4_updates = {
    'HOLD_SECTORS': {
        # This will be dynamic based on selected sectors
        'template': "리밸런싱: 선정 섹터 매수 ({sectors}), 제외 섹터 매도",
        'template_en': "REBALANCE: Buy selected sectors ({sectors}), Sell excluded sectors"
    },
    'CASH': {
        'recommended_action': "청산: 모든 섹터 ETF 매도, 현금 또는 SHY 100% 보유 (약세장)",
        'action_en': "LIQUIDATE: Sell all sector ETFs, hold 100% cash or SHY (bear market)"
    }
}

# Strategy 5: MACD-V
strategy_5_updates = {
    'Strong_Up': {
        'recommended_action': "공격적 포지션: 주식 중심 (SPY 50-70%), 강세 자산 배분",
        'action_en': "AGGRESSIVE: Equity-focused (SPY 50-70%), allocate to bullish assets"
    },
    'Weakening_Up': {
        'recommended_action': "유지/축소: 포지션 유지하되 현금 비중 증가 (15-20%), 방어적 전환 준비",
        'action_en': "MAINTAIN/REDUCE: Hold positions, increase cash (15-20%), prepare defensive shift"
    },
    'Strong_Down': {
        'recommended_action': "방어적 포지션: 주식 청산 또는 최소화, 채권/현금 중심 (TLT, GLD 70%+)",
        'action_en': "DEFENSIVE: Liquidate or minimize equities, focus on bonds/cash (TLT, GLD 70%+)"
    },
    'Weakening_Down': {
        'recommended_action': "점진적 재진입: 하락 약화 시 점진적 주식 재진입 고려 (10-30%)",
        'action_en': "GRADUAL RE-ENTRY: Consider gradual equity re-entry as decline weakens (10-30%)"
    }
}

print("Action recommendation templates created.")
print("\nStrategy 1 (Panic Buy):")
for signal, action in strategy_1_updates.items():
    print(f"  {signal}: {action['action_en']}")

print("\nStrategy 2 (Risk Management):")
for signal, action in strategy_2_updates.items():
    print(f"  {signal}: {action['action_en']}")

print("\nStrategy 4 (Sector Rotation):")
for signal, action in strategy_4_updates.items():
    if 'template_en' in action:
        print(f"  {signal}: {action['template_en']}")
    else:
        print(f"  {signal}: {action['action_en']}")

print("\nStrategy 5 (MACD-V):")
for signal, action in strategy_5_updates.items():
    print(f"  {signal}: {action['action_en']}")

print("\nNext: Manually update strategy files with these actions.")
