"""
Production monitoring and observability for DataGuild Snowflake Connector
"""

import time
import logging
import threading
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import psutil
import requests
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics supported."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """A single metric measurement."""
    name: str
    value: float
    type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # "healthy", "unhealthy", "degraded"
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


class MetricsCollector:
    """Collects and stores metrics."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[Metric] = []
        self.lock = threading.Lock()
    
    def add_metric(self, name: str, value: float, metric_type: MetricType, 
                   labels: Optional[Dict[str, str]] = None) -> None:
        """Add a metric."""
        with self.lock:
            metric = Metric(
                name=name,
                value=value,
                type=metric_type,
                labels=labels or {}
            )
            self.metrics.append(metric)
            
            # Keep only the most recent metrics
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def get_metrics(self, name: Optional[str] = None, 
                   since: Optional[datetime] = None) -> List[Metric]:
        """Get metrics, optionally filtered."""
        with self.lock:
            metrics = self.metrics
            
            if name:
                metrics = [m for m in metrics if m.name == name]
            
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            
            return metrics.copy()
    
    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self.lock:
            summary = {}
            for metric in self.metrics:
                if metric.name not in summary:
                    summary[metric.name] = {
                        'count': 0,
                        'total': 0.0,
                        'min': float('inf'),
                        'max': float('-inf'),
                        'type': metric.type
                    }
                
                summary[metric.name]['count'] += 1
                summary[metric.name]['total'] += metric.value
                summary[metric.name]['min'] = min(summary[metric.name]['min'], metric.value)
                summary[metric.name]['max'] = max(summary[metric.name]['max'], metric.value)
            
            # Calculate averages
            for name, stats in summary.items():
                if stats['count'] > 0:
                    stats['average'] = stats['total'] / stats['count']
                else:
                    stats['average'] = 0.0
            
            return summary


class HealthChecker:
    """Performs health checks."""
    
    def __init__(self):
        self.checks: List[Callable[[], HealthCheck]] = []
    
    def add_check(self, check_func: Callable[[], HealthCheck]) -> None:
        """Add a health check function."""
        self.checks.append(check_func)
    
    def run_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        results = []
        for check_func in self.checks:
            try:
                start_time = time.time()
                result = check_func()
                result.duration_ms = (time.time() - start_time) * 1000
                results.append(result)
            except Exception as e:
                results.append(HealthCheck(
                    name=check_func.__name__,
                    status="unhealthy",
                    message=f"Check failed: {str(e)}"
                ))
        return results


