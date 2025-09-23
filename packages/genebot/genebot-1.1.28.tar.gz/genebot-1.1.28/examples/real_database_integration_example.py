#!/usr/bin/env python3
"""
Real Database Integration Example
================================

This example demonstrates how the CLI now uses real database integration
instead of mock data for all trading operations.

Features demonstrated:
- Real trade data retrieval from database
- Actual position tracking and PnL calculations
- Live monitoring with real-time data
- Report generation from actual trading data
- Order closure via exchange APIs (with fallback)
"""

import asyncio
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genebot.cli.utils.data_manager import RealDataManager
from src.database.connection import DatabaseManager
from src.models.database_models import (
    TradeModel, OrderModel, PositionModel, TradingSignalModel,
    StrategyPerformanceModel, RiskEventModel
)


async def create_sample_trading_data(db_manager: DatabaseManager):
    """Create realistic sample trading data for demonstration"""
    print("Creating sample trading data...")
    
    with db_manager.get_session() as session:
        # Create sample orders
        orders = [
            OrderModel(
                id="order_001",
                symbol="BTC/USDT",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                order_type="MARKET",
                status="filled",
                timestamp=datetime.utcnow() - timedelta(hours=2),
                exchange="binance",
                filled_amount=Decimal('0.1'),
                average_fill_price=Decimal('45000.00'),
                fees=Decimal('4.50')
            ),
            OrderModel(
                id="order_002",
                symbol="BTC/USDT",
                side="SELL",
                amount=Decimal('0.1'),
                price=Decimal('46500.00'),
                order_type="MARKET",
                status="filled",
                timestamp=datetime.utcnow() - timedelta(hours=1),
                exchange="binance",
                filled_amount=Decimal('0.1'),
                average_fill_price=Decimal('46500.00'),
                fees=Decimal('4.65')
            ),
            OrderModel(
                id="order_003",
                symbol="ETH/USDT",
                side="BUY",
                amount=Decimal('2.0'),
                price=Decimal('3000.00'),
                order_type="LIMIT",
                status="open",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                exchange="binance",
                filled_amount=Decimal('0'),
                fees=Decimal('0')
            )
        ]
        
        # Create corresponding trades
        trades = [
            TradeModel(
                order_id="order_001",
                symbol="BTC/USDT",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                fees=Decimal('4.50'),
                timestamp=datetime.utcnow() - timedelta(hours=2),
                exchange="binance",
                trade_id="trade_001"
            ),
            TradeModel(
                order_id="order_002",
                symbol="BTC/USDT",
                side="SELL",
                amount=Decimal('0.1'),
                price=Decimal('46500.00'),
                fees=Decimal('4.65'),
                timestamp=datetime.utcnow() - timedelta(hours=1),
                exchange="binance",
                trade_id="trade_002"
            )
        ]
        
        # Create positions
        positions = [
            PositionModel(
                symbol="BTC/USDT",
                size=Decimal('0.1'),
                entry_price=Decimal('45000.00'),
                current_price=Decimal('46500.00'),
                side="BUY",
                exchange="binance",
                opened_at=datetime.utcnow() - timedelta(hours=2),
                closed_at=datetime.utcnow() - timedelta(hours=1),
                is_active="false"
            ),
            PositionModel(
                symbol="ETH/USDT",
                size=Decimal('5.0'),
                entry_price=Decimal('2950.00'),
                current_price=Decimal('3050.00'),
                side="BUY",
                exchange="binance",
                opened_at=datetime.utcnow() - timedelta(hours=4),
                is_active="true"
            )
        ]
        
        # Create trading signals
        signals = [
            TradingSignalModel(
                symbol="BTC/USDT",
                action="BUY",
                confidence=Decimal('0.85'),
                timestamp=datetime.utcnow() - timedelta(hours=3),
                strategy_name="RSI_Strategy",
                price=Decimal('44800.00')
            ),
            TradingSignalModel(
                symbol="BTC/USDT",
                action="SELL",
                confidence=Decimal('0.78'),
                timestamp=datetime.utcnow() - timedelta(hours=1, minutes=30),
                strategy_name="RSI_Strategy",
                price=Decimal('46200.00')
            ),
            TradingSignalModel(
                symbol="ETH/USDT",
                action="BUY",
                confidence=Decimal('0.92'),
                timestamp=datetime.utcnow() - timedelta(minutes=45),
                strategy_name="MACD_Strategy",
                price=Decimal('3020.00')
            )
        ]
        
        # Create strategy performance data
        strategy_performance = [
            StrategyPerformanceModel(
                strategy_name="RSI_Strategy",
                symbol="BTC/USDT",
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow(),
                total_trades=15,
                winning_trades=9,
                losing_trades=6,
                total_pnl=Decimal('1250.75'),
                max_drawdown=Decimal('180.50'),
                sharpe_ratio=Decimal('1.45'),
                win_rate=Decimal('0.60'),
                avg_win=Decimal('195.30'),
                avg_loss=Decimal('85.20')
            ),
            StrategyPerformanceModel(
                strategy_name="MACD_Strategy",
                symbol="ETH/USDT",
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow(),
                total_trades=8,
                winning_trades=6,
                losing_trades=2,
                total_pnl=Decimal('890.25'),
                max_drawdown=Decimal('120.00'),
                sharpe_ratio=Decimal('1.78'),
                win_rate=Decimal('0.75'),
                avg_win=Decimal('165.80'),
                avg_loss=Decimal('60.00')
            )
        ]
        
        # Create risk events
        risk_events = [
            RiskEventModel(
                event_type="POSITION_LIMIT",
                symbol="BTC/USDT",
                description="Position size exceeded 10% of portfolio",
                severity="MEDIUM",
                triggered_value=Decimal('0.12'),
                threshold_value=Decimal('0.10'),
                action_taken="Position size reduced",
                timestamp=datetime.utcnow() - timedelta(hours=6)
            ),
            RiskEventModel(
                event_type="STOP_LOSS",
                symbol="ETH/USDT",
                description="Stop loss triggered for position",
                severity="HIGH",
                triggered_value=Decimal('2850.00'),
                threshold_value=Decimal('2900.00'),
                action_taken="Position closed",
                timestamp=datetime.utcnow() - timedelta(hours=3)
            )
        ]
        
        # Add all data to session
        session.add_all(orders + trades + positions + signals + strategy_performance + risk_events)
        session.commit()
        
        print(f"Created {len(orders)} orders, {len(trades)} trades, {len(positions)} positions")
        print(f"Created {len(signals)} signals, {len(strategy_performance)} strategy records")
        print(f"Created {len(risk_events)} risk events")


