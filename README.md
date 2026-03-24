# Quantt

**Version:** 0.0.105
**Status:** Active (In Development)

## Description

Quantt is a trading bot designed to measure market conditions and provide a local trading experience. It automates cryptocurrency trading using multiple analytical approaches to improve operational accuracy.

---

## Purpose and Scope

**Problem**
Automate cryptocurrency trading using CCXT-supported exchanges (Binance, Bybit, OKX) with multiple strategies for improved accuracy.

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
* AI-based forecasting
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

**Environment Variables**

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

## Project Structure

**UI → Engine Architecture**

**UI Flow**

* User → Config → UI → Engine
* User → Request Performance → Engine → UI

**Engine Structure**

* OOP-based class management:

  * Start / Stop control
  * Variable configuration
  * Database management
* Core responsibilities:

  * Performance tracking
  * Configuration handling

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

**Execution**

* Backtesting: Run via UI
* Live simulation:

  * Set exchange (Binance or Bybit)
  * Provide API credentials
  * Enable demo mode

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

* Designed for local usage
* Limited scalability
* Single exchange focus per session

---

## Security

* Local application
* Users are responsible for API usage and associated risks

---

## Contributing

**Guidelines**

* Contributions via GitHub only
* Ensure completeness and testing before pull requests
* Large changes have lower acceptance probability

**Code Style**

* Procedural with structured OOP organization
* Naming:

  * snake_case
  * SCREAMING_SNAKE_CASE
* Indentation: 4 spaces

---

## License

MIT

---

## Maintainers

* THI100 (solo project)