class SystemMonitor:
    """Monitors system resources."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.running = False
        self.thread = None
    
    def start(self, interval: int = 30) -> None:
        """Start system monitoring."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        logger.info("System monitoring started")
    
    def stop(self) -> None:
        """Stop system monitoring."""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: int) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.add_metric(
                "system_cpu_percent", cpu_percent, MetricType.GAUGE
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics_collector.add_metric(
                "system_memory_percent", memory.percent, MetricType.GAUGE
            )
            self.metrics_collector.add_metric(
                "system_memory_used_mb", memory.used / 1024 / 1024, MetricType.GAUGE
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics_collector.add_metric(
                "system_disk_percent", disk.percent, MetricType.GAUGE
            )
            self.metrics_collector.add_metric(
                "system_disk_free_gb", disk.free / 1024 / 1024 / 1024, MetricType.GAUGE
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


class PerformanceMonitor:
    """Monitors connector performance."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.start_times: Dict[str, float] = {}
    
    @contextmanager
    def time_operation(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager to time an operation."""
        start_time = time.time()
        self.start_times[operation_name] = start_time
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics_collector.add_metric(
                f"operation_duration_seconds",
                duration,
                MetricType.HISTOGRAM,
                labels={**(labels or {}), "operation": operation_name}
            )
            del self.start_times[operation_name]
    
    def record_workunit_processed(self, workunit_type: str) -> None:
        """Record that a workunit was processed."""
        self.metrics_collector.add_metric(
            "workunits_processed_total",
            1,
            MetricType.COUNTER,
            labels={"type": workunit_type}
        )
    
    def record_error(self, error_type: str, error_message: str) -> None:
        """Record an error."""
        self.metrics_collector.add_metric(
            "errors_total",
            1,
            MetricType.COUNTER,
            labels={"type": error_type, "message": error_message[:100]}
        )
    
    def record_data_extracted(self, data_type: str, count: int) -> None:
        """Record data extraction."""
        self.metrics_collector.add_metric(
            "data_extracted_total",
            count,
            MetricType.COUNTER,
            labels={"type": data_type}
        )


class MonitoringDashboard:
    """Simple monitoring dashboard."""
    
    def __init__(self, metrics_collector: MetricsCollector, 
                 health_checker: HealthChecker, port: int = 8080):
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker
        self.port = port
        self.server = None
    
    def start(self) -> None:
        """Start the monitoring dashboard."""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json
            
            class DashboardHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.metrics_collector = metrics_collector
                    self.health_checker = health_checker
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    if self.path == '/metrics':
                        self._handle_metrics()
                    elif self.path == '/health':
                        self._handle_health()
                    elif self.path == '/':
                        self._handle_dashboard()
                    else:
                        self.send_error(404)
                
                def _handle_metrics(self):
                    metrics = self.metrics_collector.get_metrics()
                    summary = self.metrics_collector.get_metric_summary()
                    
                    response = {
                        "metrics": [
                            {
                                "name": m.name,
                                "value": m.value,
                                "type": m.type,
                                "labels": m.labels,
                                "timestamp": m.timestamp.isoformat()
                            }
                            for m in metrics[-100:]  # Last 100 metrics
                        ],
                        "summary": summary
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, indent=2).encode())
                
                def _handle_health(self):
                    health_checks = self.health_checker.run_checks()
                    
                    overall_status = "healthy"
                    for check in health_checks:
                        if check.status == "unhealthy":
                            overall_status = "unhealthy"
                            break
                        elif check.status == "degraded" and overall_status == "healthy":
                            overall_status = "degraded"
                    
                    response = {
                        "status": overall_status,
                        "checks": [
                            {
                                "name": check.name,
                                "status": check.status,
                                "message": check.message,
                                "duration_ms": check.duration_ms
                            }
                            for check in health_checks
                        ]
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, indent=2).encode())
                
                def _handle_dashboard(self):
                    html = self._generate_dashboard_html()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                
                def _generate_dashboard_html(self):
                    return """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>DataGuild Snowflake Connector - Monitoring Dashboard</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            .metric { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
                            .healthy { color: green; }
                            .unhealthy { color: red; }
                            .degraded { color: orange; }
                        </style>
                    </head>
                    <body>
                        <h1>DataGuild Snowflake Connector - Monitoring Dashboard</h1>
                        <p><a href="/metrics">Metrics (JSON)</a> | <a href="/health">Health Check (JSON)</a></p>
                        <div id="content">
                            <p>Dashboard is running. Use the links above to view metrics and health status.</p>
                        </div>
                        <script>
                            setInterval(function() {
                                fetch('/health')
                                    .then(response => response.json())
                                    .then(data => {
                                        document.getElementById('content').innerHTML = 
                                            '<h2>Health Status: <span class="' + data.status + '">' + data.status + '</span></h2>' +
                                            '<ul>' + data.checks.map(check => 
                                                '<li>' + check.name + ': <span class="' + check.status + '">' + check.status + '</span> (' + check.duration_ms.toFixed(2) + 'ms)</li>'
                                            ).join('') + '</ul>';
                                    });
                            }, 5000);
                        </script>
                    </body>
                    </html>
                    """
            
            self.server = HTTPServer(('localhost', self.port), DashboardHandler)
            logger.info(f"Monitoring dashboard started on port {self.port}")
            self.server.serve_forever()
            
        except Exception as e:
            logger.error(f"Failed to start monitoring dashboard: {e}")
    
    def stop(self) -> None:
        """Stop the monitoring dashboard."""
        if self.server:
            self.server.shutdown()
            logger.info("Monitoring dashboard stopped")


# Health check functions
def check_snowflake_connection(connector) -> HealthCheck:
    """Check Snowflake connection health."""
    try:
        if hasattr(connector, 'connection') and connector.connection:
            # Try a simple query
            cursor = connector.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return HealthCheck(
                name="snowflake_connection",
                status="healthy",
                message="Connection is active"
            )
        else:
            return HealthCheck(
                name="snowflake_connection",
                status="unhealthy",
                message="No connection available"
            )
    except Exception as e:
        return HealthCheck(
            name="snowflake_connection",
            status="unhealthy",
            message=f"Connection failed: {str(e)}"
        )


def check_memory_usage() -> HealthCheck:
    """Check memory usage health."""
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            return HealthCheck(
                name="memory_usage",
                status="unhealthy",
                message=f"Memory usage is {memory.percent:.1f}%"
            )
        elif memory.percent > 80:
            return HealthCheck(
                name="memory_usage",
                status="degraded",
                message=f"Memory usage is {memory.percent:.1f}%"
            )
        else:
            return HealthCheck(
                name="memory_usage",
                status="healthy",
                message=f"Memory usage is {memory.percent:.1f}%"
            )
    except Exception as e:
        return HealthCheck(
            name="memory_usage",
            status="unhealthy",
            message=f"Failed to check memory: {str(e)}"
        )


def check_disk_space() -> HealthCheck:
    """Check disk space health."""
    try:
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            return HealthCheck(
                name="disk_space",
                status="unhealthy",
                message=f"Disk usage is {disk.percent:.1f}%"
            )
        elif disk.percent > 85:
            return HealthCheck(
                name="disk_space",
                status="degraded",
                message=f"Disk usage is {disk.percent:.1f}%"
            )
        else:
            return HealthCheck(
                name="disk_space",
                status="healthy",
                message=f"Disk usage is {disk.percent:.1f}%"
            )
    except Exception as e:
        return HealthCheck(
            name="disk_space",
            status="unhealthy",
            message=f"Failed to check disk space: {str(e)}"
        )