async def demonstrate_real_data_retrieval():
    """Demonstrate real data retrieval capabilities"""
    print("\n" + "="*60)
    print("REAL DATA RETRIEVAL DEMONSTRATION")
    print("="*60)
    
    # Create temporary database for demonstration
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_url = f"sqlite:///{f.name}"
    
    try:
        # Initialize database and create sample data
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        await create_sample_trading_data(db_manager)
        
        # Create data manager with real database
        with RealDataManager(database_url=db_url) as data_manager:
            
            # 1. Demonstrate real trade retrieval
            print("\n1. Recent Trades (Real Database Data):")
            print("-" * 40)
            trades = data_manager.get_recent_trades(limit=5)
            for trade in trades:
                pnl_str = f"P&L: ${trade.pnl:.2f}" if trade.pnl else "P&L: N/A"
                print(f"  {trade.timestamp.strftime('%H:%M:%S')} - {trade.symbol}: "
                      f"{trade.side} {trade.quantity} at ${trade.price:.2f} ({pnl_str})")
            
            # 2. Demonstrate active positions
            print("\n2. Active Positions (Real Database Data):")
            print("-" * 40)
            positions = data_manager.get_active_positions()
            for pos in positions:
                pnl_str = f"+${pos.pnl:.2f}" if pos.pnl >= 0 else f"-${abs(pos.pnl):.2f}"
                print(f"  {pos.symbol}: {pos.side} {pos.size} @ ${pos.entry_price:.2f} "
                      f"(Current: ${pos.current_price:.2f}, P&L: {pnl_str})")
            
            # 3. Demonstrate bot status
            print("\n3. Bot Status (Real Database Data):")
            print("-" * 40)
            status = data_manager.get_bot_status_info()
            print(f"  Active Positions: {status.active_positions}")
            print(f"  Trades Today: {status.trades_today}")
            print(f"  P&L Today: ${status.total_pnl_today:.2f}")
            print(f"  Active Strategies: {', '.join(status.active_strategies)}")
            print(f"  Error Count: {status.error_count}")
            
            # 4. Demonstrate trading summary
            print("\n4. Trading Summary (Real Performance Calculations):")
            print("-" * 40)
            summary = data_manager.get_trading_summary(days=7)
            print(f"  Total Trades: {summary.total_trades}")
            print(f"  Win Rate: {summary.win_rate:.1f}%")
            print(f"  Total P&L: ${summary.total_pnl:.2f}")
            print(f"  Average Win: ${summary.avg_win:.2f}")
            print(f"  Average Loss: ${summary.avg_loss:.2f}")
            print(f"  Max Drawdown: ${summary.max_drawdown:.2f}")
            if summary.sharpe_ratio:
                print(f"  Sharpe Ratio: {summary.sharpe_ratio:.2f}")
            
            # 5. Demonstrate recent activity
            print("\n5. Recent Activity (Real-time Data):")
            print("-" * 40)
            activities = data_manager.get_recent_activity(limit=5)
            for activity in activities:
                print(f"  {activity}")
            
            # 6. Demonstrate report generation
            print("\n6. Report Generation (Real Data):")
            print("-" * 40)
            report = data_manager.generate_report_data("summary", days=7)
            print(f"  Report Period: {report['period']}")
            print(f"  Total Trades: {report['total_trades']}")
            print(f"  Win Rate: {report['win_rate']:.1f}%")
            print(f"  Total P&L: ${report['total_pnl']:.2f}")
            
    finally:
        # Cleanup
        import os
        try:
            os.unlink(f.name)
        except:
            pass


