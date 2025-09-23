# Strategy Orchestrator API Reference

## Overview

The Strategy Orchestrator provides a comprehensive REST API for programmatic control and monitoring. The API supports real-time status monitoring, configuration management, performance analytics, and operational control.

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

The API supports multiple authentication methods:

### Bearer Token Authentication

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8080/api/v1/orchestrator/status
```

### API Key Authentication

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     http://localhost:8080/api/v1/orchestrator/status
```

## API Endpoints

### Orchestrator Control

#### GET /orchestrator/status

Get current orchestrator status and health information.

**Response:**
```json
{
  "status": "running",
  "uptime": 3600,
  "strategies_active": 5,
  "strategies_total": 8,
  "last_rebalance": "2024-01-15T10:30:00Z",
  "performance": {
    "total_return": 0.0523,
    "sharpe_ratio": 1.34,
    "max_drawdown": 0.0234
  },
  "health": {
    "overall": "healthy",
    "data_feed": "connected",
    "exchanges": "connected",
    "risk_monitor": "active"
  }
}
```

#### POST /orchestrator/start

Start the orchestrator with specified configuration.

**Request Body:**
```json
{
  "config_path": "config/orchestrator_config.yaml",
  "force": false
}
```

**Response:**
```json
{
  "status": "started",
  "message": "Orchestrator started successfully",
  "strategies_loaded": 5
}
```

#### POST /orchestrator/stop

Stop the orchestrator gracefully.

**Request Body:**
```json
{
  "force": false,
  "timeout": 30
}
```

**Response:**
```json
{
  "status": "stopped",
  "message": "Orchestrator stopped successfully"
}
```

#### POST /orchestrator/restart

Restart the orchestrator with optional configuration reload.

**Request Body:**
```json
{
  "reload_config": true,
  "config_path": "config/new_config.yaml"
}
```

### Strategy Management

#### GET /strategies

List all available strategies and their status.

**Query Parameters:**
- `status`: Filter by status (active, inactive, error)
- `market`: Filter by market (crypto, forex)
- `sort_by`: Sort by field (performance, allocation, name)

**Response:**
```json
{
  "strategies": [
    {
      "name": "ma_short_term",
      "type": "MovingAverageStrategy",
      "status": "active",
      "allocation": 0.15,
      "performance": {
        "total_return": 0.0234,
        "sharpe_ratio": 1.12,
        "win_rate": 0.58
      },
      "last_signal": "2024-01-15T10:25:00Z",
      "positions": 2
    }
  ],
  "total": 5,
  "active": 4,
  "inactive": 1
}
```

#### GET /strategies/{strategy_name}

Get detailed information about a specific strategy.

**Response:**
```json
{
  "name": "ma_short_term",
  "type": "MovingAverageStrategy",
  "status": "active",
  "allocation": 0.15,
  "configuration": {
    "short_period": 10,
    "long_period": 20,
    "signal_threshold": 0.01
  },
  "performance": {
    "total_return": 0.0234,
    "sharpe_ratio": 1.12,
    "max_drawdown": 0.0156,
    "win_rate": 0.58,
    "profit_factor": 1.34,
    "total_trades": 45,
    "winning_trades": 26
  },
  "risk_metrics": {
    "volatility": 0.0234,
    "var_95": 0.0123,
    "beta": 0.87
  },
  "positions": [
    {
      "symbol": "BTC/USD",
      "side": "long",
      "size": 0.1,
      "entry_price": 45000,
      "current_price": 45500,
      "pnl": 50.0
    }
  ]
}
```

#### POST /strategies/{strategy_name}/enable

Enable a specific strategy.

**Response:**
```json
{
  "status": "enabled",
  "message": "Strategy ma_short_term enabled successfully"
}
```

#### POST /strategies/{strategy_name}/disable

Disable a specific strategy.

**Response:**
```json
{
  "status": "disabled",
  "message": "Strategy ma_short_term disabled successfully"
}
```

### Allocation Management

#### GET /allocations

Get current allocation across all strategies.

**Response:**
```json
{
  "allocations": {
    "ma_short_term": 0.15,
    "rsi_strategy": 0.12,
    "arbitrage_strategy": 0.18,
    "momentum_strategy": 0.10
  },
  "total_allocated": 0.55,
  "cash_reserve": 0.45,
  "last_rebalance": "2024-01-15T10:30:00Z",
  "next_rebalance": "2024-01-16T10:30:00Z"
}
```

#### POST /allocations/rebalance

Trigger manual rebalancing of allocations.

**Request Body:**
```json
{
  "force": true,
  "method": "performance_based"
}
```

