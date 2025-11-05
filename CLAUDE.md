# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based investment strategy signal generator system implementing 5 independent, modular trading strategies based on Charles H. Dow Award-winning research papers. Each strategy operates independently without inter-strategy dependencies.

**Key Design Principles:**
- **Modularity**: Each strategy is a completely independent module
- **Independence**: No dependencies between strategies (can run individually)
- **Standardization**: All strategies use consistent JSON output format
- **Extensibility**: New strategies inherit from `BaseStrategy`

## Common Commands

### Installation
```bash
pip install -r requirements.txt
```

Required packages: pandas>=2.0.0, numpy>=1.24.0, yfinance>=0.2.28, requests>=2.31.0

### Running Strategies

**All strategies:**
```bash
python main.py --strategy all
```

**Individual strategy (1-5):**
```bash
python main.py --strategy 3
python main.py --strategy 1 --start-date 2020-01-01 --end-date 2024-12-31
```

### Testing
Multiple test scripts exist for validation:
- `simple_test.py` - Basic strategy test
- `test_strategies_only.py` - Strategy-only tests (no data loading)
- `test_integration.py` - Full integration tests
- `test_final.py` - Final validation tests
- `test_direct.py`, `test_real.py`, `test_working.py` - Development tests

Run tests directly:
```bash
python simple_test.py
python test_strategies_only.py
```

## Architecture

### Core Components

**1. Strategy Base Class (`strategies/base_strategy.py`)**
- Abstract base class defining the strategy interface
- All strategies must implement:
  - `generate_signals(**kwargs) -> pd.DataFrame`: Main signal generation logic
  - `get_latest_signal() -> Dict[str, Any]`: Returns most recent signal in JSON format
- Provides standardized signal output via `_create_signal_output()`
- Maintains signal history in `signals_history` list

**2. Data Loading (`utils/data_loader.py`)**
- `DataLoader` class handles all market data fetching via yfinance
- Supports: market indices (SPY, QQQ, DIA), VIX, sector ETFs, safe haven ETFs, custom asset universes
- **Important**: NYSE breadth data (Strategy 1) returns mock data - requires separate data source for production use
- Default date range: 5 years ago to today (configurable)

**3. Technical Indicators (`utils/indicators.py`)**
- Static utility class providing common indicators:
  - SMA, EMA, ATR, MACD-V
  - Rolling high/low, volatility, momentum
- Used across strategies to avoid code duplication

### The 5 Strategies

**Strategy 1: Panic Buy** (`strategy_1_panic_buy.py`)
- Identifies extreme market sell-offs using NYSE breadth data
- Key indicators: NYSE New Lows Ratio, STCO (Short-Term Cumulative Oscillator)
- Signals: `BUY` or `NONE`
- **Data dependency**: Requires NYSE breadth data (currently mock data)

**Strategy 2: Risk Management** (`strategy_2_risk_management.py`)
- Detects increasing market risk via volatility and decline speed
- Key indicators: VIX std dev, 52-week high drawdown, 200-day SMA
- Signals: `RISK_OFF` or `NONE`

**Strategy 3: Leverage** (`strategy_3_leverage.py`)
- Simplest strategy - uses/removes leverage based on long-term trend
- Key indicator: 200-day SMA
- Signals: `LEVERAGE_ON` or `LEVERAGE_OFF`

**Strategy 4: Sector Rotation** (`strategy_4_sector_rotation.py`)
- Selects top-performing sectors using momentum and volatility
- Operates on 11 sector ETFs (XLE, XLF, XLK, XLV, XLI, XLP, XLY, XLB, XLU, XLRE, XLC)
- Key indicators: 6-month momentum, 100-day volatility, 200-day SMA filter
- Signals: `HOLD_SECTORS` (with sector list) or `CASH`

**Strategy 5: MACD-V** (`strategy_5_macd_v.py`)
- Volatility-normalized momentum using MACD-V indicator
- Classifies asset momentum states: `Strong_Up`, `Weakening_Up`, `Strong_Down`, `Weakening_Down`
- Key indicator: MACD-V = ((EMA_Short - EMA_Long) / ATR) * 100
- Combines with market regime (above/below 200-day SMA)

### Signal Output Format

All strategies produce standardized JSON output:
```json
{
  "strategy_id": "Strategy_3_Leverage",
  "strategy_name": "Trend-Based Leverage",
  "date": "2024-11-04",
  "signal": "LEVERAGE_ON",
  "asset": "SPY",
  "details": {
    "reason": "Price_Above_SMA",
    "current_price": 450.25,
    "sma_200": 435.80
  }
}
```

## Development Guidelines

### Adding a New Strategy

1. Create new file in `strategies/` directory: `strategy_N_name.py`
2. Inherit from `BaseStrategy`:
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
        # Signal generation logic
        pass

    def get_latest_signal(self):
        # Return latest signal
        pass
```
3. Register in `strategies/__init__.py`
4. Add execution function in `main.py`

### Strategy Independence Rules

- Each strategy must be executable independently
- No shared state between strategies
- Each strategy has its own parameter configuration
- Data loading is done per-strategy (no shared data objects)

### Working with yfinance Data

yfinance returns DataFrames with MultiIndex when downloading multiple tickers. Use `.xs()` to extract single ticker data:
```python
# For multi-ticker downloads
data = yf.download(['SPY', 'TLT'], ...)
spy_close = data['Close']['SPY']  # or data['Close'].xs('SPY', axis=1)
```

Handle yfinance import optionally since it's not always available during testing:
```python
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False
```

### Data Requirements

**Available via yfinance:**
- Market indices: SPY, QQQ, DIA, ^GSPC, ^NDX, ^DJI
- VIX: ^VIX
- Sector ETFs: XLE, XLF, XLK, XLV, XLI, XLP, XLY, XLB, XLU, XLRE, XLC
- Safe haven: SHY, BIL, SHV
- Any other valid ticker

**Not available via yfinance (requires separate source):**
- NYSE breadth data: New Lows Ratio, Advance/Decline ratios, Up/Down Volume ratios
- Current implementation uses mock data in `DataLoader.get_nyse_breadth_data()`

## Important Notes

- This is a backtesting/research codebase, not production trading code
- NYSE breadth data in Strategy 1 is mocked - production requires real data source
- All strategies use historical data; no real-time data feeds
- Parameters in each strategy are configurable and should be adjusted based on market conditions
- The codebase is in Korean (README, comments) but code/variables are in English
