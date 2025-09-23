"""
Log aggregation preparation and structured logging for machine processing.

This module provides utilities for preparing logs for aggregation systems
like ELK Stack, Fluentd, Splunk, and other log processing platforms.
"""

import json
import gzip
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Iterator
from enum import Enum
import logging

from .context import LogContext


class AggregationFormat(Enum):
    """Supported log aggregation formats."""
    ELASTICSEARCH = "elasticsearch"
    FLUENTD = "fluentd"
    SPLUNK = "splunk"
    LOGSTASH = "logstash"
    GENERIC_JSON = "generic_json"


@dataclass
class StructuredLogEntry:
    """Represents a structured log entry for aggregation."""
    timestamp: datetime
    level: str
    logger: str
    message: str
    context: Optional[LogContext] = None
    metadata: Optional[Dict[str, Any]] = None
    exception: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'timestamp': self.timestamp.isoformat() + 'Z',
            'level': self.level,
            'logger': self.logger,
            'message': self.message
        }
        
        if self.context:
            result['context'] = asdict(self.context)
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        if self.exception:
            result['exception'] = self.exception
        
        if self.performance:
            result['performance'] = self.performance
        
        return result


class LogAggregationFormatter(ABC):
    """Abstract base class for log aggregation formatters."""
    
    @abstractmethod
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format a log entry for the target aggregation system."""
        pass
    
    @abstractmethod
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format a batch of log entries."""
        pass


class ElasticsearchFormatter(LogAggregationFormatter):
    """Formatter for Elasticsearch/ELK Stack."""
    
    def __init__(self, index_name: str = "trading-bot-logs"):
        """
        Initialize Elasticsearch formatter.
        
        Args:
            index_name: Elasticsearch index name
        """
        self.index_name = index_name
    
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format entry for Elasticsearch bulk API."""
        # Action line
        action = {
            "index": {
                "_index": self.index_name,
                "_type": "_doc"
            }
        }
        
        # Document line
        document = entry.to_dict()
        
        # Add Elasticsearch-specific fields
        document['@timestamp'] = entry.timestamp.isoformat() + 'Z'
        document['host'] = self._get_host_info()
        document['tags'] = self._generate_tags(entry)
        
        return json.dumps(action) + '\n' + json.dumps(document)
    
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format batch for Elasticsearch bulk API."""
        lines = []
        for entry in entries:
            lines.append(self.format_entry(entry))
        
        return '\n'.join(lines) + '\n'
    
    def _get_host_info(self) -> Dict[str, str]:
        """Get host information."""
        import socket
        import os
        
        return {
            'hostname': socket.gethostname(),
            'ip': socket.gethostbyname(socket.gethostname()),
            'pid': str(os.getpid())
        }
    
    def _generate_tags(self, entry: StructuredLogEntry) -> List[str]:
        """Generate tags for the log entry."""
        tags = [
            f"level:{entry.level.lower()}",
            f"logger:{entry.logger}"
        ]
        
        if entry.context:
            if entry.context.component:
                tags.append(f"component:{entry.context.component}")
            if entry.context.operation:
                tags.append(f"operation:{entry.context.operation}")
            if entry.context.exchange:
                tags.append(f"exchange:{entry.context.exchange}")
            if entry.context.symbol:
                tags.append(f"symbol:{entry.context.symbol}")
        
        return tags


class FluentdFormatter(LogAggregationFormatter):
    """Formatter for Fluentd."""
    
    def __init__(self, tag: str = "trading_bot"):
        """
        Initialize Fluentd formatter.
        
        Args:
            tag: Fluentd tag
        """
        self.tag = tag
    
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format entry for Fluentd."""
        fluentd_entry = {
            'tag': self.tag,
            'time': int(entry.timestamp.timestamp()),
            'record': entry.to_dict()
        }
        
        return json.dumps(fluentd_entry)
    
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format batch for Fluentd."""
        formatted_entries = [self.format_entry(entry) for entry in entries]
        return '\n'.join(formatted_entries)


class SplunkFormatter(LogAggregationFormatter):
    """Formatter for Splunk."""
    
    def __init__(self, source: str = "trading_bot", sourcetype: str = "json"):
        """
        Initialize Splunk formatter.
        
        Args:
            source: Splunk source field
            sourcetype: Splunk sourcetype field
        """
        self.source = source
        self.sourcetype = sourcetype
    
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format entry for Splunk."""
        splunk_entry = {
            'time': entry.timestamp.timestamp(),
            'source': self.source,
            'sourcetype': self.sourcetype,
            'event': entry.to_dict()
        }
        
        return json.dumps(splunk_entry)
    
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format batch for Splunk."""
        formatted_entries = [self.format_entry(entry) for entry in entries]
        return '\n'.join(formatted_entries)


class LogstashFormatter(LogAggregationFormatter):
    """Formatter for Logstash."""
    
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format entry for Logstash."""
        logstash_entry = entry.to_dict()
        
        # Add Logstash-specific fields
        logstash_entry['@version'] = "1"
        logstash_entry['@timestamp'] = entry.timestamp.isoformat() + 'Z'
        logstash_entry['host'] = self._get_host_info()
        
        return json.dumps(logstash_entry)
    
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format batch for Logstash."""
        formatted_entries = [self.format_entry(entry) for entry in entries]
        return '\n'.join(formatted_entries)
    
    def _get_host_info(self) -> str:
        """Get host information."""
        import socket
        return socket.gethostname()


