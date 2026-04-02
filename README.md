# Quantt

**Version:** 0.0.121
**Status:** Active (In Development)

---

## Description

Quantt is a trading bot designed to measure market conditions and provide a local trading experience. It automates cryptocurrency trading using multiple analytical approaches to improve operational accuracy.

---

## Purpose and Scope

**Problem**
Automate cryptocurrency trading using CCXT-supported exchanges (Binance, Bybit, OKX) with multiple strategies to improve execution accuracy.

**Target Users**

* Enthusiasts
* Traders
* Companies evaluating talent

**Use Cases**

* Automated cryptocurrency trading
* Custom trading strategies based on user preferences

---

## Features

**Core Features**

* Technical analysis
* AI-based market signal generation (time-series forecasting)
* Custom risk management
* Order management and execution
* Local-first usage

**Non-Goals**

* Full automation of all trading decisions
* Financial management beyond broker interaction

---

## Tech Stack

**Languages**

* Python
* JavaScript
* TypeScript

**Frameworks and Libraries**

* React
* Vite
* Electron
* CCXT
* PyTorch
* vectorbt
* Pandas
* NumPy
* FastAPI
* SQLAlchemy
* loguru

---

## Installation

**Prerequisites**

* CPU: 2 cores minimum
* RAM: 2 GB minimum (4 GB recommended)
* Storage: ~200 MB
* OS: Any
* Python: 3.11
* Node.js: 25+

**Setup**
Refer to `Setup.md`

---

## Quick Start

```bash
    # clone
    git clone <repo>
    cd quantt
    
    # engine
    cd quantt-engine
    py -m venv venv
    source venv/bin/activate
    pip install .
    # start the engine
    py main.py
    
    # ui
    cd quantt-ui
    npm install
    # start the UI
    npm run electron
    npm run vite
```

---

## Environment Variables

* `API`
* `API_SECRET`

---

## Usage

**Input**

* User-defined configurations via UI

**Output**

* Performance metrics
* Graphical analytics

---

## Architecture Overview

```text
[ UI (Electron + React) ]
            ↓
        [ FastAPI ]
            ↓
 [ Trading Engine (OOP Core) ]
            ↓
 [ Exchange APIs via CCXT ]
            ↓
        [ Database ]
```

---

## AI Forecasting

* Model: Granite TTM 2.1 (fine-tuned)
* Type: Time-series forecasting
* Scope:

  * OHLCV data
  * Active indicators
* Precision:

  * FP64 / FP32
* Performance:

  * Optimized for lightweight execution
  * Runs on 2-core CPU without significant overhead

---

## Configuration

* Location: `Engine/config`
* Note: Contains sensitive API-related data

---

## API

**Ports**

* Engine: 5000
* UI: 3000

**Endpoints**

* Defined in `Engine/API`

---

## Testing

**Backtesting**

* Executed via UI
* Powered by vectorbt

**Simulation (Paper Trading)**

* Use demo mode
* Supported exchanges: Binance, Bybit

**Live Trading**

* Requires API credentials
* User assumes full responsibility

**Frameworks**

* vectorbt
* empyrical
* CCXT (Binance / Bybit)

---

## Build and Deployment

**Steps**
Refer to `Setup.md`

**Environment**

* `.env`
* Python virtual environment (engine)
* `package.json` (UI)

---

## Limitations

* Designed primarily for local usage
* Limited scalability
* Single exchange usage per session

---

## Safety Defaults

* No trading without API configuration
* Demo mode recommended by default
* No custody or storage of user funds

---

## Security

* Local application
* API keys stored locally
* Users are responsible for securing credentials and usage

---

## Roadmap

* Improve AI model accuracy
* Multi-exchange simultaneous support
* Strategy modularization
* Performance optimization

---

## Screenshots / UI Preview

*To be added*

---

## Contributing

**Guidelines**

* Contributions via GitHub only
* Ensure completeness and proper testing before pull requests
* Large changes have lower acceptance probability

**Code Style**

* Procedural with structured OOP organization
* Naming conventions:

  * `snake_case`
  * `SCREAMING_SNAKE_CASE`
* Indentation: 4 spaces

---

## Disclaimer

This software does not provide financial advice. Use at your own risk. The user is solely responsible for any financial decisions and outcomes resulting from the use of this project.

---

## License

MIT

---

## Maintainers

* THI100 (solo project)