**Response:**
```json
{
  "status": "rebalanced",
  "changes": {
    "ma_short_term": {
      "old": 0.15,
      "new": 0.18,
      "change": 0.03
    },
    "rsi_strategy": {
      "old": 0.12,
      "new": 0.10,
      "change": -0.02
    }
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

#### PUT /allocations/{strategy_name}

Set allocation for a specific strategy.

**Request Body:**
```json
{
  "allocation": 0.20
}
```

**Response:**
```json
{
  "status": "updated",
  "strategy": "ma_short_term",
  "old_allocation": 0.15,
  "new_allocation": 0.20
}
```

### Performance Analytics

#### GET /performance

Get overall portfolio performance metrics.

**Query Parameters:**
- `period`: Time period (1d, 7d, 30d, 90d, 1y)
- `metrics`: Comma-separated list of metrics

**Response:**
```json
{
  "period": "30d",
  "performance": {
    "total_return": 0.0523,
    "annualized_return": 0.2134,
    "sharpe_ratio": 1.34,
    "sortino_ratio": 1.67,
    "max_drawdown": 0.0234,
    "volatility": 0.0456,
    "win_rate": 0.62,
    "profit_factor": 1.45
  },
  "attribution": {
    "ma_short_term": 0.0123,
    "rsi_strategy": 0.0089,
    "arbitrage_strategy": 0.0234,
    "momentum_strategy": 0.0077
  },
  "benchmark_comparison": {
    "benchmark": "BTC",
    "portfolio_return": 0.0523,
    "benchmark_return": 0.0345,
    "alpha": 0.0178,
    "beta": 0.87
  }
}
```

#### GET /performance/attribution

Get detailed performance attribution analysis.

**Response:**
```json
{
  "attribution": {
    "allocation_effect": 0.0123,
    "selection_effect": 0.0234,
    "interaction_effect": 0.0045,
    "total_return": 0.0402
  },
  "strategy_contributions": {
    "ma_short_term": {
      "contribution": 0.0123,
      "weight": 0.15,
      "return": 0.0820
    },
    "rsi_strategy": {
      "contribution": 0.0089,
      "weight": 0.12,
      "return": 0.0742
    }
  }
}
```

#### GET /performance/history

Get historical performance data.

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `frequency`: Data frequency (daily, weekly, monthly)

**Response:**
```json
{
  "history": [
    {
      "date": "2024-01-01",
      "portfolio_value": 100000,
      "total_return": 0.0000,
      "daily_return": 0.0000
    },
    {
      "date": "2024-01-02",
      "portfolio_value": 100234,
      "total_return": 0.0023,
      "daily_return": 0.0023
    }
  ]
}
```

### Risk Management

#### GET /risk/status

Get current risk status and metrics.

**Response:**
```json
{
  "risk_status": "normal",
  "portfolio_drawdown": 0.0234,
  "max_drawdown_limit": 0.10,
  "position_size": 0.0456,
  "position_size_limit": 0.05,
  "correlation_matrix": {
    "ma_short_term": {
      "rsi_strategy": 0.34,
      "arbitrage_strategy": 0.12
    }
  },
  "risk_alerts": [],
  "emergency_stop_active": false
}
```

#### POST /risk/emergency-stop

Trigger emergency stop for all strategies.

**Request Body:**
```json
{
  "reason": "Manual intervention",
  "close_positions": true
}
```

**Response:**
```json
{
  "status": "emergency_stop_activated",
  "timestamp": "2024-01-15T11:30:00Z",
  "positions_closed": 12,
  "strategies_stopped": 5
}
```

#### GET /risk/limits

Get current risk limits and their status.

**Response:**
```json
{
  "limits": {
    "max_portfolio_drawdown": {
      "limit": 0.10,
      "current": 0.0234,
      "status": "ok"
    },
    "max_position_size": {
      "limit": 0.05,
      "current": 0.0456,
      "status": "ok"
    },
    "max_correlation": {
      "limit": 0.80,
      "current": 0.67,
      "status": "ok"
    }
  }
}
```

### Configuration Management

#### GET /config

Get current orchestrator configuration.

**Response:**
```json
{
  "allocation": {
    "method": "performance_based",
    "rebalance_frequency": "daily",
    "min_allocation": 0.01,
    "max_allocation": 0.25
  },
  "risk": {
    "max_portfolio_drawdown": 0.10,
    "position_size_limit": 0.05
  },
  "strategies": [
    {
      "type": "MovingAverageStrategy",
      "name": "ma_short_term",
      "enabled": true,
      "parameters": {
        "short_period": 10,
        "long_period": 20
      }
    }
  ]
}
```

#### PUT /config

Update orchestrator configuration.

**Request Body:**
```json
{
  "allocation": {
    "method": "risk_parity",
    "rebalance_frequency": "weekly"
  }
}
```

**Response:**
```json
{
  "status": "updated",
  "changes": [
    "allocation.method: performance_based -> risk_parity",
    "allocation.rebalance_frequency: daily -> weekly"
  ],
  "restart_required": false
}
```

#### POST /config/validate

Validate configuration without applying changes.

**Request Body:**
```json
{
  "config": {
    "allocation": {
      "method": "invalid_method"
    }
  }
}
```

**Response:**
```json
{
  "valid": false,
  "errors": [
    {
      "field": "allocation.method",
      "message": "Invalid allocation method: invalid_method",
      "valid_values": ["equal_weight", "performance_based", "risk_parity", "custom"]
    }
  ]
}
```

### Monitoring and Alerts

#### GET /alerts

Get current alerts and notifications.

**Query Parameters:**
- `status`: Filter by status (active, resolved, acknowledged)
- `severity`: Filter by severity (low, medium, high, critical)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_001",
      "type": "performance_degradation",
      "severity": "medium",
      "status": "active",
      "message": "Strategy ma_short_term performance below threshold",
      "timestamp": "2024-01-15T11:00:00Z",
      "strategy": "ma_short_term",
      "details": {
        "current_sharpe": 0.45,
        "threshold": 0.50
      }
    }
  ],
  "total": 1,
  "active": 1,
  "resolved": 0
}
```