class GenericJSONFormatter(LogAggregationFormatter):
    """Generic JSON formatter for custom aggregation systems."""
    
    def __init__(self, include_metadata: bool = True):
        """
        Initialize generic JSON formatter.
        
        Args:
            include_metadata: Whether to include metadata fields
        """
        self.include_metadata = include_metadata
    
    def format_entry(self, entry: StructuredLogEntry) -> str:
        """Format entry as generic JSON."""
        json_entry = entry.to_dict()
        
        if self.include_metadata:
            json_entry['formatted_at'] = datetime.utcnow().isoformat() + 'Z'
            json_entry['version'] = "1.0"
        
        return json.dumps(json_entry)
    
    def format_batch(self, entries: List[StructuredLogEntry]) -> str:
        """Format batch as JSON array."""
        formatted_entries = [json.loads(self.format_entry(entry)) for entry in entries]
        return json.dumps(formatted_entries, indent=2)


class LogAggregationPreparer:
    """Prepares logs for aggregation systems."""
    
    def __init__(self, format_type: AggregationFormat = AggregationFormat.ELASTICSEARCH):
        """
        Initialize log aggregation preparer.
        
        Args:
            format_type: Target aggregation format
        """
        self.format_type = format_type
        self.formatter = self._create_formatter(format_type)
        self.buffer: List[StructuredLogEntry] = []
        self.buffer_size = 1000
        self.output_directory = Path("logs/aggregation")
        self.output_directory.mkdir(parents=True, exist_ok=True)
    
    def _create_formatter(self, format_type: AggregationFormat) -> LogAggregationFormatter:
        """Create formatter based on format type."""
        if format_type == AggregationFormat.ELASTICSEARCH:
            return ElasticsearchFormatter()
        elif format_type == AggregationFormat.FLUENTD:
            return FluentdFormatter()
        elif format_type == AggregationFormat.SPLUNK:
            return SplunkFormatter()
        elif format_type == AggregationFormat.LOGSTASH:
            return LogstashFormatter()
        elif format_type == AggregationFormat.GENERIC_JSON:
            return GenericJSONFormatter()
        else:
            raise ValueError(f"Unsupported aggregation format: {format_type}")
    
    def add_log_entry(self, entry: StructuredLogEntry) -> None:
        """Add a log entry to the buffer."""
        self.buffer.append(entry)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self) -> Optional[Path]:
        """Flush the buffer to a file."""
        if not self.buffer:
            return None
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_{self.format_type.value}_{timestamp}.json"
        
        if self.format_type == AggregationFormat.ELASTICSEARCH:
            filename = f"logs_elasticsearch_{timestamp}.ndjson"
        
        output_path = self.output_directory / filename
        
        try:
            formatted_data = self.formatter.format_batch(self.buffer)
            
            # Compress if file is large
            if len(formatted_data) > 1024 * 1024:  # 1MB
                output_path = output_path.with_suffix(output_path.suffix + '.gz')
                with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                    f.write(formatted_data)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_data)
            
            self.buffer.clear()
            return output_path
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to flush aggregation buffer: {e}")
            return None
    
    def create_log_entry_from_record(self, record: logging.LogRecord) -> StructuredLogEntry:
        """Create StructuredLogEntry from logging.LogRecord."""
        # Extract context if available
        context = None
        if hasattr(record, 'context') and record.context:
            if isinstance(record.context, LogContext):
                context = record.context
            elif isinstance(record.context, dict):
                context = LogContext(**record.context)
        
        # Extract metadata
        metadata = {
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'process_name': record.processName
        }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info', 'context']:
                metadata[key] = value
        
        # Extract exception information
        exception = None
        if record.exc_info:
            import traceback
            exception = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Extract performance information if available
        performance = None
        if hasattr(record, 'performance') and record.performance:
            performance = record.performance
        
        return StructuredLogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            context=context,
            metadata=metadata,
            exception=exception,
            performance=performance
        )


