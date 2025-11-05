# 빠른 시작 가이드 (Quick Start)

이 가이드를 따라하면 5분 안에 전략을 실행할 수 있습니다!

## 1단계: 패키지 설치 (1분)

```bash
# 프로젝트 디렉토리로 이동
cd dakjong

# 필수 패키지 설치
pip install pandas numpy yfinance
```

## 2단계: 간단한 테스트 실행 (1분)

### 방법 A: 가장 간단한 전략 (Strategy 3) 테스트

```bash
python main.py --strategy 3
```

이 명령어는 SPY의 200일 이동평균 기반 레버리지 전략을 실행합니다.

### 방법 B: 모든 전략 한번에 실행

```bash
python main.py --strategy all
```

## 3단계: Python 코드에서 직접 사용 (2분)

### 예제 1: Strategy 3 (레버리지) - 가장 간단

```python
from utils.data_loader import DataLoader
from strategies import LeverageStrategy

# 데이터 로드 (최근 2년)
loader = DataLoader(start_date='2023-01-01')
spy_data = loader.load_market_index('SPY')

# 전략 실행
strategy = LeverageStrategy(sma_period=200, leverage_multiple=1.5)
signals = strategy.generate_signals(market_data=spy_data)

# 최신 신호 확인
print(strategy.get_latest_signal())
```

### 예제 2: Strategy 2 (위험 관리)

```python
from utils.data_loader import DataLoader
from strategies import RiskManagementStrategy

# 데이터 로드
loader = DataLoader(start_date='2023-01-01')
spy_data = loader.load_market_index('SPY')
vix_data = loader.load_vix()

# 전략 실행
strategy = RiskManagementStrategy()
signals = strategy.generate_signals(vix_data=vix_data, market_data=spy_data)

# 최신 신호 확인
print(strategy.get_latest_signal())
```

### 예제 3: Strategy 5 (MACD-V)

```python
from utils.data_loader import DataLoader
from strategies import MACDVStrategy

# 데이터 로드
loader = DataLoader(start_date='2023-01-01')
asset_data = loader.load_asset_universe(['SPY', 'TLT', 'GLD', 'DBC'])

# 전략 실행
strategy = MACDVStrategy()
signals = strategy.generate_signals(asset_data=asset_data)

# 최신 신호 확인
latest = strategy.get_latest_signal()
print(f"신호: {latest['signal']}")
print(f"시장 체제: {latest['details']['market_regime']}")
```

## 실행 옵션

### 날짜 범위 지정

```bash
# 2020년부터 2024년까지 데이터로 실행
python main.py --strategy 3 --start-date 2020-01-01 --end-date 2024-12-31
```

### 개별 전략 실행

```bash
python main.py --strategy 1  # 패닉 매수
python main.py --strategy 2  # 위험 관리
python main.py --strategy 3  # 레버리지
python main.py --strategy 4  # 섹터 로테이션
python main.py --strategy 5  # MACD-V
```

## 예상 출력

Strategy 3을 실행하면 다음과 같은 출력을 볼 수 있습니다:

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

## 문제 해결

### yfinance 설치 실패 시

```bash
# 대안 1: 최신 pip 사용
pip install --upgrade pip
pip install yfinance

# 대안 2: conda 사용 (anaconda가 설치된 경우)
conda install -c conda-forge yfinance
```

### ImportError 발생 시

```bash
# 현재 디렉토리에서 실행하고 있는지 확인
pwd  # /path/to/dakjong 여야 함

# Python 경로 확인
python -c "import sys; print(sys.path)"
```

## 다음 단계

1. **파라미터 조정**: 각 전략의 파라미터를 조정해보세요
   ```python
   strategy = LeverageStrategy(
       sma_period=150,      # 200 대신 150일
       leverage_multiple=2.0  # 1.5배 대신 2배
   )
   ```

2. **백테스팅**: 과거 데이터로 성과 분석

3. **신호 히스토리**: 모든 신호 확인
   ```python
   all_signals = strategy.get_signals_history()
   ```

4. **커스텀 전략**: `strategies/base_strategy.py`를 상속받아 새로운 전략 추가

## 주의사항

⚠️ **NYSE 광역 데이터**: Strategy 1은 NYSE 광역 데이터가 필요합니다. 현재는 모의 데이터를 사용합니다. 실제 운용 시 별도 데이터 소스가 필요합니다.

⚠️ **백테스팅 전용**: 이 코드는 교육/연구 목적입니다. 실제 투자 전 충분한 검증이 필요합니다.

## 지원

문제가 발생하면 GitHub 이슈를 생성해주세요.
