# 거래 액션 가이드 (Trading Action Guide)

이 문서는 각 전략의 신호에 따른 구체적인 거래 액션을 설명합니다.

---

## Strategy 1: Market Panic Identification and Bottom Buying

### 신호 타입

#### 1. `BUY` 신호
**의미**: 극단적인 시장 패닉 상황 감지, 저점 매수 기회

**거래 액션**:
- **매수**: SPY (S&P 500 ETF) 또는 QQQ (NASDAQ ETF)
- **타이밍**: 신호 발생 즉시 또는 지연 진입(delay_days 파라미터에 따라)
- **포지션 크기**: 포트폴리오의 10-20% (리스크 허용도에 따라 조정)
- **청산**: 가격이 회복되거나 추가 하락 시 손절

**예시**:
```
신호 날짜: 2024-03-15
액션: SPY 100주 매수 @ $450
목표가: +10-15% 상승 시 청산
손절가: -5% 하락 시 청산
```

#### 2. `NONE` 신호
**의미**: 패닉 조건 미달, 관망

**거래 액션**:
- 기존 포지션 유지 또는 대기

---

## Strategy 2: Volatility/Decline Speed Based Risk Management

### 신호 타입

#### 1. `RISK_OFF` 신호
**의미**: 시장 위험 증가, 방어 태세 전환

**거래 액션**:
- **매도**: 모든 주식 포지션 청산 (SPY, QQQ, 섹터 ETF 등)
- **매수**: 안전자산으로 이동
  - SHY (1-3년 만기 국채 ETF)
  - BIL (단기 국채 ETF)
  - 또는 현금 보유
- **타이밍**: 신호 확인 후 1-2거래일 내
- **포지션**: 100% 안전자산으로 전환

**예시**:
```
신호 날짜: 2024-04-15
액션:
  - SPY 전량 매도 @ $537
  - SHY 매수 (매도 금액의 100%)
리스크 복귀: VIX 안정화 및 가격이 200일선 위로 회복 시
```

#### 2. `NONE` 신호
**의미**: 정상 시장 환경

**거래 액션**:
- 기존 포지션 유지 또는 다른 전략 신호 따름

---

## Strategy 3: Trend-Based Leverage

### 신호 타입

#### 1. `LEVERAGE_ON` 신호
**의미**: 강세장 확인, 레버리지 사용 가능

**거래 액션**:
- **Option A (레버리지 ETF 사용)**:
  - 매수: SPXL (S&P 500 3배 레버리지 ETF)
  - 또는: TQQQ (NASDAQ 100 3배 레버리지 ETF)
  - 포지션: 일반 투자 금액의 33-50% (레버리지 고려)

- **Option B (마진/선물 사용)**:
  - SPY에 1.5배 레버리지 적용
  - 예: $100,000 → $150,000 익스포저

**예시**:
```
신호 날짜: 2024-05-12
현재 가격: SPY $583
액션:
  - SPXL 50주 매수 @ $140 (약 $50,000 투자 = SPY $150,000 상당)
  또는
  - SPY 250주 매수 (일반) + 마진으로 125주 추가
```

#### 2. `LEVERAGE_OFF` 신호
**의미**: 약세장 전환, 레버리지 제거

**거래 액션**:
- **매도**: 레버리지 포지션 전량 청산 (SPXL, TQQQ 등)
- **매수**: 일반 ETF로 전환 (SPY, QQQ)
- **또는**: 마진 포지션 정리, 현금 비중 증가

**예시**:
```
신호 날짜: 2024-06-20
액션:
  - SPXL 전량 매도
  - SPY 매수 (일반 1배 익스포저)
```

---

## Strategy 4: Quantamental Sector Rotation

### 신호 타입

#### 1. `HOLD_SECTORS` 신호
**의미**: 선정된 상위 섹터 보유

**거래 액션**:
- **리밸런싱**: 월말/분기말 (rebalance_frequency에 따라)
- **매도**: 이전에 보유했지만 이번 리밸런싱에서 제외된 섹터
- **매수**: 새로 선정된 섹터 ETF

