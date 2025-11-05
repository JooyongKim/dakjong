# Investment Strategy Signal Generators

5개의 독립적이고 모듈화된 투자 전략 신호 발생기 시스템입니다. 각 전략은 Charles H. Dow Award 수상 논문들에 기반하여 개발되었습니다.

## 개요

이 프로젝트는 다음과 같은 5개의 독립적인 투자 전략 모듈을 제공합니다:

1. **Strategy 1**: 시장 패닉 식별 및 저점 매수 (Market Panic Identification)
2. **Strategy 2**: 변동성/하락 속도 기반 위험 관리 (Risk Management)
3. **Strategy 3**: 추세 기반 레버리지 (Trend-Based Leverage)
4. **Strategy 4**: 섹터 로테이션 (Sector Rotation)
5. **Strategy 5**: 변동성 정규화 모멘텀 MACD-V (Volatility-Normalized Momentum)

## 주요 특징

- **모듈성**: 각 전략은 완전히 독립적인 모듈로 구현
- **독립성**: 전략 간 의존성 없음 (개별 실행 가능)
- **유연성**: 파라미터 조정 가능
- **표준화된 출력**: JSON 형식의 일관된 신호 출력
- **확장성**: 새로운 전략 추가 용이

## 프로젝트 구조

```
dakjong/
├── strategies/              # 전략 모듈
│   ├── __init__.py
│   ├── base_strategy.py    # 전략 베이스 클래스
│   ├── strategy_1_panic_buy.py
│   ├── strategy_2_risk_management.py
│   ├── strategy_3_leverage.py
│   ├── strategy_4_sector_rotation.py
│   └── strategy_5_macd_v.py
├── utils/                   # 유틸리티 모듈
│   ├── __init__.py
│   ├── data_loader.py      # 데이터 로딩
│   └── indicators.py       # 기술적 지표
├── main.py                  # 통합 실행 스크립트
├── example_usage.py         # 사용 예제
├── requirements.txt         # 의존성 패키지
└── README.md
```

## 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd dakjong
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

필수 패키지:
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.28
- pandas-ta >= 0.3.14b
- requests >= 2.31.0

## 사용 방법

### 모든 전략 실행

```bash
python main.py --strategy all
```

### 개별 전략 실행

```bash
# Strategy 1만 실행
python main.py --strategy 1

# Strategy 3만 실행
python main.py --strategy 3
```

### 날짜 범위 지정

```bash
python main.py --strategy all --start-date 2020-01-01 --end-date 2024-12-31
```

### Python 코드에서 사용

```python
from utils.data_loader import DataLoader
from strategies import LeverageStrategy

# 데이터 로더 초기화
data_loader = DataLoader(start_date='2020-01-01')

# 데이터 로드
spy_data = data_loader.load_market_index('SPY')

# 전략 초기화
strategy = LeverageStrategy(
    sma_period=200,
    leverage_multiple=1.5
)

# 신호 생성
signals_df = strategy.generate_signals(market_data=spy_data)

# 최신 신호 확인
latest_signal = strategy.get_latest_signal()
print(latest_signal)
```

## 전략 상세 설명

### Strategy 1: 시장 패닉 식별 및 저점 매수

**기반 논문**: Vince & Williams (2024); Diodato (2019)

**목적**: 극단적 투매 현상을 감지하여 매수 신호 생성

**핵심 지표**:
- NYSE New Lows Ratio (3일 이동평균)
- STCO (Short-Term Cumulative Oscillator)

**출력 신호**: `BUY` 또는 `NONE`

**조정 가능한 파라미터**:
- `nl_ma_period`: 신저가 비율 이동평균 기간 (기본값: 3)
- `nl_threshold`: 신저가 비율 임계값 (기본값: 0.50)
- `stco_threshold`: STCO 임계값 (기본값: 80)
- `entry_logic`: 'Delayed' 또는 'Confirmed'
- `delay_days`: 지연 진입 대기일 (기본값: 10)

### Strategy 2: 변동성/하락 속도 기반 위험 관리

**기반 논문**: Thrasher (2017 & 2023)

**목적**: 시장 잠재 위험 증가 시 경고 신호 생성

**핵심 지표**:
- VIX 표준편차 (20일)
- 52주 최고가 대비 하락률
- 200일 이동평균 돌파

**출력 신호**: `RISK_OFF` 또는 `NONE`

**조정 가능한 파라미터**:
- `vix_std_period`: VIX 표준편차 기간 (기본값: 20)
- `vix_std_threshold`: VIX 표준편차 임계값 (기본값: 0.86)
- `drop_pct`: 하락률 (기본값: 0.05 = 5%)
- `canary_days`: 카나리아 신호 기준일 (기본값: 15)

