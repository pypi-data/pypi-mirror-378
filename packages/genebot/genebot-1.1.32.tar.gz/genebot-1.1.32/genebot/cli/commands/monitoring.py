"""
Monitoring and Reporting Commands
================================

Commands for monitoring trading activity and generating reports.
"""

from argparse import Namespace
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timedelta

from ..result import CommandResult
from .base import BaseCommand
from ..utils.data_manager import RealDataManager, TradeInfo, TradingSummary
from ..utils.process_manager import ProcessManager
from ..utils.account_validator import RealAccountValidator
from ..utils.integration_manager import IntegrationManager
try:
    from src.strategies.strategy_config import StrategyConfigManager
except ImportError:
    class StrategyConfigManager:
        def __init__(self, *args, **kwargs):
            pass

try:
    from src.exchanges.ccxt_adapter import CCXTAdapter
except ImportError:
    class CCXTAdapter:
        def __init__(self, *args, **kwargs):
            pass
from genebot.config.manager import ConfigManager
import psutil
import asyncio
import yaml


class MonitorCommand(BaseCommand):
    """Real-time trading monitor"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute monitor command"""
        refresh_interval = getattr(args, 'refresh', 5)
        account_filter = getattr(args, 'account', None)
        
        self.logger.section("Real-Time Trading Monitor")
        self.logger.info(f"Refresh interval: {refresh_interval} seconds")
        
        if account_filter:
            self.logger.info(f"Monitoring account: {account_filter}")
        
        try:
            with RealDataManager() as data_manager:
                self._run_monitor_loop(refresh_interval, account_filter, data_manager)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
            return CommandResult.error(
                f"Monitoring failed: {str(e)}",
                suggestions=[
                    "Check database connectivity",
                    "Verify log file permissions",
                    "Ensure trading bot is running"
                ]
            )
        
        return CommandResult.success("Monitoring session completed")
    
    def _run_monitor_loop(self, refresh_interval: int, account_filter: str, data_manager: RealDataManager) -> None:
        """Run the monitoring loop"""
        iteration = 0
        
        while True:
            iteration += 1
            
            # Clear screen (simple approach)
            print("\033[2J\033[H", end="")
            
            self.logger.banner(f"GeneBot Live Monitor - Update #{iteration}")
            
            # Get real live data
            self._display_live_status(data_manager)
            self._display_active_positions(data_manager, account_filter)
            self._display_recent_activity(data_manager)
            
            self.logger.info(f"\nNext update in {refresh_interval} seconds... (Ctrl+C to stop)")
            
            time.sleep(refresh_interval)
    
    def _display_live_status(self, data_manager: RealDataManager) -> None:
        """Display live bot status with real process monitoring"""
        self.logger.subsection("Bot Status")
        
        try:
            # Get real process status
            process_manager = ProcessManager(self.context.workspace_path)
            bot_status = process_manager.get_bot_status()
            
            # Get trading data status
            trading_status = data_manager.get_bot_status_info()
            
            # Determine overall status
            if bot_status.running:
                if bot_status.process_info and bot_status.process_info.status == 'running':
                    status_icon = "🟢 Running"
                elif bot_status.error_message:
                    status_icon = "🟡 Running (Issues)"
                else:
                    status_icon = "🟢 Running"
            else:
                status_icon = "🔴 Stopped"
            
            # Format PnL with proper sign
            pnl_str = f"+${trading_status.total_pnl_today:.2f}" if trading_status.total_pnl_today >= 0 else f"-${abs(trading_status.total_pnl_today):.2f}"
            
            status_items = [
                ("Bot Status", status_icon),
                ("Process ID", str(bot_status.pid) if bot_status.pid else "N/A"),
                ("Uptime", self._format_uptime(bot_status.uptime) if bot_status.uptime else "N/A"),
                ("Memory Usage", f"{bot_status.memory_usage:.1f} MB" if bot_status.memory_usage else "N/A"),
                ("CPU Usage", f"{bot_status.cpu_usage:.1f}%" if bot_status.cpu_usage else "N/A"),
                ("Active Strategies", str(len(trading_status.active_strategies))),
                ("Open Positions", str(trading_status.active_positions)),
                ("Trades Today", str(trading_status.trades_today)),
                ("P&L Today", pnl_str),
                ("Errors Today", str(trading_status.error_count))
            ]
            
            if trading_status.last_activity:
                last_activity = trading_status.last_activity.strftime("%H:%M:%S")
                status_items.append(("Last Activity", last_activity))
            
            if bot_status.error_message:
                status_items.append(("Error", bot_status.error_message))
            
            for label, value in status_items:
                self.logger.list_item(f"{label}: {value}", "info")
                
            # Display strategy information if available
            if trading_status.active_strategies:
                self._display_strategy_info(trading_status.active_strategies)
                
        except Exception as e:
            self.logger.error(f"Error displaying status: {e}")
            self.logger.list_item("Status: ❌ Error retrieving data", "error")
    
    def _format_uptime(self, uptime) -> str:
        """Format uptime as human-readable string"""
        if not uptime:
            return "N/A"
        
        total_seconds = int(uptime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _display_strategy_info(self, active_strategies: List[str]) -> None:
        """Display real strategy information from configuration"""
        self.logger.subsection("Active Strategies")
        
        try:
            # Load strategy configurations
            strategy_manager = StrategyConfigManager()
            config_manager = ConfigManager()
            
            # Get strategy configurations from the trading bot config
            bot_config = config_manager.load_config()
            if bot_config and 'strategies' in bot_config:
                for strategy_name in active_strategies:
                    strategy_config = bot_config['strategies'].get(strategy_name)
                    if strategy_config:
                        enabled_status = "✅" if strategy_config.get('enabled', True) else "❌"
                        confidence = strategy_config.get('parameters', {}).get('min_confidence', 'N/A')
                        
                        self.logger.list_item(
                            f"{enabled_status} {strategy_name} (confidence: {confidence})", 
                            "info"
                        )
                    else:
                        self.logger.list_item(f"⚠️ {strategy_name} (config not found)", "warning")
            else:
                for strategy_name in active_strategies:
                    self.logger.list_item(f"📊 {strategy_name}", "info")
                    
        except Exception as e:
            self.logger.warning(f"Could not load strategy details: {e}")
            for strategy_name in active_strategies:
                self.logger.list_item(f"📊 {strategy_name}", "info")
    
    def _display_active_positions(self, data_manager: RealDataManager, account_filter: str) -> None:
        """Display active trading positions"""
        self.logger.subsection("Active Positions")
        
        try:
            # Get real position data
            positions = data_manager.get_active_positions(account_filter)
            
            if positions:
                self.logger.table_header(['Symbol', 'Side', 'Size', 'Entry Price', 'Current Price', 'P&L', 'Duration'])
                for pos in positions:
                    # Format PnL with proper sign
                    pnl_str = f"+${pos.pnl:.2f}" if pos.pnl >= 0 else f"-${abs(pos.pnl):.2f}"
                    
                    # Format duration
                    duration_str = f"{pos.duration.days}d {pos.duration.seconds//3600}h" if pos.duration.days > 0 else f"{pos.duration.seconds//3600}h {(pos.duration.seconds//60)%60}m"
                    
                    self.logger.table_row([
                        pos.symbol,
                        pos.side,
                        f"{pos.size:.4f}",
                        f"${pos.entry_price:.4f}",
                        f"${pos.current_price:.4f}",
                        pnl_str,
                        duration_str
                    ])
            else:
                self.logger.info("No active positions")
                
        except Exception as e:
            self.logger.error(f"Error displaying positions: {e}")
            self.logger.info("Error retrieving position data")
    
    def _display_recent_activity(self, data_manager: RealDataManager) -> None:
        """Display recent trading activity"""
        self.logger.subsection("Recent Activity")
        
        try:
            # Get real activity data
            activities = data_manager.get_recent_activity(limit=8)
            
            if activities:
                for activity in activities:
                    self.logger.list_item(activity, "info")
            else:
                self.logger.info("No recent activity")
                
        except Exception as e:
            self.logger.error(f"Error displaying activity: {e}")
            self.logger.info("Error retrieving activity data")


class TradesCommand(BaseCommand):
    """Show recent trades and P&L"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute trades command"""
        limit = getattr(args, 'limit', 20)
        account_filter = getattr(args, 'account', None)
        days = getattr(args, 'days', None)
        
        self.logger.section("Trading History")
        
        if account_filter:
            self.logger.info(f"Account filter: {account_filter}")
        if days:
            self.logger.info(f"Time filter: Last {days} days")
        
        try:
            with RealDataManager() as data_manager:
                # Load trades from actual database
                trades = data_manager.get_recent_trades(limit, account_filter, days)
                
                if not trades:
                    return CommandResult.warning(
                        "No trades found matching the specified criteria",
                        suggestions=[
                            "Check if the bot has been running and making trades",
                            "Verify account filter is correct",
                            "Try expanding the time range",
                            "Check database connectivity"
                        ]
                    )
                
                self._display_trades(trades)
                self._display_summary(trades, data_manager, days or 30)
                
                return CommandResult.success(
                    f"Displayed {len(trades)} trade(s)",
                    data={'trades_count': len(trades)}
                )
                
        except Exception as e:
            self.logger.error(f"Error retrieving trades: {str(e)}")
            return CommandResult.error(
                f"Failed to retrieve trades: {str(e)}",
                suggestions=[
                    "Check database connectivity",
                    "Verify database tables exist",
                    "Check log file permissions"
                ]
            )
    
    def _format_trade_for_display(self, trade) -> Dict[str, str]:
        """Format trade info for display"""
        # Format PnL with proper sign
        pnl_str = "N/A"
        if trade.pnl is not None:
            pnl_str = f"+${trade.pnl:.2f}" if trade.pnl >= 0 else f"-${abs(trade.pnl):.2f}"
        
        # Format price with currency symbol if needed
        if 'USD' in trade.symbol:
            price_str = f"${trade.price:.4f}"
        else:
            price_str = f"{trade.price:.8f}"
        
        return {
            'timestamp': trade.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': trade.symbol,
            'side': trade.side,
            'quantity': f"{trade.quantity:.8f}".rstrip('0').rstrip('.'),
            'price': price_str,
            'pnl': pnl_str,
            'account': trade.account,
            'fees': f"${trade.fees:.4f}" if trade.fees else "N/A"
        }
    
    def _display_trades(self, trades) -> None:
        """Display trades in table format"""
        self.logger.table_header(['Time', 'Symbol', 'Side', 'Quantity', 'Price', 'P&L', 'Fees', 'Account'])
        
        for trade in trades:
            formatted_trade = self._format_trade_for_display(trade)
            self.logger.table_row([
                formatted_trade['timestamp'].split()[1],  # Just time part
                formatted_trade['symbol'],
                formatted_trade['side'],
                formatted_trade['quantity'],
                formatted_trade['price'],
                formatted_trade['pnl'],
                formatted_trade['fees'],
                formatted_trade['account']
            ])
    
    def _display_summary(self, trades, data_manager: RealDataManager, days: int) -> None:
        """Display trading summary"""
        self.logger.subsection("Trading Summary")
        
        try:
            # Get comprehensive trading summary
            summary = data_manager.get_trading_summary(days)
            
            # Format total PnL with proper sign
            total_pnl_str = f"+${summary.total_pnl:.2f}" if summary.total_pnl >= 0 else f"-${abs(summary.total_pnl):.2f}"
            
            summary_items = [
                ("Total Trades", str(summary.total_trades)),
                ("Winning Trades", str(summary.winning_trades)),
                ("Losing Trades", str(summary.losing_trades)),
                ("Win Rate", f"{summary.win_rate:.1f}%"),
                ("Total P&L", total_pnl_str),
                ("Average Win", f"${summary.avg_win:.2f}"),
                ("Average Loss", f"${summary.avg_loss:.2f}"),
                ("Max Drawdown", f"${summary.max_drawdown:.2f}")
            ]
            
            if summary.sharpe_ratio is not None:
                summary_items.append(("Sharpe Ratio", f"{summary.sharpe_ratio:.2f}"))
            
            for label, value in summary_items:
                self.logger.list_item(f"{label}: {value}", "info")
                
        except Exception as e:
            self.logger.error(f"Error calculating summary: {e}")
            # Fallback to basic summary from displayed trades
            total_trades = len(trades)
            self.logger.list_item(f"Displayed Trades: {total_trades}", "info")


class ReportCommand(BaseCommand):
    """Generate comprehensive trading reports with real data and analytics"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute report command"""
        report_type = args.type
        output_file = getattr(args, 'output', None)
        output_format = getattr(args, 'format', 'text')
        days = getattr(args, 'days', 30)
        include_charts = getattr(args, 'charts', False)
        
        self.logger.section(f"Generating {report_type.title()} Report")
        self.logger.info(f"Format: {output_format}")
        self.logger.info(f"Period: Last {days} days")
        
        if output_file:
            self.logger.info(f"Output file: {output_file}")
        if include_charts:
            self.logger.info("Including performance charts")
        
        try:
            with RealDataManager() as data_manager:
                # Generate comprehensive report from real database
                if report_type == 'performance':
                    report_data = self._generate_performance_report(data_manager, days)
                elif report_type == 'compliance':
                    report_data = self._generate_compliance_report(data_manager, days)
                elif report_type == 'strategy':
                    report_data = self._generate_strategy_report(data_manager, days)
                elif report_type == 'pnl':
                    report_data = self._generate_pnl_analysis_report(data_manager, days)
                else:
                    report_data = data_manager.generate_report_data(report_type, days)
                
                if 'error' in report_data:
                    return CommandResult.error(
                        report_data['error'],
                        suggestions=[
                            "Check database connectivity",
                            "Verify trading data exists",
                            "Try a different time period"
                        ]
                    )
                
                # Generate charts if requested
                chart_files = []
                if include_charts and output_format in ['html', 'pdf']:
                    chart_files = self._generate_performance_charts(report_data, days)
                    report_data['charts'] = chart_files
                
                # Output report in requested format
                if output_format == 'json':
                    self._output_json_report(report_data, output_file)
                elif output_format == 'csv':
                    self._output_csv_report(report_data, output_file)
                elif output_format == 'html':
                    self._output_html_report(report_data, report_type, output_file)
                elif output_format == 'pdf':
                    self._output_pdf_report(report_data, report_type, output_file)
                else:
                    self._output_text_report(report_data, report_type, output_file)
                
                return CommandResult.success(
                    f"{report_type.title()} report generated successfully",
                    data={'report_type': report_type, 'period_days': days, 'format': output_format}
                )
                
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return CommandResult.error(
                f"Failed to generate report: {str(e)}",
                suggestions=[
                    "Check database connectivity",
                    "Verify sufficient trading data exists",
                    "Check file permissions for output"
                ]
            )
    
    def _serialize_report_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize report data for JSON output (handle Decimal types)"""
        serialized = {}
        for key, value in data.items():
            if isinstance(value, Decimal):
                serialized[key] = float(value)
            elif isinstance(value, dict):
                serialized[key] = self._serialize_report_data(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_report_data(item) if isinstance(item, dict) 
                    else float(item) if isinstance(item, Decimal) 
                    else item 
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    def _output_text_report(self, data: Dict[str, Any], report_type: str, output_file: str) -> None:
        """Output report in text format"""
        lines = [
            f"GeneBot Trading Report - {report_type.title()}",
            "=" * 50,
            f"Generated: {data.get('generated_at', 'Unknown')}",
            f"Period: {data.get('period', 'Unknown')}",
            ""
        ]
        
        # Add summary section if available
        if 'summary' in data:
            summary = data['summary']
            lines.extend([
                "Performance Summary:",
                f"  Total Trades: {summary.get('total_trades', 0)}",
                f"  Winning Trades: {summary.get('winning_trades', 0)}",
                f"  Losing Trades: {summary.get('losing_trades', 0)}",
                f"  Win Rate: {summary.get('win_rate', 0):.1f}%",
                f"  Total P&L: ${summary.get('total_pnl', 0):.2f}",
                f"  Max Drawdown: {summary.get('max_drawdown', 0):.1f}%",
                f"  Sharpe Ratio: {summary.get('sharpe_ratio', 0):.2f}" if summary.get('sharpe_ratio') else "  Sharpe Ratio: N/A",
                ""
            ])
        
        # Add other sections
        for key, value in data.items():
            if key in ['generated_at', 'period', 'summary', 'report_type']:
                continue
            
            lines.append(f"{key.replace('_', ' ').title()}:")
            if isinstance(value, dict):
                for k, v in value.items():
                    formatted_value = f"{v:.2f}" if isinstance(v, (int, float)) else str(v)
                    lines.append(f"  {k.replace('_', ' ').title()}: {formatted_value}")
            elif isinstance(value, list):
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"  {value}")
            lines.append("")
        
        report_text = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            self.logger.success(f"Report saved to {output_file}")
        else:
            print(report_text)
    
    def _generate_performance_report(self, data_manager: RealDataManager, days: int) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        try:
            # Get basic trading summary
            summary = data_manager.get_trading_summary(days)
            
            # Get detailed trade analysis
            trades = data_manager.get_recent_trades(limit=1000, days=days)
            
            # Calculate advanced metrics
            performance_metrics = self._calculate_advanced_metrics(trades, summary)
            
            # Get risk metrics
            risk_metrics = self._calculate_risk_metrics(trades, days)
            
            # Get strategy breakdown
            strategy_performance = data_manager._get_strategy_performance()
            
            return {
                'report_type': 'performance',
                'generated_at': datetime.utcnow().isoformat(),
                'period': f'Last {days} days',
                'summary': {
                    'total_trades': summary.total_trades,
                    'winning_trades': summary.winning_trades,
                    'losing_trades': summary.losing_trades,
                    'win_rate': summary.win_rate,
                    'total_pnl': float(summary.total_pnl),
                    'max_drawdown': float(summary.max_drawdown),
                    'sharpe_ratio': summary.sharpe_ratio,
                    'avg_win': float(summary.avg_win),
                    'avg_loss': float(summary.avg_loss)
                },
                'advanced_metrics': performance_metrics,
                'risk_metrics': risk_metrics,
                'strategy_performance': strategy_performance,
                'trade_distribution': self._analyze_trade_distribution(trades),
                'daily_pnl': data_manager._calculate_daily_pnl(days)
            }
            
        except Exception as e:
            return {'error': f'Failed to generate performance report: {str(e)}'}
    
    def _generate_compliance_report(self, data_manager: RealDataManager, days: int) -> Dict[str, Any]:
        """Generate compliance and audit trail report"""
        try:
            try:
                from src.compliance.reporting_engine import ReportingEngine
                from src.compliance.audit_trail import AuditTrail
            except ImportError:
                class ReportingEngine:
                    def __init__(self, *args, **kwargs):
                        pass
                    
                    def generate_report(self, *args, **kwargs):
                        return {"status": "Compliance reporting not available"}
                
                class AuditTrail:
                    def __init__(self, *args, **kwargs):
                        pass
                    
                    def get_audit_data(self, *args, **kwargs):
                        return []
            
            # Initialize compliance components
            compliance_config = {
                'output_directory': 'reports/compliance',
                'jurisdictions': ['US', 'EU'],
                'formats': ['json', 'csv']
            }
            reporting_engine = ReportingEngine(compliance_config)
            audit_trail = AuditTrail()
            
            # Get compliance events
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            compliance_events = audit_trail.get_compliance_events(start_date, end_date)
            trades = data_manager.get_recent_trades(limit=10000, days=days)
            
            # Generate compliance report
            compliance_report = reporting_engine.generate_compliance_report(
                compliance_events, start_date, end_date
            )
            
            # Generate trade report for regulatory purposes
            trade_report = reporting_engine.generate_trade_report(
                [self._convert_trade_to_order(trade) for trade in trades],
                start_date, end_date
            )
            
            return {
                'report_type': 'compliance',
                'generated_at': datetime.utcnow().isoformat(),
                'period': f'Last {days} days',
                'compliance_summary': compliance_report['data'],
                'trade_report': trade_report['data'],
                'audit_events': len(compliance_events),
                'violations': sum(1 for event in compliance_events if event.status.value == 'violations'),
                'regulatory_files': [
                    compliance_report.get('file_path'),
                    trade_report.get('file_path')
                ]
            }
            
        except Exception as e:
            return {'error': f'Failed to generate compliance report: {str(e)}'}
    
    def _generate_strategy_report(self, data_manager: RealDataManager, days: int) -> Dict[str, Any]:
        """Generate detailed strategy performance report"""
        try:
            strategy_performance = data_manager._get_strategy_performance()
            trades = data_manager.get_recent_trades(limit=10000, days=days)
            
            # Group trades by strategy
            strategy_trades = {}
            for trade in trades:
                strategy = trade.strategy or 'Unknown'
                if strategy not in strategy_trades:
                    strategy_trades[strategy] = []
                strategy_trades[strategy].append(trade)
            
            # Analyze each strategy
            strategy_analysis = {}
            for strategy_name, strategy_trades_list in strategy_trades.items():
                analysis = self._analyze_strategy_performance(strategy_name, strategy_trades_list)
                strategy_analysis[strategy_name] = analysis
            
            return {
                'report_type': 'strategy',
                'generated_at': datetime.utcnow().isoformat(),
                'period': f'Last {days} days',
                'strategy_count': len(strategy_analysis),
                'strategy_performance': strategy_performance,
                'detailed_analysis': strategy_analysis,
                'best_performing': self._find_best_strategy(strategy_analysis),
                'worst_performing': self._find_worst_strategy(strategy_analysis),
                'recommendations': self._generate_strategy_recommendations(strategy_analysis)
            }
            
        except Exception as e:
            return {'error': f'Failed to generate strategy report: {str(e)}'}
    
    def _generate_pnl_analysis_report(self, data_manager: RealDataManager, days: int) -> Dict[str, Any]:
        """Generate detailed P&L analysis report"""
        try:
            trades = data_manager.get_recent_trades(limit=10000, days=days)
            summary = data_manager.get_trading_summary(days)
            
            # Calculate P&L metrics
            pnl_analysis = {
                'total_pnl': float(summary.total_pnl),
                'gross_profit': sum(float(trade.pnl) for trade in trades if trade.pnl and trade.pnl > 0),
                'gross_loss': sum(float(trade.pnl) for trade in trades if trade.pnl and trade.pnl < 0),
                'profit_factor': 0,
                'daily_pnl': data_manager._calculate_daily_pnl(days),
                'pnl_by_symbol': self._calculate_pnl_by_symbol(trades),
                'pnl_by_exchange': self._calculate_pnl_by_exchange(trades),
                'monthly_pnl': self._calculate_monthly_pnl(trades),
                'drawdown_analysis': self._analyze_drawdowns(trades)
            }
            
            # Calculate profit factor
            if pnl_analysis['gross_loss'] != 0:
                pnl_analysis['profit_factor'] = abs(pnl_analysis['gross_profit'] / pnl_analysis['gross_loss'])
            
            return {
                'report_type': 'pnl_analysis',
                'generated_at': datetime.utcnow().isoformat(),
                'period': f'Last {days} days',
                'pnl_analysis': pnl_analysis,
                'risk_adjusted_returns': self._calculate_risk_adjusted_returns(trades),
                'performance_attribution': self._analyze_performance_attribution(trades)
            }
            
        except Exception as e:
            return {'error': f'Failed to generate P&L analysis report: {str(e)}'}
    
    def _calculate_advanced_metrics(self, trades: List[TradeInfo], summary: TradingSummary) -> Dict[str, Any]:
        """Calculate advanced performance metrics"""
        if not trades:
            return {}
        
        # Calculate additional metrics
        trade_pnls = [float(trade.pnl) for trade in trades if trade.pnl is not None]
        
        if not trade_pnls:
            return {}
        
        # Sortino ratio (downside deviation)
        negative_returns = [pnl for pnl in trade_pnls if pnl < 0]
        downside_deviation = (sum(pnl ** 2 for pnl in negative_returns) / len(negative_returns)) ** 0.5 if negative_returns else 0
        sortino_ratio = (sum(trade_pnls) / len(trade_pnls)) / downside_deviation if downside_deviation > 0 else 0
        
        # Calmar ratio (return / max drawdown)
        calmar_ratio = float(summary.total_pnl) / float(summary.max_drawdown) if summary.max_drawdown > 0 else 0
        
        # Recovery factor
        recovery_factor = float(summary.total_pnl) / float(summary.max_drawdown) if summary.max_drawdown > 0 else 0
        
        return {
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'recovery_factor': recovery_factor,
            'profit_factor': float(summary.avg_win) / abs(float(summary.avg_loss)) if summary.avg_loss != 0 else 0,
            'expectancy': sum(trade_pnls) / len(trade_pnls),
            'largest_win': max(trade_pnls),
            'largest_loss': min(trade_pnls),
            'consecutive_wins': self._calculate_consecutive_wins(trade_pnls),
            'consecutive_losses': self._calculate_consecutive_losses(trade_pnls)
        }
    
    def _calculate_risk_metrics(self, trades: List[TradeInfo], days: int) -> Dict[str, Any]:
        """Calculate risk management metrics"""
        if not trades:
            return {}
        
        trade_pnls = [float(trade.pnl) for trade in trades if trade.pnl is not None]
        
        if not trade_pnls:
            return {}
        
        # Value at Risk (VaR) - 95% confidence
        sorted_pnls = sorted(trade_pnls)
        var_95 = sorted_pnls[int(len(sorted_pnls) * 0.05)] if len(sorted_pnls) > 20 else min(trade_pnls)
        
        # Expected Shortfall (Conditional VaR)
        var_index = int(len(sorted_pnls) * 0.05)
        expected_shortfall = sum(sorted_pnls[:var_index]) / var_index if var_index > 0 else var_95
        
        # Maximum consecutive loss period
        max_loss_period = self._calculate_max_loss_period(trades)
        
        return {
            'value_at_risk_95': var_95,
            'expected_shortfall': expected_shortfall,
            'max_loss_period_days': max_loss_period,
            'volatility': (sum((pnl - sum(trade_pnls)/len(trade_pnls))**2 for pnl in trade_pnls) / len(trade_pnls))**0.5,
            'downside_volatility': (sum((pnl - 0)**2 for pnl in trade_pnls if pnl < 0) / len([p for p in trade_pnls if p < 0]))**0.5 if any(p < 0 for p in trade_pnls) else 0
        }
    
    def _analyze_trade_distribution(self, trades: List[TradeInfo]) -> Dict[str, Any]:
        """Analyze trade distribution patterns"""
        if not trades:
            return {}
        
        # Distribution by symbol
        symbol_counts = {}
        for trade in trades:
            symbol_counts[trade.symbol] = symbol_counts.get(trade.symbol, 0) + 1
        
        # Distribution by exchange
        exchange_counts = {}
        for trade in trades:
            exchange_counts[trade.exchange] = exchange_counts.get(trade.exchange, 0) + 1
        
        # Distribution by hour of day
        hour_counts = {}
        for trade in trades:
            hour = trade.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return {
            'by_symbol': symbol_counts,
            'by_exchange': exchange_counts,
            'by_hour': hour_counts,
            'total_symbols': len(symbol_counts),
            'total_exchanges': len(exchange_counts),
            'most_traded_symbol': max(symbol_counts.items(), key=lambda x: x[1])[0] if symbol_counts else None,
            'most_active_hour': max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        }
    
    def _output_json_report(self, data: Dict[str, Any], output_file: str) -> None:
        """Output report in JSON format"""
        # Serialize data to handle Decimal types
        serialized_data = self._serialize_report_data(data)
        json_text = json.dumps(serialized_data, indent=2, default=str)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_text)
            self.logger.success(f"JSON report saved to {output_file}")
        else:
            print(json_text)
    
    def _output_csv_report(self, data: Dict[str, Any], output_file: str) -> None:
        """Output report in CSV format"""
        try:
            import csv
            from io import StringIO
            
            output = StringIO()
            
            # Write summary data
            if 'summary' in data:
                output.write("Summary Metrics\n")
                writer = csv.writer(output)
                writer.writerow(['Metric', 'Value'])
                for key, value in data['summary'].items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                output.write("\n")
            
            # Write trade data if available
            if 'recent_trades' in data:
                output.write("Recent Trades\n")
                trades = data['recent_trades']
                if trades:
                    writer = csv.DictWriter(output, fieldnames=trades[0].keys())
                    writer.writeheader()
                    writer.writerows(trades)
            
            csv_content = output.getvalue()
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(csv_content)
                self.logger.success(f"CSV report saved to {output_file}")
            else:
                print(csv_content)
                
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {e}")
    
    def _output_html_report(self, data: Dict[str, Any], report_type: str, output_file: str) -> None:
        """Output report in HTML format"""
        try:
            html_content = self._generate_html_content(data, report_type)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(html_content)
                self.logger.success(f"HTML report saved to {output_file}")
            else:
                print(html_content)
                
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
    
    def _output_pdf_report(self, data: Dict[str, Any], report_type: str, output_file: str) -> None:
        """Output report in PDF format"""
        try:
            # Generate HTML first, then convert to PDF
            html_content = self._generate_html_content(data, report_type)
            
            # For now, save as HTML with PDF extension
            # In a full implementation, you'd use a library like weasyprint or reportlab
            if output_file:
                pdf_file = output_file.replace('.pdf', '.html') if output_file.endswith('.pdf') else f"{output_file}.html"
                with open(pdf_file, 'w') as f:
                    f.write(html_content)
                self.logger.success(f"HTML report saved to {pdf_file} (PDF conversion requires additional libraries)")
            else:
                self.logger.warning("PDF output to console not supported, displaying HTML instead")
                print(html_content)
                
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")


    def _generate_html_content(self, data: Dict[str, Any], report_type: str) -> str:
        """Generate HTML content for reports"""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GeneBot {report_type.title()} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #007acc; padding-bottom: 20px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .section {{ margin: 30px 0; }}
        .section h3 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .chart-placeholder {{ background-color: #f8f9fa; padding: 40px; text-align: center; border: 2px dashed #dee2e6; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GeneBot Trading Report</h1>
            <h2>{report_type.title()} Analysis</h2>
            <p>Generated: {data.get('generated_at', 'Unknown')}</p>
            <p>Period: {data.get('period', 'Unknown')}</p>
        </div>
        
        {self._generate_summary_section(data)}
        {self._generate_detailed_sections(data, report_type)}
    </div>
</body>
</html>
        """
        return html_template
    
    def _generate_summary_section(self, data: Dict[str, Any]) -> str:
        """Generate summary metrics section for HTML"""
        if 'summary' not in data:
            return ""
        
        summary = data['summary']
        html = '<div class="summary">'
        
        metrics = [
            ('Total Trades', summary.get('total_trades', 0)),
            ('Win Rate', f"{summary.get('win_rate', 0):.1f}%"),
            ('Total P&L', f"${summary.get('total_pnl', 0):.2f}"),
            ('Sharpe Ratio', f"{summary.get('sharpe_ratio', 0):.2f}" if summary.get('sharpe_ratio') else 'N/A'),
            ('Max Drawdown', f"{summary.get('max_drawdown', 0):.2f}%"),
            ('Profit Factor', f"{summary.get('profit_factor', 0):.2f}" if 'profit_factor' in summary else 'N/A')
        ]
        
        for label, value in metrics:
            html += f'''
            <div class="metric-box">
                <div>{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def _generate_detailed_sections(self, data: Dict[str, Any], report_type: str) -> str:
        """Generate detailed sections based on report type"""
        html = ""
        
        if report_type == 'performance' and 'advanced_metrics' in data:
            html += self._generate_advanced_metrics_section(data['advanced_metrics'])
        
        if report_type == 'strategy' and 'detailed_analysis' in data:
            html += self._generate_strategy_analysis_section(data['detailed_analysis'])
        
        if report_type == 'compliance' and 'compliance_summary' in data:
            html += self._generate_compliance_section(data['compliance_summary'])
        
        if 'trade_distribution' in data:
            html += self._generate_distribution_section(data['trade_distribution'])
        
        return html
    
    def _generate_advanced_metrics_section(self, metrics: Dict[str, Any]) -> str:
        """Generate advanced metrics section"""
        html = '''
        <div class="section">
            <h3>Advanced Performance Metrics</h3>
            <table>
                <tr><th>Metric</th><th>Value</th><th>Description</th></tr>
        '''
        
        metric_descriptions = {
            'sortino_ratio': 'Risk-adjusted return focusing on downside volatility',
            'calmar_ratio': 'Annual return divided by maximum drawdown',
            'recovery_factor': 'Net profit divided by maximum drawdown',
            'expectancy': 'Average profit/loss per trade',
            'largest_win': 'Largest single winning trade',
            'largest_loss': 'Largest single losing trade',
            'consecutive_wins': 'Maximum consecutive winning trades',
            'consecutive_losses': 'Maximum consecutive losing trades'
        }
        
        for key, value in metrics.items():
            description = metric_descriptions.get(key, '')
            formatted_value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
            html += f'<tr><td>{key.replace("_", " ").title()}</td><td>{formatted_value}</td><td>{description}</td></tr>'
        
        html += '</table></div>'
        return html
    
    def _generate_strategy_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Generate strategy analysis section"""
        html = '''
        <div class="section">
            <h3>Strategy Performance Analysis</h3>
            <table>
                <tr><th>Strategy</th><th>Trades</th><th>Win Rate</th><th>P&L</th><th>Avg Trade</th></tr>
        '''
        
        for strategy, data in analysis.items():
            win_rate = data.get('win_rate', 0)
            pnl = data.get('total_pnl', 0)
            avg_trade = data.get('avg_pnl_per_trade', 0)
            trades = data.get('trade_count', 0)
            
            pnl_class = 'positive' if pnl >= 0 else 'negative'
            html += f'''
            <tr>
                <td>{strategy}</td>
                <td>{trades}</td>
                <td>{win_rate:.1f}%</td>
                <td class="{pnl_class}">${pnl:.2f}</td>
                <td class="{pnl_class}">${avg_trade:.2f}</td>
            </tr>
            '''
        
        html += '</table></div>'
        return html
    
    def _generate_compliance_section(self, compliance_data: Dict[str, Any]) -> str:
        """Generate compliance section"""
        html = '''
        <div class="section">
            <h3>Compliance Summary</h3>
            <table>
                <tr><th>Status</th><th>Count</th><th>Percentage</th></tr>
        '''
        
        summary = compliance_data.get('summary', {})
        total = summary.get('total_events', 1)
        
        for status, count in summary.items():
            if status != 'total_events':
                percentage = (count / total * 100) if total > 0 else 0
                status_class = 'negative' if status == 'violations' else 'positive' if status == 'compliant' else ''
                html += f'<tr><td class="{status_class}">{status.title()}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>'
        
        html += '</table></div>'
        return html
    
    def _generate_distribution_section(self, distribution: Dict[str, Any]) -> str:
        """Generate trade distribution section"""
        html = '''
        <div class="section">
            <h3>Trade Distribution</h3>
        '''
        
        if 'by_symbol' in distribution:
            html += '<h4>Top Traded Symbols</h4><table><tr><th>Symbol</th><th>Trades</th></tr>'
            sorted_symbols = sorted(distribution['by_symbol'].items(), key=lambda x: x[1], reverse=True)[:10]
            for symbol, count in sorted_symbols:
                html += f'<tr><td>{symbol}</td><td>{count}</td></tr>'
            html += '</table>'
        
        if 'by_exchange' in distribution:
            html += '<h4>Exchange Distribution</h4><table><tr><th>Exchange</th><th>Trades</th></tr>'
            for exchange, count in distribution['by_exchange'].items():
                html += f'<tr><td>{exchange}</td><td>{count}</td></tr>'
            html += '</table>'
        
        html += '</div>'
        return html
    
    def _analyze_strategy_performance(self, strategy_name: str, trades: List[TradeInfo]) -> Dict[str, Any]:
        """Analyze performance of a specific strategy"""
        if not trades:
            return {'trade_count': 0, 'total_pnl': 0, 'win_rate': 0, 'avg_pnl_per_trade': 0}
        
        trade_pnls = [float(trade.pnl) for trade in trades if trade.pnl is not None]
        winning_trades = [pnl for pnl in trade_pnls if pnl > 0]
        
        return {
            'trade_count': len(trades),
            'total_pnl': sum(trade_pnls),
            'win_rate': (len(winning_trades) / len(trade_pnls) * 100) if trade_pnls else 0,
            'avg_pnl_per_trade': sum(trade_pnls) / len(trade_pnls) if trade_pnls else 0,
            'best_trade': max(trade_pnls) if trade_pnls else 0,
            'worst_trade': min(trade_pnls) if trade_pnls else 0,
            'volatility': (sum((pnl - sum(trade_pnls)/len(trade_pnls))**2 for pnl in trade_pnls) / len(trade_pnls))**0.5 if len(trade_pnls) > 1 else 0
        }
    
    def _find_best_strategy(self, analysis: Dict[str, Any]) -> str:
        """Find the best performing strategy"""
        if not analysis:
            return "None"
        
        best_strategy = max(analysis.items(), key=lambda x: x[1].get('total_pnl', 0))
        return best_strategy[0]
    
    def _find_worst_strategy(self, analysis: Dict[str, Any]) -> str:
        """Find the worst performing strategy"""
        if not analysis:
            return "None"
        
        worst_strategy = min(analysis.items(), key=lambda x: x[1].get('total_pnl', 0))
        return worst_strategy[0]
    
    def _generate_strategy_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate strategy recommendations based on analysis"""
        recommendations = []
        
        for strategy, data in analysis.items():
            win_rate = data.get('win_rate', 0)
            total_pnl = data.get('total_pnl', 0)
            trade_count = data.get('trade_count', 0)
            
            if win_rate < 40:
                recommendations.append(f"Consider reviewing {strategy} - low win rate ({win_rate:.1f}%)")
            
            if total_pnl < 0:
                recommendations.append(f"Strategy {strategy} is losing money - consider disabling or optimizing")
            
            if trade_count < 5:
                recommendations.append(f"Strategy {strategy} has low activity - check signal generation")
        
        if not recommendations:
            recommendations.append("All strategies are performing within acceptable parameters")
        
        return recommendations
    
    def _calculate_pnl_by_symbol(self, trades: List[TradeInfo]) -> Dict[str, float]:
        """Calculate P&L breakdown by symbol"""
        symbol_pnl = {}
        for trade in trades:
            if trade.pnl is not None:
                symbol_pnl[trade.symbol] = symbol_pnl.get(trade.symbol, 0) + float(trade.pnl)
        return symbol_pnl
    
    def _calculate_pnl_by_exchange(self, trades: List[TradeInfo]) -> Dict[str, float]:
        """Calculate P&L breakdown by exchange"""
        exchange_pnl = {}
        for trade in trades:
            if trade.pnl is not None:
                exchange_pnl[trade.exchange] = exchange_pnl.get(trade.exchange, 0) + float(trade.pnl)
        return exchange_pnl
    
    def _calculate_monthly_pnl(self, trades: List[TradeInfo]) -> Dict[str, float]:
        """Calculate monthly P&L"""
        monthly_pnl = {}
        for trade in trades:
            if trade.pnl is not None:
                month_key = trade.timestamp.strftime('%Y-%m')
                monthly_pnl[month_key] = monthly_pnl.get(month_key, 0) + float(trade.pnl)
        return monthly_pnl
    
    def _analyze_drawdowns(self, trades: List[TradeInfo]) -> Dict[str, Any]:
        """Analyze drawdown periods"""
        if not trades:
            return {}
        
        # Sort trades by timestamp
        sorted_trades = sorted(trades, key=lambda x: x.timestamp)
        
        # Calculate cumulative P&L
        cumulative_pnl = 0
        running_max = 0
        max_drawdown = 0
        current_drawdown = 0
        drawdown_periods = []
        
        for trade in sorted_trades:
            if trade.pnl is not None:
                cumulative_pnl += float(trade.pnl)
                
                if cumulative_pnl > running_max:
                    running_max = cumulative_pnl
                    current_drawdown = 0
                else:
                    current_drawdown = running_max - cumulative_pnl
                    max_drawdown = max(max_drawdown, current_drawdown)
        
        return {
            'max_drawdown': max_drawdown,
            'current_drawdown': current_drawdown,
            'drawdown_periods': len(drawdown_periods)
        }
    
    def _calculate_risk_adjusted_returns(self, trades: List[TradeInfo]) -> Dict[str, float]:
        """Calculate risk-adjusted return metrics"""
        if not trades:
            return {}
        
        trade_pnls = [float(trade.pnl) for trade in trades if trade.pnl is not None]
        
        if not trade_pnls:
            return {}
        
        mean_return = sum(trade_pnls) / len(trade_pnls)
        volatility = (sum((pnl - mean_return)**2 for pnl in trade_pnls) / len(trade_pnls))**0.5
        
        return {
            'sharpe_ratio': mean_return / volatility if volatility > 0 else 0,
            'information_ratio': mean_return / volatility if volatility > 0 else 0,
            'volatility': volatility
        }
    
    def _analyze_performance_attribution(self, trades: List[TradeInfo]) -> Dict[str, Any]:
        """Analyze what contributed to performance"""
        if not trades:
            return {}
        
        # Attribution by symbol
        symbol_contribution = self._calculate_pnl_by_symbol(trades)
        
        # Attribution by time of day
        hour_contribution = {}
        for trade in trades:
            if trade.pnl is not None:
                hour = trade.timestamp.hour
                hour_contribution[hour] = hour_contribution.get(hour, 0) + float(trade.pnl)
        
        return {
            'top_contributing_symbol': max(symbol_contribution.items(), key=lambda x: x[1]) if symbol_contribution else None,
            'worst_contributing_symbol': min(symbol_contribution.items(), key=lambda x: x[1]) if symbol_contribution else None,
            'best_trading_hour': max(hour_contribution.items(), key=lambda x: x[1]) if hour_contribution else None,
            'symbol_contributions': symbol_contribution,
            'hourly_contributions': hour_contribution
        }
    
    def _calculate_consecutive_wins(self, trade_pnls: List[float]) -> int:
        """Calculate maximum consecutive wins"""
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in trade_pnls:
            if pnl > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_consecutive_losses(self, trade_pnls: List[float]) -> int:
        """Calculate maximum consecutive losses"""
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in trade_pnls:
            if pnl < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_max_loss_period(self, trades: List[TradeInfo]) -> int:
        """Calculate maximum consecutive loss period in days"""
        if not trades:
            return 0
        
        sorted_trades = sorted(trades, key=lambda x: x.timestamp)
        max_loss_days = 0
        current_loss_start = None
        
        for trade in sorted_trades:
            if trade.pnl is not None and trade.pnl < 0:
                if current_loss_start is None:
                    current_loss_start = trade.timestamp
            else:
                if current_loss_start is not None:
                    loss_period = (trade.timestamp - current_loss_start).days
                    max_loss_days = max(max_loss_days, loss_period)
                    current_loss_start = None
        
        return max_loss_days
    
    def _convert_trade_to_order(self, trade: TradeInfo):
        """Convert TradeInfo to Order format for compliance reporting"""
        # This is a simplified conversion - in a real implementation,
        # you'd need to properly map to the Order model
        try:
            from src.models.data_models import Order, Symbol
            from src.markets.types import MarketType
        except ImportError:
            # Create minimal stubs
            class Order:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            class Symbol:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            class MarketType:
                CRYPTO = "crypto"
                FOREX = "forex"
        
        # Determine market type from symbol
        market_type = MarketType.CRYPTO if any(crypto in trade.symbol.upper() for crypto in ['BTC', 'ETH', 'USD']) else MarketType.FOREX
        
        symbol = Symbol(
            base_currency=trade.symbol.split('/')[0] if '/' in trade.symbol else trade.symbol[:3],
            quote_currency=trade.symbol.split('/')[1] if '/' in trade.symbol else trade.symbol[3:],
            market_type=market_type
        )
        
        return Order(
            id=f"trade_{trade.timestamp.strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            side=trade.side.lower(),
            amount=trade.quantity,
            price=trade.price,
            order_type='market',
            status='filled',
            timestamp=trade.timestamp
        )
    
    def _generate_performance_charts(self, data: Dict[str, Any], days: int) -> List[str]:
        """Generate performance charts for reports"""
        # This would generate actual charts using matplotlib
        # For now, return placeholder chart references
        charts = []
        
        try:
            import matplotlib.pyplot as plt
            import os
            
            # Create charts directory
            charts_dir = Path("reports/charts")
            charts_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate P&L chart
            if 'daily_pnl' in data:
                plt.figure(figsize=(12, 6))
                daily_pnl = data['daily_pnl']
                plt.plot(range(len(daily_pnl)), daily_pnl, linewidth=2)
                plt.title('Daily P&L Over Time')
                plt.xlabel('Days')
                plt.ylabel('P&L ($)')
                plt.grid(True, alpha=0.3)
                
                chart_file = charts_dir / f"daily_pnl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                charts.append(str(chart_file))
            
            return charts
            
        except ImportError:
            self.logger.warning("Matplotlib not available for chart generation")
            return []
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            return []


class CloseOrdersCommand(BaseCommand):
    """Close all open orders safely using real exchange APIs"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute close orders command"""
        timeout = getattr(args, 'timeout', 300)
        account_filter = getattr(args, 'account', None)
        
        self.logger.section("Closing All Open Orders")
        self.logger.info(f"Timeout: {timeout} seconds")
        
        if account_filter:
            self.logger.info(f"Account filter: {account_filter}")
        
        if not self.confirm_action("Close all open orders?", default=False):
            return CommandResult.info("Order closure cancelled by user")
        
        try:
            # Get real exchange connections and close orders
            closed_orders, failed_orders = asyncio.run(
                self._close_orders_via_exchanges(account_filter, timeout)
            )
            
            if failed_orders > 0:
                return CommandResult.warning(
                    f"Closed {closed_orders} orders, {failed_orders} failed",
                    suggestions=[
                        "Check failed orders manually",
                        "Verify account connectivity",
                        "Try closing failed orders individually",
                        "Check exchange API status"
                    ]
                )
            
            if closed_orders == 0:
                return CommandResult.info("No open orders found to close")
            
            return CommandResult.success(f"Successfully closed {closed_orders} order(s)")
                
        except Exception as e:
            self.logger.error(f"Error closing orders: {str(e)}")
            return CommandResult.error(
                f"Failed to close orders: {str(e)}",
                suggestions=[
                    "Check database connectivity",
                    "Verify exchange API access",
                    "Check network connectivity",
                    "Try again with shorter timeout"
                ]
            )
    
    async def _close_orders_via_exchanges(self, account_filter: Optional[str], timeout: int) -> Tuple[int, int]:
        """Close orders using real exchange APIs"""
        closed_orders = 0
        failed_orders = 0
        
        try:
            # Load account configurations
            accounts_config = self._load_accounts_config()
            
            if not accounts_config:
                self.logger.warning("No account configurations found")
                return 0, 0
            
            # Filter accounts if specified
            accounts_to_process = {}
            for account_name, account_config in accounts_config.items():
                if account_filter and account_filter not in account_name:
                    continue
                if not account_config.get('enabled', True):
                    continue
                accounts_to_process[account_name] = account_config
            
            if not accounts_to_process:
                self.logger.info("No matching enabled accounts found")
                return 0, 0
            
            self.logger.progress(f"Processing {len(accounts_to_process)} account(s)...")
            
            # Process each account
            for account_name, account_config in accounts_to_process.items():
                try:
                    self.logger.progress(f"Closing orders for {account_name}...")
                    
                    # Create exchange adapter
                    exchange_adapter = await self._create_exchange_adapter(account_name, account_config)
                    if not exchange_adapter:
                        self.logger.warning(f"Could not create adapter for {account_name}")
                        continue
                    
                    # Get open orders
                    open_orders = await exchange_adapter.get_open_orders()
                    
                    if not open_orders:
                        self.logger.info(f"No open orders for {account_name}")
                        continue
                    
                    self.logger.info(f"Found {len(open_orders)} open orders for {account_name}")
                    
                    # Close each order
                    for order in open_orders:
                        try:
                            await exchange_adapter.cancel_order(order.id, order.symbol)
                            closed_orders += 1
                            self.logger.info(f"Closed order {order.id} for {order.symbol}")
                        except Exception as e:
                            failed_orders += 1
                            self.logger.error(f"Failed to close order {order.id}: {e}")
                    
                    # Disconnect from exchange
                    await exchange_adapter.disconnect()
                    
                except Exception as e:
                    self.logger.error(f"Error processing account {account_name}: {e}")
                    failed_orders += 1
            
            return closed_orders, failed_orders
            
        except Exception as e:
            self.logger.error(f"Error in close orders process: {e}")
            return closed_orders, failed_orders
    
    async def _create_exchange_adapter(self, account_name: str, account_config: Dict[str, Any]) -> Optional[CCXTAdapter]:
        """Create and connect exchange adapter for an account"""
        try:
            # Determine exchange type
            exchange_type = account_config.get('exchange', account_config.get('type', ''))
            
            if not exchange_type:
                self.logger.error(f"No exchange type specified for {account_name}")
                return None
            
            # Create adapter configuration
            adapter_config = {
                'api_key': account_config.get('api_key', ''),
                'secret': account_config.get('secret', ''),
                'passphrase': account_config.get('passphrase', ''),
                'sandbox': account_config.get('sandbox', False),
                'test': account_config.get('test', False)
            }
            
            # Create and connect adapter
            adapter = CCXTAdapter(exchange_type, adapter_config)
            
            # Connect and authenticate
            if not await adapter.connect():
                self.logger.error(f"Failed to connect to {exchange_type} for {account_name}")
                return None
            
            if not await adapter.authenticate():
                self.logger.error(f"Failed to authenticate with {exchange_type} for {account_name}")
                await adapter.disconnect()
                return None
            
            return adapter
            
        except Exception as e:
            self.logger.error(f"Error creating exchange adapter for {account_name}: {e}")
            return None
    
    def _load_accounts_config(self) -> Dict[str, Any]:
        """Load accounts configuration from YAML file"""
        try:
            accounts_file = Path("config") / "accounts.yaml"
            if not accounts_file.exists():
                return {}
            
            with open(accounts_file, 'r') as f:
                accounts_data = yaml.safe_load(f)
            
            # Flatten the structure for easier access
            all_accounts = {}
            
            # Add crypto exchanges
            crypto_exchanges = accounts_data.get('crypto_exchanges', {})
            for name, config in crypto_exchanges.items():
                all_accounts[name] = {
                    **config,
                    'type': 'crypto',
                    'exchange': config.get('exchange_type', 'unknown')
                }
            
            # Add forex brokers
            forex_brokers = accounts_data.get('forex_brokers', {})
            for name, config in forex_brokers.items():
                all_accounts[name] = {
                    **config,
                    'type': 'forex',
                    'exchange': config.get('broker_type', 'unknown')
                }
            
            return all_accounts
            
        except Exception as e:
            self.logger.error(f"Error loading accounts configuration: {e}")
            return {}


class ComprehensiveStatusCommand(BaseCommand):
    """Show comprehensive bot status with resource usage and health metrics"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute comprehensive status command"""
        detailed = getattr(args, 'detailed', False)
        json_output = getattr(args, 'json', False)
        
        self.logger.section("Comprehensive Bot Status")
        
        try:
            # Gather all status information
            status_data = self._gather_comprehensive_status()
            
            if json_output:
                print(json.dumps(status_data, indent=2, default=str))
                return CommandResult.success("Comprehensive status displayed in JSON format")
            
            # Display formatted status
            self._display_comprehensive_status(status_data, detailed)
            
            return CommandResult.success(
                "Comprehensive status information displayed",
                data=status_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive status: {str(e)}")
            return CommandResult.error(
                f"Failed to get comprehensive bot status: {str(e)}",
                suggestions=[
                    "Check if bot process exists",
                    "Verify database connectivity",
                    "Check system permissions",
                    "Ensure configuration files are accessible"
                ]
            )
    
    def _gather_comprehensive_status(self) -> Dict[str, Any]:
        """Gather comprehensive status information from all sources"""
        status_data = {}
        
        try:
            # Process status
            process_manager = ProcessManager(self.context.workspace_path)
            bot_status = process_manager.get_bot_status()
            health_info = process_manager.monitor_health()
            
            status_data['process'] = {
                'running': bot_status.running,
                'pid': bot_status.pid,
                'uptime_seconds': bot_status.uptime.total_seconds() if bot_status.uptime else None,
                'memory_usage_mb': bot_status.memory_usage,
                'cpu_usage_percent': bot_status.cpu_usage,
                'error_message': bot_status.error_message,
                'healthy': health_info.get('healthy', False),
                'last_check': health_info.get('timestamp')
            }
            
            if bot_status.process_info:
                status_data['process'].update({
                    'process_name': bot_status.process_info.name,
                    'process_status': bot_status.process_info.status,
                    'memory_percent': bot_status.process_info.memory_percent,
                    'create_time': bot_status.process_info.create_time.isoformat(),
                    'command_line': bot_status.process_info.command_line
                })
            
        except Exception as e:
            self.logger.warning(f"Error gathering process status: {e}")
            status_data['process'] = {'error': str(e)}
        
        try:
            # Trading status
            with RealDataManager() as data_manager:
                trading_status = data_manager.get_bot_status_info()
                
                status_data['trading'] = {
                    'active_positions': trading_status.active_positions,
                    'total_pnl_today': float(trading_status.total_pnl_today),
                    'trades_today': trading_status.trades_today,
                    'active_strategies': trading_status.active_strategies,
                    'last_activity': trading_status.last_activity.isoformat() if trading_status.last_activity else None,
                    'error_count': trading_status.error_count
                }
                
        except Exception as e:
            self.logger.warning(f"Error gathering trading status: {e}")
            status_data['trading'] = {'error': str(e)}
        
        try:
            # System resources
            system_info = self._get_system_resources()
            status_data['system'] = system_info
            
        except Exception as e:
            self.logger.warning(f"Error gathering system status: {e}")
            status_data['system'] = {'error': str(e)}
        
        try:
            # Account connectivity
            account_status = asyncio.run(self._check_account_connectivity())
            status_data['accounts'] = account_status
            
        except Exception as e:
            self.logger.warning(f"Error checking account connectivity: {e}")
            status_data['accounts'] = {'error': str(e)}
        
        try:
            # Configuration status
            config_status = self._check_configuration_status()
            status_data['configuration'] = config_status
            
        except Exception as e:
            self.logger.warning(f"Error checking configuration: {e}")
            status_data['configuration'] = {'error': str(e)}
        
        return status_data
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information (basic)
            network_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 1)
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to get system resources: {str(e)}'}
    
    def _load_accounts_config(self) -> Dict[str, Any]:
        """Load accounts configuration"""
        try:
            import yaml
            accounts_file = Path(self.context.config_path) / "accounts.yaml"
            
            if not accounts_file.exists():
                return {}
            
            with open(accounts_file, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            # Flatten crypto and forex accounts
            all_accounts = {}
            
            # Add crypto exchanges
            crypto_exchanges = config.get('crypto_exchanges', {})
            for name, account_config in crypto_exchanges.items():
                account_config = dict(account_config)
                account_config['name'] = name
                account_config['type'] = 'crypto'
                all_accounts[name] = account_config
            
            # Add forex brokers
            forex_brokers = config.get('forex_brokers', {})
            for name, account_config in forex_brokers.items():
                account_config = dict(account_config)
                account_config['name'] = name
                account_config['type'] = 'forex'
                all_accounts[name] = account_config
            
            return all_accounts
            
        except Exception as e:
            self.logger.warning(f"Failed to load accounts config: {e}")
            return {}

    async def _check_account_connectivity(self) -> Dict[str, Any]:
        """Check connectivity to all configured accounts"""
        try:
            accounts_config = self._load_accounts_config()
            
            if not accounts_config:
                return {'total_accounts': 0, 'connected': 0, 'failed': 0, 'accounts': []}
            
            account_statuses = []
            connected_count = 0
            failed_count = 0
            
            for account_name, account_config in accounts_config.items():
                if not account_config.get('enabled', True):
                    continue
                
                try:
                    # Quick connectivity test (simplified for now)
                    # In a real implementation, this would test actual connectivity
                    status = 'unknown'  # Simplified for now
                    
                    account_statuses.append({
                        'name': account_name,
                        'type': account_config.get('type', 'unknown'),
                        'status': status,
                        'enabled': account_config.get('enabled', True)
                    })
                    
                except Exception as e:
                    failed_count += 1
                    account_statuses.append({
                        'name': account_name,
                        'type': account_config.get('type', 'unknown'),
                        'status': 'failed',
                        'error': str(e),
                        'enabled': account_config.get('enabled', True)
                    })
                    
                    account_statuses.append({
                        'name': account_name,
                        'exchange': account_config.get('exchange', 'unknown'),
                        'status': status,
                        'enabled': account_config.get('enabled', True)
                    })
                    
                except Exception as e:
                    failed_count += 1
                    account_statuses.append({
                        'name': account_name,
                        'exchange': account_config.get('exchange', 'unknown'),
                        'status': 'error',
                        'error': str(e),
                        'enabled': account_config.get('enabled', True)
                    })
            
            return {
                'total_accounts': len(account_statuses),
                'connected': connected_count,
                'failed': failed_count,
                'accounts': account_statuses
            }
            
        except Exception as e:
            return {'error': f'Failed to check account connectivity: {str(e)}'}
    
    def _check_configuration_status(self) -> Dict[str, Any]:
        """Check configuration file status and validity"""
        try:
            config_manager = ConfigManager()
            
            # Check main configuration
            main_config_exists = (Path("config") / "trading_bot_config.yaml").exists()
            accounts_config_exists = (Path("config") / "accounts.yaml").exists()
            
            # Check configuration validity
            config_valid = False
            config_error = None
            try:
                config = config_manager.load_config()
                config_valid = config is not None
            except Exception as e:
                config_error = str(e)
            
            # Check strategy configurations
            strategy_manager = StrategyConfigManager()
            available_strategies = strategy_manager.get_available_templates()
            
            return {
                'main_config': {
                    'exists': main_config_exists,
                    'valid': config_valid,
                    'error': config_error
                },
                'accounts_config': {
                    'exists': accounts_config_exists
                },
                'strategies': {
                    'available_templates': len(available_strategies),
                    'templates': available_strategies
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to check configuration status: {str(e)}'}
    
    def _display_comprehensive_status(self, status_data: Dict[str, Any], detailed: bool) -> None:
        """Display comprehensive status in formatted output"""
        
        # Process Status
        self.logger.subsection("Process Status")
        process_data = status_data.get('process', {})
        
        if 'error' in process_data:
            self.logger.list_item(f"❌ Error: {process_data['error']}", "error")
        else:
            running = process_data.get('running', False)
            status_icon = "🟢 Running" if running else "🔴 Stopped"
            
            self.logger.list_item(f"Status: {status_icon}", "info")
            
            if running:
                if process_data.get('pid'):
                    self.logger.list_item(f"Process ID: {process_data['pid']}", "info")
                
                if process_data.get('uptime_seconds'):
                    uptime = self._format_uptime_seconds(process_data['uptime_seconds'])
                    self.logger.list_item(f"Uptime: {uptime}", "info")
                
                if process_data.get('memory_usage_mb'):
                    self.logger.list_item(f"Memory Usage: {process_data['memory_usage_mb']:.1f} MB", "info")
                
                if process_data.get('cpu_usage_percent'):
                    self.logger.list_item(f"CPU Usage: {process_data['cpu_usage_percent']:.1f}%", "info")
                
                healthy = process_data.get('healthy', False)
                health_icon = "✅ Healthy" if healthy else "⚠️ Unhealthy"
                self.logger.list_item(f"Health: {health_icon}", "info")
        
        # Trading Status
        self.logger.subsection("Trading Status")
        trading_data = status_data.get('trading', {})
        
        if 'error' in trading_data:
            self.logger.list_item(f"❌ Error: {trading_data['error']}", "error")
        else:
            pnl = trading_data.get('total_pnl_today', 0)
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            
            self.logger.list_item(f"Active Positions: {trading_data.get('active_positions', 0)}", "info")
            self.logger.list_item(f"Trades Today: {trading_data.get('trades_today', 0)}", "info")
            self.logger.list_item(f"P&L Today: {pnl_str}", "info")
            self.logger.list_item(f"Errors Today: {trading_data.get('error_count', 0)}", "info")
            
            strategies = trading_data.get('active_strategies', [])
            if strategies:
                self.logger.list_item(f"Active Strategies: {', '.join(strategies)}", "info")
        
        # System Resources
        self.logger.subsection("System Resources")
        system_data = status_data.get('system', {})
        
        if 'error' in system_data:
            self.logger.list_item(f"❌ Error: {system_data['error']}", "error")
        else:
            cpu_data = system_data.get('cpu', {})
            memory_data = system_data.get('memory', {})
            disk_data = system_data.get('disk', {})
            
            if cpu_data:
                self.logger.list_item(f"CPU Usage: {cpu_data.get('usage_percent', 0):.1f}% ({cpu_data.get('count', 0)} cores)", "info")
            
            if memory_data:
                self.logger.list_item(f"Memory: {memory_data.get('used_gb', 0):.1f}GB / {memory_data.get('total_gb', 0):.1f}GB ({memory_data.get('usage_percent', 0):.1f}%)", "info")
            
            if disk_data:
                self.logger.list_item(f"Disk: {disk_data.get('used_gb', 0):.1f}GB / {disk_data.get('total_gb', 0):.1f}GB ({disk_data.get('usage_percent', 0):.1f}%)", "info")
        
        # Account Connectivity
        self.logger.subsection("Account Connectivity")
        accounts_data = status_data.get('accounts', {})
        
        if 'error' in accounts_data:
            self.logger.list_item(f"❌ Error: {accounts_data['error']}", "error")
        else:
            total = accounts_data.get('total_accounts', 0)
            connected = accounts_data.get('connected', 0)
            failed = accounts_data.get('failed', 0)
            
            self.logger.list_item(f"Total Accounts: {total}", "info")
            self.logger.list_item(f"Connected: {connected}", "info")
            self.logger.list_item(f"Failed: {failed}", "info")
            
            if detailed and accounts_data.get('accounts'):
                for account in accounts_data['accounts']:
                    status_icon = "✅" if account['status'] == 'connected' else "❌"
                    self.logger.list_item(f"  {status_icon} {account['name']} ({account['exchange']})", "info")
        
        # Configuration Status
        self.logger.subsection("Configuration Status")
        config_data = status_data.get('configuration', {})
        
        if 'error' in config_data:
            self.logger.list_item(f"❌ Error: {config_data['error']}", "error")
        else:
            main_config = config_data.get('main_config', {})
            accounts_config = config_data.get('accounts_config', {})
            strategies = config_data.get('strategies', {})
            
            main_icon = "✅" if main_config.get('exists') and main_config.get('valid') else "❌"
            self.logger.list_item(f"Main Config: {main_icon}", "info")
            
            accounts_icon = "✅" if accounts_config.get('exists') else "❌"
            self.logger.list_item(f"Accounts Config: {accounts_icon}", "info")
            
            strategy_count = strategies.get('available_templates', 0)
            self.logger.list_item(f"Available Strategies: {strategy_count}", "info")
    
    def _format_uptime_seconds(self, seconds: float) -> str:
        """Format uptime seconds as human-readable string"""
        total_seconds = int(seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"