async def demonstrate_order_closure():
    """Demonstrate real order closure functionality"""
    print("\n" + "="*60)
    print("ORDER CLOSURE DEMONSTRATION")
    print("="*60)
    
    # Create temporary database for demonstration
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_url = f"sqlite:///{f.name}"
    
    try:
        # Initialize database
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # Create data manager
        with RealDataManager(database_url=db_url) as data_manager:
            
            # Add some open orders
            with data_manager.db_manager.get_session() as session:
                open_orders = [
                    OrderModel(
                        id="open_order_1",
                        symbol="BTC/USDT",
                        side="BUY",
                        amount=Decimal('0.05'),
                        price=Decimal('44000.00'),
                        order_type="LIMIT",
                        status="open",
                        timestamp=datetime.utcnow(),
                        exchange="binance"
                    ),
                    OrderModel(
                        id="open_order_2",
                        symbol="ETH/USDT",
                        side="SELL",
                        amount=Decimal('1.0'),
                        price=Decimal('3100.00'),
                        order_type="LIMIT",
                        status="open",
                        timestamp=datetime.utcnow(),
                        exchange="coinbase"
                    )
                ]
                session.add_all(open_orders)
                session.commit()
            
            print("\n1. Open Orders Before Closure:")
            print("-" * 40)
            with data_manager.db_manager.get_session() as session:
                orders = session.query(OrderModel).filter_by(status="open").all()
                for order in orders:
                    print(f"  {order.id}: {order.side} {order.amount} {order.symbol} "
                          f"at ${order.price:.2f} on {order.exchange}")
            
            # Demonstrate order closure
            print("\n2. Closing All Orders:")
            print("-" * 40)
            closed, failed = data_manager.close_all_orders()
            print(f"  Closed: {closed} orders")
            print(f"  Failed: {failed} orders")
            
            print("\n3. Orders After Closure:")
            print("-" * 40)
            with data_manager.db_manager.get_session() as session:
                orders = session.query(OrderModel).all()
                for order in orders:
                    print(f"  {order.id}: {order.status} - {order.side} {order.amount} "
                          f"{order.symbol} at ${order.price:.2f}")
            
            # Demonstrate filtered closure
            print("\n4. Demonstrating Filtered Closure:")
            print("-" * 40)
            
            # Add more orders
            with data_manager.db_manager.get_session() as session:
                filtered_orders = [
                    OrderModel(
                        id="binance_order_1",
                        symbol="BTC/USDT",
                        side="BUY",
                        amount=Decimal('0.1'),
                        price=Decimal('43000.00'),
                        order_type="LIMIT",
                        status="open",
                        timestamp=datetime.utcnow(),
                        exchange="binance"
                    ),
                    OrderModel(
                        id="kraken_order_1",
                        symbol="BTC/USD",
                        side="SELL",
                        amount=Decimal('0.1'),
                        price=Decimal('47000.00'),
                        order_type="LIMIT",
                        status="open",
                        timestamp=datetime.utcnow(),
                        exchange="kraken"
                    )
                ]
                session.add_all(filtered_orders)
                session.commit()
            
            # Close only binance orders
            closed, failed = data_manager.close_all_orders(account_filter="binance")
            print(f"  Closed Binance orders: {closed}")
            print(f"  Failed: {failed}")
            
            # Show remaining orders
            with data_manager.db_manager.get_session() as session:
                remaining = session.query(OrderModel).filter_by(status="open").all()
                print(f"  Remaining open orders: {len(remaining)}")
                for order in remaining:
                    print(f"    {order.id}: {order.exchange}")
    
    finally:
        # Cleanup
        import os
        try:
            os.unlink(f.name)
        except:
            pass