#### POST /alerts/{alert_id}/acknowledge

Acknowledge an alert.

**Response:**
```json
{
  "status": "acknowledged",
  "alert_id": "alert_001",
  "acknowledged_by": "api_user",
  "timestamp": "2024-01-15T11:15:00Z"
}
```

#### GET /metrics

Get real-time metrics for monitoring dashboards.

**Response:**
```json
{
  "timestamp": "2024-01-15T11:30:00Z",
  "metrics": {
    "portfolio_value": 105234.56,
    "total_return": 0.0523,
    "daily_pnl": 234.56,
    "active_strategies": 5,
    "active_positions": 12,
    "risk_utilization": 0.67,
    "correlation_avg": 0.34
  }
}
```

## WebSocket API

For real-time updates, the orchestrator provides WebSocket endpoints:

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/v1/orchestrator');
```

### Subscription

```javascript
// Subscribe to performance updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'performance',
  frequency: '1m'
}));

// Subscribe to allocation changes
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'allocations'
}));

// Subscribe to alerts
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'alerts'
}));
```

### Message Format

```javascript
{
  "channel": "performance",
  "timestamp": "2024-01-15T11:30:00Z",
  "data": {
    "total_return": 0.0523,
    "daily_pnl": 234.56,
    "sharpe_ratio": 1.34
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_STRATEGY",
    "message": "Strategy 'invalid_strategy' not found",
    "details": {
      "available_strategies": ["ma_short_term", "rsi_strategy"]
    }
  },
  "timestamp": "2024-01-15T11:30:00Z",
  "request_id": "req_12345"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Common Error Codes

- `INVALID_STRATEGY`: Strategy not found or invalid
- `ALLOCATION_ERROR`: Allocation validation failed
- `RISK_LIMIT_EXCEEDED`: Risk limits would be exceeded
- `CONFIG_INVALID`: Configuration validation failed
- `ORCHESTRATOR_NOT_RUNNING`: Orchestrator is not active
- `INSUFFICIENT_FUNDS`: Insufficient capital for operation
- `MARKET_CLOSED`: Market is closed for trading

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default Limit**: 100 requests per minute per API key
- **Burst Limit**: 20 requests per 10 seconds
- **Headers**: Rate limit information in response headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## SDK Examples

### Python SDK

```python
from orchestrator_client import OrchestratorClient

client = OrchestratorClient(
    base_url="http://localhost:8080/api/v1",
    api_key="your_api_key"
)

# Get status
status = client.get_status()
print(f"Orchestrator status: {status['status']}")

# Get performance
performance = client.get_performance(period="30d")
print(f"Total return: {performance['performance']['total_return']}")

# Rebalance allocations
result = client.rebalance_allocations(force=True)
print(f"Rebalance result: {result['status']}")
```

### JavaScript SDK

```javascript
import { OrchestratorClient } from 'orchestrator-client';

const client = new OrchestratorClient({
  baseURL: 'http://localhost:8080/api/v1',
  apiKey: 'your_api_key'
});

// Get status
const status = await client.getStatus();
console.log(`Orchestrator status: ${status.status}`);

// Subscribe to real-time updates
client.subscribe('performance', (data) => {
  console.log('Performance update:', data);
});
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
```
http://localhost:8080/api/v1/docs/openapi.json
```

Interactive API documentation is available at:
```
http://localhost:8080/api/v1/docs
```

## Authentication Setup

### Generate API Token

```bash
# Generate new API token
genebot orchestrator auth generate-token --name "my_app" --permissions "read,write"

# List existing tokens
genebot orchestrator auth list-tokens

# Revoke token
genebot orchestrator auth revoke-token --token-id "token_123"
```

### Configure Authentication

```yaml
api:
  authentication:
    enabled: true
    method: "bearer_token"
    tokens:
      - name: "dashboard"
        token: "token_abc123"
        permissions: ["read"]
      - name: "trading_app"
        token: "token_def456"
        permissions: ["read", "write", "admin"]
```

For more examples and detailed integration guides, see the SDK documentation and example applications in the `examples/api/` directory.