**포지션 구성** (예시: top_n_sectors=3, weighting_method='EW'):
```
신호 날짜: 2024-11-03
선정 섹터:
  - XLI (산업) 33.33%
  - XLC (통신) 33.33%
  - XLU (유틸리티) 33.33%

액션:
  1. 기존 포지션 중 제외된 섹터 매도 (예: XLE, XLF)
  2. 새로 선정된 섹터 매수:
     - XLI 매수 ($33,333 투자)
     - XLC 매수 ($33,333 투자)
     - XLU 매수 ($33,333 투자)
```

**포지션 구성** (변동성 역가중, weighting_method='IV'):
```
선정 섹터 (변동성 고려):
  - XLU (낮은 변동성) 40%
  - XLI (중간 변동성) 35%
  - XLC (높은 변동성) 25%
```

#### 2. `CASH` 신호
**의미**: 시장 필터 미달 (SPY < 200일 SMA), 약세장

**거래 액션**:
- **매도**: 모든 섹터 ETF 포지션 청산
- **보유**: 현금 또는 SHY/BIL (단기 국채)

**예시**:
```
신호 날짜: 2024-12-15
액션:
  - 모든 섹터 ETF 매도 (XLI, XLC, XLU 등)
  - SHY 매수 또는 100% 현금 보유
재진입: SPY가 200일 SMA 위로 상승 시
```

---

## Strategy 5: Volatility-Normalized Momentum (MACD-V)

### 신호 타입 및 자산별 액션

이 전략은 여러 자산의 모멘텀 상태를 분류하여 포트폴리오 구성을 제안합니다.

#### 신호 분류

| 신호 | 시장 체제 | 의미 | 거래 액션 |
|------|-----------|------|-----------|
| `Strong_Up` | Bull | 강한 상승 모멘텀 | 공격적 포지션 (주식 중심) |
| `Weakening_Up` | Bull | 약화되는 상승 | 포지션 축소 또는 유지 |
| `Strong_Down` | Bear | 강한 하락 모멘텀 | 방어적 포지션 (채권/현금) |
| `Weakening_Down` | Bear | 약화되는 하락 | 점진적 재진입 고려 |

#### 자산별 상태 해석

**자산 유니버스**: SPY, TLT, GLD, DBC

**MACD-V 상태**:
- `Overbought` (>150): 과매수, 차익실현 고려
- `Rallying` (50~150): 강한 상승, 보유
- `Ranging_Upper` (0~50): 횡보 상단
- `Ranging_Lower` (-50~0): 횡보 하단
- `Reversing` (-150~-50): 반전 신호
- `Oversold` (<-150): 과매도, 매수 고려

#### 포트폴리오 구성 예시

**시나리오 1: 강세장 (Bull Market)**
```
신호: Strong_Up
자산 상태:
  - SPY: Rallying (MACD-V = 55)
  - TLT: Rallying (MACD-V = 120)
  - GLD: Overbought (MACD-V = 156)
  - DBC: Ranging_Lower (MACD-V = 18)

포트폴리오 구성:
  - SPY 50% (주력)
  - TLT 20% (채권 강세)
  - GLD 10% (과매수, 축소)
  - DBC 5% (약세)
  - 현금 15%
```

**시나리오 2: 약세장 (Bear Market)**
```
신호: Strong_Down
자산 상태:
  - SPY: Reversing (MACD-V = -140)
  - TLT: Overbought (MACD-V = 165)
  - GLD: Rallying (MACD-V = 80)
  - DBC: Oversold (MACD-V = -180)

포트폴리오 구성:
  - SPY 0% (약세, 청산)
  - TLT 50% (채권 강세)
  - GLD 30% (안전자산)
  - DBC 10% (과매도 반등 기대)
  - 현금 10%
```