class AggregationHandler(logging.Handler):
    """Logging handler that prepares logs for aggregation."""
    
    def __init__(self, format_type: AggregationFormat = AggregationFormat.ELASTICSEARCH):
        """
        Initialize aggregation handler.
        
        Args:
            format_type: Target aggregation format
        """
        super().__init__()
        self.preparer = LogAggregationPreparer(format_type)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record for aggregation."""
        try:
            entry = self.preparer.create_log_entry_from_record(record)
            self.preparer.add_log_entry(entry)
        except Exception:
            self.handleError(record)
    
    def close(self) -> None:
        """Close the handler and flush remaining logs."""
        self.preparer.flush_buffer()
        super().close()


class LogAnalyzer:
    """Analyzes logs for patterns and insights."""
    
    def __init__(self):
        """Initialize log analyzer."""
        self.patterns = defaultdict(int)
        self.error_patterns = defaultdict(int)
        self.performance_data = defaultdict(list)
    
    def analyze_log_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a log file for patterns and insights.
        
        Args:
            file_path: Path to log file
            
        Returns:
            Analysis results
        """
        analysis = {
            'file_info': {
                'path': str(file_path),
                'size_bytes': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            },
            'log_levels': defaultdict(int),
            'loggers': defaultdict(int),
            'error_patterns': defaultdict(int),
            'time_range': {'start': None, 'end': None},
            'performance_stats': {},
            'anomalies': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Try to parse as JSON
                        log_entry = json.loads(line)
                        self._analyze_json_entry(log_entry, analysis)
                    except json.JSONDecodeError:
                        # Try to parse as standard format
                        self._analyze_text_entry(line, analysis)
        
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_json_entry(self, entry: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Analyze a JSON log entry."""
        # Count log levels
        level = entry.get('level', 'UNKNOWN')
        analysis['log_levels'][level] += 1
        
        # Count loggers
        logger = entry.get('logger', 'UNKNOWN')
        analysis['loggers'][logger] += 1
        
        # Track time range
        timestamp = entry.get('timestamp')
        if timestamp:
            if not analysis['time_range']['start']:
                analysis['time_range']['start'] = timestamp
            analysis['time_range']['end'] = timestamp
        
        # Analyze errors
        if level in ['ERROR', 'CRITICAL']:
            message = entry.get('message', '')
            # Extract error pattern (first 50 characters)
            pattern = message[:50] + '...' if len(message) > 50 else message
            analysis['error_patterns'][pattern] += 1
        
        # Analyze performance data
        if 'performance' in entry:
            perf_data = entry['performance']
            if 'execution_time_ms' in perf_data:
                operation = entry.get('context', {}).get('operation', 'unknown')
                analysis['performance_stats'].setdefault(operation, []).append(
                    perf_data['execution_time_ms']
                )
    
    def _analyze_text_entry(self, line: str, analysis: Dict[str, Any]) -> None:
        """Analyze a text log entry."""
        # Simple pattern matching for standard log format
        parts = line.split(' - ')
        if len(parts) >= 3:
            level_part = parts[2] if len(parts) > 2 else 'UNKNOWN'
            analysis['log_levels'][level_part] += 1
    
    def generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from log analysis."""
        insights = []
        
        # Error rate insights
        total_logs = sum(analysis['log_levels'].values())
        error_logs = analysis['log_levels'].get('ERROR', 0) + analysis['log_levels'].get('CRITICAL', 0)
        
        if total_logs > 0:
            error_rate = (error_logs / total_logs) * 100
            if error_rate > 10:
                insights.append(f"High error rate: {error_rate:.1f}% of logs are errors")
            elif error_rate > 5:
                insights.append(f"Moderate error rate: {error_rate:.1f}% of logs are errors")
        
        # Performance insights
        for operation, times in analysis['performance_stats'].items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                
                if avg_time > 1000:  # More than 1 second
                    insights.append(f"Slow operation '{operation}': avg {avg_time:.0f}ms, max {max_time:.0f}ms")
        
        # Volume insights
        if total_logs > 100000:
            insights.append(f"High log volume: {total_logs:,} log entries")
        
        # Top error patterns
        if analysis['error_patterns']:
            top_error = max(analysis['error_patterns'].items(), key=lambda x: x[1])
            insights.append(f"Most common error: '{top_error[0]}' ({top_error[1]} occurrences)")
        
        return insights


def create_aggregation_config(
    format_type: AggregationFormat,
    output_directory: str = "logs/aggregation",
    buffer_size: int = 1000,
    compress_output: bool = True
) -> Dict[str, Any]:
    """
    Create configuration for log aggregation.
    
    Args:
        format_type: Target aggregation format
        output_directory: Output directory for aggregated logs
        buffer_size: Buffer size before flushing
        compress_output: Whether to compress output files
        
    Returns:
        Configuration dictionary
    """
    return {
        'aggregation': {
            'enabled': True,
            'format_type': format_type.value,
            'output_directory': output_directory,
            'buffer_size': buffer_size,
            'compress_output': compress_output,
            'flush_interval': 300,  # 5 minutes
            'retention_days': 30
        }
    }


def setup_log_aggregation(config: Dict[str, Any]) -> Optional[AggregationHandler]:
    """
    Set up log aggregation based on configuration.
    
    Args:
        config: Aggregation configuration
        
    Returns:
        AggregationHandler if enabled, None otherwise
    """
    aggregation_config = config.get('aggregation', {})
    
    if not aggregation_config.get('enabled', False):
        return None
    
    format_type = AggregationFormat(aggregation_config.get('format_type', 'elasticsearch'))
    handler = AggregationHandler(format_type)
    
    # Configure handler
    if 'buffer_size' in aggregation_config:
        handler.preparer.buffer_size = aggregation_config['buffer_size']
    
    if 'output_directory' in aggregation_config:
        handler.preparer.output_directory = Path(aggregation_config['output_directory'])
        handler.preparer.output_directory.mkdir(parents=True, exist_ok=True)
    
    return handler