async def demonstrate_live_monitoring():
    """Demonstrate live monitoring capabilities"""
    print("\n" + "="*60)
    print("LIVE MONITORING DEMONSTRATION")
    print("="*60)
    
    # Create temporary logs directory
    with tempfile.TemporaryDirectory() as temp_dir:
        logs_path = Path(temp_dir)
        
        # Create sample log files
        main_log = logs_path / "trading_bot.log"
        main_log.write_text("""
2024-01-01 10:00:01 - INFO - Trading bot started successfully
2024-01-01 10:00:05 - INFO - Connected to Binance exchange
2024-01-01 10:00:10 - INFO - Strategy RSI_Strategy initialized
2024-01-01 10:01:00 - INFO - BUY signal generated for BTC/USDT at 45000.00
2024-01-01 10:01:05 - INFO - Order placed: BUY 0.1 BTC/USDT at 45000.00
2024-01-01 10:02:30 - INFO - Order filled: BUY 0.1 BTC/USDT at 45000.00
2024-01-01 11:15:20 - INFO - SELL signal generated for BTC/USDT at 46500.00
2024-01-01 11:15:25 - INFO - Order placed: SELL 0.1 BTC/USDT at 46500.00
2024-01-01 11:15:30 - INFO - Order filled: SELL 0.1 BTC/USDT at 46500.00
        """.strip())
        
        # Create error log
        error_log_dir = logs_path / "errors"
        error_log_dir.mkdir()
        error_log = error_log_dir / "error.log"
        error_log.write_text("""
2024-01-01 10:30:00 - ERROR - Connection timeout to Binance API
2024-01-01 10:30:30 - WARNING - Retrying connection to Binance
2024-01-01 10:31:00 - INFO - Connection restored to Binance
        """.strip())
        
        # Create data manager with logs
        with RealDataManager(logs_path=logs_path) as data_manager:
            
            print("\n1. Live Log Data:")
            print("-" * 40)
            log_entries = data_manager.get_live_log_data(lines=8)
            for entry in log_entries:
                print(f"  {entry}")
            
            print("\n2. System Health Metrics:")
            print("-" * 40)
            metrics = data_manager.get_system_health_metrics()
            print(f"  Bot Running: {metrics.get('bot_running', 'Unknown')}")
            print(f"  Database Available: {metrics.get('database_available', 'Unknown')}")
            
            if 'system_cpu_percent' in metrics:
                print(f"  System CPU: {metrics['system_cpu_percent']:.1f}%")
                print(f"  System Memory: {metrics['system_memory_percent']:.1f}%")
                print(f"  Disk Free: {metrics['disk_free_gb']:.1f} GB")
            
            if 'bot_memory_mb' in metrics and metrics['bot_memory_mb']:
                print(f"  Bot Memory: {metrics['bot_memory_mb']:.1f} MB")
                print(f"  Bot CPU: {metrics['bot_cpu_percent']:.1f}%")


async def main():
    """Main demonstration function"""
    print("GeneBot CLI Real Database Integration Example")
    print("=" * 60)
    print("This example demonstrates how the CLI now uses real database")
    print("integration instead of mock data for all operations.")
    print()
    
    try:
        # Run all demonstrations
        await demonstrate_real_data_retrieval()
        await demonstrate_order_closure()
        await demonstrate_live_monitoring()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("Key improvements implemented:")
        print("✓ Real PnL calculations from position tracking")
        print("✓ Actual database queries for all data")
        print("✓ Live log file monitoring")
        print("✓ Real exchange API integration for order closure")
        print("✓ Comprehensive error handling and fallbacks")
        print("✓ System health monitoring")
        print("✓ Real-time activity tracking")
        print()
        print("The CLI now provides accurate, real-time trading data")
        print("instead of mock implementations!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())