**시나리오 3: 혼조장**
```
신호: Weakening_Up
자산 상태:
  - SPY: Ranging_Upper (MACD-V = 35)
  - TLT: Ranging_Lower (MACD-V = -20)
  - GLD: Rallying (MACD-V = 90)
  - DBC: Ranging_Lower (MACD-V = -30)

포트폴리오 구성:
  - SPY 30% (횡보)
  - TLT 20% (약세)
  - GLD 25% (강세)
  - DBC 5%
  - 현금 20% (불확실성 대비)
```

---

## 종합 거래 전략 사용 예시

### 복합 전략 사용

여러 전략을 동시에 사용하는 경우:

#### 예시 1: 보수적 투자자
```
전략 조합: Strategy 2 (위험관리) + Strategy 3 (레버리지)

룰:
1. Strategy 2가 RISK_OFF → 모든 포지션 청산, 안전자산
2. Strategy 2가 NONE:
   - Strategy 3이 LEVERAGE_ON → SPY 투자
   - Strategy 3이 LEVERAGE_OFF → SHY 투자

현재 신호:
  - Strategy 2: NONE
  - Strategy 3: LEVERAGE_ON

액션: SPY 100% 투자
```

#### 예시 2: 공격적 투자자
```
전략 조합: Strategy 3 (레버리지) + Strategy 5 (MACD-V)

룰:
1. Strategy 3이 LEVERAGE_ON + Strategy 5가 Strong_Up → SPXL 투자
2. Strategy 3이 LEVERAGE_OFF → SPY로 전환
3. Strategy 5 자산 배분 참고

현재 신호:
  - Strategy 3: LEVERAGE_ON
  - Strategy 5: Strong_Up

액션: SPXL 70%, TLT 20%, 현금 10%
```

#### 예시 3: 균형 투자자
```
전략 조합: Strategy 2 + Strategy 4 (섹터로테이션) + Strategy 5

룰:
1. Strategy 2가 RISK_OFF → 안전자산 100%
2. Strategy 2가 NONE:
   - Strategy 4 섹터 선정 따름 (60%)
   - Strategy 5 자산 배분 참고 (40%)

현재 신호:
  - Strategy 2: NONE
  - Strategy 4: HOLD_SECTORS (XLI, XLC, XLU)
  - Strategy 5: Weakening_Up

포트폴리오:
  - XLI 20%
  - XLC 20%
  - XLU 20%
  - TLT 20% (Strategy 5 참고)
  - 현금 20% (Weakening 신호로 방어)
```

---

## 리스크 관리 원칙

### 1. 포지션 크기 관리
- 단일 전략: 포트폴리오의 최대 100%
- 레버리지 사용 시: 최대 1.5-2배
- 개별 섹터: 최대 33% (3개 섹터 분산)

### 2. 손절 규칙
- 패닉 매수 (Strategy 1): -5% 손절
- 일반 포지션: -10% 손절
- 레버리지 포지션: -7% 손절 (변동성 크므로)

### 3. 리밸런싱
- Strategy 4: 월말 또는 분기말
- Strategy 5: 주간 검토, 큰 변화 시 조정
- 기타: 신호 변경 시 즉시

### 4. 거래 비용 고려
- 빈번한 매매 지양
- ETF 스프레드 확인
- 세금 효율성 고려 (장기 보유 vs 단기 매매)

---

## 주의사항

⚠️ **중요**: 이 가이드는 교육 및 연구 목적입니다. 실제 투자 시:

1. **백테스팅 필수**: 과거 데이터로 전략 성과 검증
2. **소액 테스트**: 실전 투자 전 소액으로 검증
3. **리스크 평가**: 개인의 리스크 허용도에 맞게 조정
4. **전문가 상담**: 필요 시 재무 전문가와 상담
5. **시장 모니터링**: 전략이 작동하지 않는 시장 환경도 존재

---

## 문의 및 피드백

전략 사용 중 문제나 개선 사항이 있다면 GitHub Issues에 제출해주세요.