### Strategy 3: 추세 기반 레버리지

**기반 논문**: Gayed & Bilello (2016)

**목적**: S&P 500 장기 추세에 따라 레버리지 사용/해제

**핵심 지표**:
- 200일 단순 이동평균

**출력 신호**: `LEVERAGE_ON` 또는 `LEVERAGE_OFF`

**조정 가능한 파라미터**:
- `sma_period`: 이동평균 기간 (기본값: 200)
- `leverage_multiple`: 레버리지 배수 (기본값: 1.5)

### Strategy 4: 섹터 로테이션

**기반 논문**: Cain & Connors (2020); Giordano (2018)

**목적**: 모멘텀과 변동성 기반으로 상위 섹터 선정

**핵심 지표**:
- 6개월 모멘텀
- 100일 변동성
- 200일 이동평균 (시장 필터)

**출력 신호**: `HOLD_SECTORS` 또는 `CASH`

**조정 가능한 파라미터**:
- `momentum_period`: 모멘텀 계산 기간 (개월, 기본값: 6)
- `volatility_period`: 변동성 계산 기간 (일, 기본값: 100)
- `top_n_sectors`: 선정할 섹터 수 (기본값: 3)
- `weighting_method`: 'EW' (동일비중) 또는 'IV' (변동성역가중)
- `rebalance_frequency`: 'Monthly' 또는 'Quarterly'

### Strategy 5: 변동성 정규화 모멘텀 (MACD-V)

**기반 논문**: Spiroglou (2022)

**목적**: MACD-V를 통한 자산 모멘텀 상태 분류

**핵심 지표**:
- MACD-V = ((EMA_Short - EMA_Long) / ATR) * 100
- 시장 체제 (200일 이동평균 기준)

**출력 신호**: `Strong_Up`, `Weakening_Up`, `Strong_Down`, `Weakening_Down`

**조정 가능한 파라미터**:
- `ema_short`: 단기 EMA 기간 (기본값: 12)
- `ema_long`: 장기 EMA 기간 (기본값: 26)
- `atr_period`: ATR 기간 (기본값: 26)
- `thresholds`: MACD-V 분류 임계값 딕셔너리

## 신호 출력 형식

모든 전략은 다음과 같은 표준화된 JSON 형식으로 신호를 출력합니다:

```json
{
  "strategy_id": "Strategy_3_Leverage",
  "strategy_name": "Trend-Based Leverage",
  "date": "2024-11-04",
  "signal": "LEVERAGE_ON",
  "asset": "SPY",
  "details": {
    "reason": "Price_Above_SMA",
    "leverage_multiple": 1.5,
    "current_price": 450.25,
    "sma_200": 435.80,
    "price_vs_sma_pct": 3.32
  }
}
```

## 데이터 요구사항

### yfinance를 통해 자동 수집 가능:
- 시장 지수 (SPY, QQQ, DIA)
- VIX 지수
- 섹터 ETF (XLE, XLF, XLK 등 11개)
- 안전자산 ETF (SHY, BIL)

### 별도 소스 필요 (Strategy 1):
- NYSE 광역 데이터:
  - 신저가 비율 (New Lows Ratio)
  - 상승/하락 거래량 비율
  - 상승/하락 종목 수 비율

**주의**: 현재 구현에서는 NYSE 광역 데이터를 모의 데이터로 제공합니다. 실제 운용 시에는 별도의 데이터 소스(유료 API, 웹 스크래핑 등)가 필요합니다.

## 예제

더 많은 사용 예제는 `example_usage.py` 파일을 참조하세요.

```python
# Strategy 3 간단한 예제
from utils.data_loader import DataLoader
from strategies import LeverageStrategy
from datetime import datetime, timedelta

# 최근 2년 데이터 로드
start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
data_loader = DataLoader(start_date=start_date)

# SPY 데이터 로드
spy_data = data_loader.load_market_index('SPY')

# 전략 초기화 및 실행
strategy = LeverageStrategy(sma_period=200, leverage_multiple=2.0)
signals_df = strategy.generate_signals(market_data=spy_data)

# 최신 신호 확인
latest_signal = strategy.get_latest_signal()
print(latest_signal)
```

## 개발 원칙

1. **모듈성**: 각 전략은 독립적인 모듈로 개발
2. **독립성**: 전략 간 신호 또는 상태 의존성 없음
3. **개별 실행**: 각 전략을 선택적으로 실행 가능
4. **표준화**: 일관된 인터페이스 및 출력 형식

## 확장 방법

새로운 전략을 추가하려면:

1. `strategies/` 디렉토리에 새 전략 모듈 생성
2. `BaseStrategy` 클래스를 상속
3. `generate_signals()` 및 `get_latest_signal()` 메서드 구현
4. `strategies/__init__.py`에 등록
5. `main.py`에 실행 함수 추가

예시:

```python
from strategies.base_strategy import BaseStrategy

class MyNewStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__(
            strategy_id="Strategy_6_MyNew",
            strategy_name="My New Strategy"
        )
        self.param1 = param1
        self.param2 = param2

    def generate_signals(self, data):
        # 신호 생성 로직
        pass

    def get_latest_signal(self):
        # 최신 신호 반환
        pass
```

## 거래 액션 가이드

각 전략의 신호에 따른 구체적인 거래 액션 요약입니다. 자세한 내용은 [TRADING_GUIDE.md](TRADING_GUIDE.md)를 참조하세요.

### Strategy 1: Market Panic Buy
| 신호 | 거래 액션 |
|------|-----------|
| **BUY** | **매수**: SPY 또는 QQQ (포트폴리오의 10-20%)<br>목표 수익률: +10-15%<br>손절: -5% |
| **NONE** | **대기**: 기존 포지션 유지 또는 관망 |

### Strategy 2: Risk Management
| 신호 | 거래 액션 |
|------|-----------|
| **RISK_OFF** | **매도**: 모든 주식 포지션 청산<br>**매수**: SHY, BIL (안전자산) 또는 100% 현금 |
| **NONE** | **유지**: 정상 시장 환경, 기존 포지션 유지 |

### Strategy 3: Trend-Based Leverage
| 신호 | 거래 액션 |
|------|-----------|
| **LEVERAGE_ON** | **매수**: SPXL (3배 레버리지 ETF) 또는 SPY에 1.5배 레버리지 적용 |
| **LEVERAGE_OFF** | **매도**: 레버리지 포지션 청산<br>**전환**: SPY 1배로 전환 또는 현금/SHY |

### Strategy 4: Sector Rotation
| 신호 | 거래 액션 |
|------|-----------|
| **HOLD_SECTORS** | **리밸런싱**: 선정 섹터 매수 (예: XLI, XLC, XLU)<br>제외 섹터 매도<br>월말/분기말 리밸런싱 |
| **CASH** | **청산**: 모든 섹터 ETF 매도, 100% 현금 또는 SHY 보유 |

### Strategy 5: MACD-V Momentum
| 신호 | 거래 액션 |
|------|-----------|
| **Strong_Up** | **공격적**: 주식 중심 (SPY 50-70%), 강세 자산 배분 |
| **Weakening_Up** | **유지/축소**: 포지션 유지, 현금 비중 증가 (15-20%) |
| **Strong_Down** | **방어적**: 주식 청산, 채권/현금 중심 (TLT, GLD 70%+) |
| **Weakening_Down** | **재진입**: 점진적 주식 재진입 고려 (10-30%) |

### 시각화

각 전략의 지표와 신호를 시각화할 수 있습니다:

```python
from utils.data_loader import DataLoader
from strategies import LeverageStrategy

loader = DataLoader(start_date='2023-01-01')
spy_data = loader.load_market_index('SPY')

strategy = LeverageStrategy()
strategy.plot(market_data=spy_data, save_path='strategy_chart.png')
```

모든 전략 시각화 테스트:
```bash
python test_visualization.py
```

## 주의사항

1. **백테스팅 전용**: 이 코드는 교육 및 연구 목적입니다. 실제 투자에 사용하기 전에 충분한 검증이 필요합니다.
2. **데이터 한계**: NYSE 광역 데이터는 yfinance에서 제공되지 않으므로 별도 소스가 필요합니다.
3. **파라미터 최적화**: 각 전략의 파라미터는 시장 상황과 투자 목표에 따라 조정이 필요합니다.
4. **리스크 관리**: 모든 투자 전략은 적절한 리스크 관리와 함께 사용되어야 합니다.
5. **전문가 상담**: 실제 투자 전 재무 전문가와 상담하시기 바랍니다.

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

## 기여

버그 리포트, 기능 제안, 풀 리퀘스트 환영합니다.

## 참고 문헌

1. Vince, R., & Williams, L. (2024). Charles H. Dow Award Paper
2. Diodato, M. (2019). Market Breadth Indicators
3. Thrasher, D. (2017, 2023). Volatility and Risk Management
4. Gayed, M., & Bilello, C. (2016). Trend Following with Leverage
5. Cain, M., & Connors, L. (2020). Sector Rotation Strategies
6. Giordano, R. (2018). Quantamental Investing
7. Spiroglou, P. (2022). MACD-V: Volatility-Normalized Momentum

## 문의

질문이나 문의사항이 있으시면 이슈를 생성해 주세요.
