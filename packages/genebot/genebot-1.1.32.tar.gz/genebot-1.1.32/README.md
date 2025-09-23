# Trading Bot Python

A comprehensive Python trading bot for cryptocurrency markets with support for multiple exchanges, configurable strategies, and robust risk management.

## Features

- **Multi-Exchange Support**: Connect to multiple cryptocurrency exchanges via CCXT
- **Multi-Market Trading**: Support for both cryptocurrency and forex markets
- **Strategy Orchestration**: Intelligent coordination of multiple trading strategies
- **Configurable Strategies**: Pluggable trading strategy framework with 13+ built-in strategies
- **Advanced Risk Management**: Portfolio-level and strategy-level risk controls
- **Performance-Based Allocation**: Automatic capital allocation based on strategy performance
- **Cross-Market Arbitrage**: Arbitrage opportunities across different markets and exchanges
- **Data Management**: Historical data collection and storage with unified data layer
- **Backtesting**: Comprehensive backtesting with multi-strategy support
- **Monitoring & Analytics**: Extensive logging, performance tracking, and real-time monitoring
- **CLI Interface**: Comprehensive command-line interface for all operations
- **API Access**: REST API for programmatic access and integration

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd trading-bot-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add your exchange API keys and other settings
```

### 3. Run the Bot

#### Traditional Single-Strategy Mode

```bash
# Run the main application
python main.py

# Or using the CLI
genebot start
```

#### Strategy Orchestration Mode (Recommended)

```bash
# Initialize orchestrator configuration
genebot orchestrator-migrate generate

# Start the orchestrator
genebot orchestrator-start --daemon

# Monitor orchestrator performance
genebot orchestrator-monitor
```

## Strategy Orchestration

The Strategy Orchestration system is the recommended way to run genebot, providing intelligent coordination of multiple trading strategies with automatic allocation management and advanced risk controls.

### Key Benefits

- **Intelligent Allocation**: Automatically allocates capital across strategies based on performance
- **Risk Management**: Portfolio-level risk controls and correlation monitoring
- **Performance Optimization**: Continuous optimization of strategy combinations
- **Unified Monitoring**: Single dashboard for all strategies and performance metrics
- **Cross-Market Coordination**: Seamless coordination between crypto and forex strategies

### Quick Start with Orchestrator

```bash
# Analyze existing setup (if migrating)
genebot orchestrator-migrate analyze

# Generate orchestrator configuration
genebot orchestrator-migrate generate --allocation-method performance_based

# Start orchestrator
genebot orchestrator-start --daemon

# Monitor performance
genebot orchestrator-monitor --hours 24

# Check status
genebot orchestrator-status --verbose
```

### Available Strategies

The orchestrator can coordinate all available strategies:

**Crypto Strategies:**
- Moving Average Strategy
- RSI Strategy  
- Mean Reversion Strategy
- Multi-Indicator Strategy
- Advanced Momentum Strategy
- ATR Volatility Strategy
- ML Pattern Strategy

**Forex Strategies:**
- Forex Carry Trade Strategy
- Forex Session Strategy
- Forex News Strategy

**Cross-Market Strategies:**
- Cross-Market Arbitrage Strategy
- Triangular Arbitrage Strategy
- Crypto-Forex Arbitrage Strategy

### Allocation Methods

- **Equal Weight**: Equal allocation across all strategies
- **Performance Based**: Allocation based on risk-adjusted returns (recommended)
- **Risk Parity**: Allocation based on risk contribution

## Project Structure

```
trading-bot-python/
├── src/                    # Source code
│   └── __init__.py
├── tests/                  # Test files
│   └── __init__.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── logging.py         # Logging configuration
├── docs/                   # Documentation
│   └── README.md
├── main.py                 # Application entry point
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Configuration

The bot uses environment variables for configuration. Key settings include:

- **Database**: SQLite or PostgreSQL connection
- **Exchanges**: API keys for supported exchanges
- **Risk Management**: Position limits and stop-loss settings
- **Logging**: Log level and output format

See `.env.example` for all available configuration options.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Requirements

- Python 3.8+
- Virtual environment (recommended)
- Exchange API keys for trading
- Database (SQLite for development, PostgreSQL for production)

## Security

- Never commit API keys or sensitive data
- Use environment variables for configuration
- Enable sandbox mode for testing
- Implement proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.