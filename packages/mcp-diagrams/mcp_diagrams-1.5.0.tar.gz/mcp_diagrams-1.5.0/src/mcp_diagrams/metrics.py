"""Metrics collection for production monitoring"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger("mcp_diagrams.metrics")


@dataclass
class OperationMetrics:
    """Metrics for a single operation type"""
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: float = 0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

    @property
    def average_duration_ms(self) -> float:
        """Calculate average duration"""
        if self.total_count == 0:
            return 0
        return self.total_duration_ms / self.total_count

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_count == 0:
            return 100.0
        return (self.success_count / self.total_count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": f"{self.success_rate:.2f}%",
            "avg_duration_ms": f"{self.average_duration_ms:.2f}",
            "min_duration_ms": f"{self.min_duration_ms:.2f}" if self.min_duration_ms != float('inf') else "N/A",
            "max_duration_ms": f"{self.max_duration_ms:.2f}",
            "last_error": self.last_error,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None
        }


class MetricsCollector:
    """Collects and reports metrics for the MCP Diagrams Server"""

    def __init__(self, metrics_dir: Optional[Path] = None):
        self.start_time = datetime.now()
        self.metrics: Dict[str, OperationMetrics] = defaultdict(OperationMetrics)
        self.recent_errors = deque(maxlen=100)  # Keep last 100 errors
        self.metrics_dir = metrics_dir

        # Only try to create directory if a path was provided
        if self.metrics_dir:
            try:
                self.metrics_dir.mkdir(exist_ok=True)
            except (OSError, PermissionError):
                # If we can't create the directory, work in memory only
                self.metrics_dir = None
                logger.debug("Cannot create metrics directory, operating in memory-only mode")

        # Session metrics
        self.active_sessions = 0
        self.total_sessions_created = 0
        self.total_sessions_deleted = 0

        # Node metrics
        self.total_nodes_created = 0
        self.largest_diagram_nodes = 0

        # Rate limiting metrics
        self.rate_limit_hits = 0

        # Initialize logger only if we have a writable directory
        if self.metrics_dir:
            try:
                self._setup_logging()
            except (OSError, PermissionError):
                # If we can't setup logging, continue without it
                logger.debug("Cannot setup file logging, using console only")

    def _setup_logging(self):
        """Setup production logging"""
        log_file = self.metrics_dir / "mcp_diagrams.log"

        # File handler for all logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Error file handler
        error_log_file = self.metrics_dir / "mcp_diagrams_errors.log"
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.setLevel(logging.INFO)

    def record_operation(self, operation: str, success: bool, duration_ms: float,
                         error: Optional[str] = None, metadata: Optional[Dict] = None):
        """Record metrics for an operation"""
        metrics = self.metrics[operation]
        metrics.total_count += 1

        if success:
            metrics.success_count += 1
        else:
            metrics.failure_count += 1
            metrics.last_error = error
            metrics.last_error_time = datetime.now()

            # Log error
            logger.error(f"Operation {operation} failed: {error}", extra={"metadata": metadata})

            # Track recent errors
            self.recent_errors.append({
                "operation": operation,
                "error": error,
                "time": datetime.now().isoformat(),
                "metadata": metadata
            })

        # Update duration metrics
        metrics.total_duration_ms += duration_ms
        metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
        metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)

        # Log slow operations
        if duration_ms > 5000:  # More than 5 seconds
            logger.warning(f"Slow operation: {operation} took {duration_ms:.2f}ms",
                          extra={"metadata": metadata})

    def record_session_created(self, session_id: str, node_count: int = 0):
        """Record session creation"""
        self.active_sessions += 1
        self.total_sessions_created += 1
        logger.info(f"Session created: {session_id}", extra={"node_count": node_count})

    def record_session_deleted(self, session_id: str):
        """Record session deletion"""
        self.active_sessions = max(0, self.active_sessions - 1)
        self.total_sessions_deleted += 1
        logger.info(f"Session deleted: {session_id}")

    def record_nodes_added(self, count: int, session_id: str):
        """Record nodes being added"""
        self.total_nodes_created += count
        logger.debug(f"Added {count} nodes to session {session_id}")

    def record_diagram_size(self, node_count: int):
        """Track largest diagram"""
        self.largest_diagram_nodes = max(self.largest_diagram_nodes, node_count)
        if node_count > 100:
            logger.info(f"Large diagram rendered: {node_count} nodes")

    def record_rate_limit_hit(self, session_id: str):
        """Record rate limit being hit"""
        self.rate_limit_hits += 1
        logger.warning(f"Rate limit hit for session: {session_id}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        uptime = datetime.now() - self.start_time

        return {
            "server": {
                "start_time": self.start_time.isoformat(),
                "uptime_hours": f"{uptime.total_seconds() / 3600:.2f}",
                "version": "1.0.0"
            },
            "sessions": {
                "active": self.active_sessions,
                "total_created": self.total_sessions_created,
                "total_deleted": self.total_sessions_deleted
            },
            "nodes": {
                "total_created": self.total_nodes_created,
                "largest_diagram": self.largest_diagram_nodes
            },
            "rate_limiting": {
                "total_hits": self.rate_limit_hits
            },
            "operations": {
                name: metrics.to_dict()
                for name, metrics in self.metrics.items()
            },
            "recent_errors": list(self.recent_errors)[-10:]  # Last 10 errors
        }

    def save_metrics_snapshot(self):
        """Save metrics snapshot to file"""
        snapshot_file = self.metrics_dir / f"metrics_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(snapshot_file, 'w') as f:
                json.dump(self.get_metrics_summary(), f, indent=2, default=str)

            logger.info(f"Metrics snapshot saved to {snapshot_file}")

            # Clean up old snapshots (keep last 100)
            snapshots = sorted(self.metrics_dir.glob("metrics_snapshot_*.json"))
            if len(snapshots) > 100:
                for old_snapshot in snapshots[:-100]:
                    old_snapshot.unlink()

        except Exception as e:
            logger.error(f"Failed to save metrics snapshot: {e}")

    def log_health_check(self):
        """Log health check information"""
        metrics = self.get_metrics_summary()

        # Check health indicators
        health_status = "healthy"
        issues = []

        # Check error rate
        for op_name, op_metrics in self.metrics.items():
            if op_metrics.success_rate < 95 and op_metrics.total_count > 10:
                issues.append(f"High error rate for {op_name}: {op_metrics.success_rate:.1f}%")
                health_status = "degraded"

        # Check for memory issues (too many active sessions)
        if self.active_sessions > 100:
            issues.append(f"High number of active sessions: {self.active_sessions}")
            health_status = "warning"

        logger.info(f"Health check: {health_status}", extra={
            "active_sessions": self.active_sessions,
            "recent_errors": len(self.recent_errors),
            "issues": issues
        })

        return {
            "status": health_status,
            "issues": issues,
            "metrics": metrics
        }


# Global metrics collector instance
# Initialize without directory to work in memory-only mode (avoids read-only filesystem issues)
metrics_collector = MetricsCollector(metrics_dir=None)


def track_operation(operation_name: str):
    """Decorator to track operation metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            result = None

            try:
                result = func(*args, **kwargs)
                success = result.get("status") == "success" if isinstance(result, dict) else True
                error = result.get("error") if isinstance(result, dict) and not success else None
            except Exception as e:
                success = False
                error = str(e)
                result = {"status": "error", "error": error}
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Extract session_id if available
                session_id = None
                if args and len(args) > 0:
                    if isinstance(args[0], str):
                        session_id = args[0]
                    elif isinstance(args[0], dict) and "session_id" in args[0]:
                        session_id = args[0]["session_id"]
                elif "session_id" in kwargs:
                    session_id = kwargs["session_id"]

                metrics_collector.record_operation(
                    operation_name,
                    success,
                    duration_ms,
                    error,
                    {"session_id": session_id} if session_id else None
                )

            return result

        return wrapper
    return decorator