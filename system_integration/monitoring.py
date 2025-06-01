"""
System monitoring for Manus AI Clone
Implements comprehensive system health monitoring
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable

class SystemMetric:
    """
    Represents a system metric with time series data
    """
    def __init__(self, 
                 name: str,
                 description: str = "",
                 unit: str = "count",
                 aggregation: str = "sum"):
        self.name = name
        self.description = description
        self.unit = unit
        self.aggregation = aggregation
        self.data_points = []  # type: List[Dict[str, Any]]
        self.last_updated = None

    def add_data_point(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """
        Add a new data point to the metric
        
        Args:
            value: Metric value
            timestamp: Time of measurement (defaults to now)
        """
        timestamp = timestamp or datetime.now()
        self.data_points.append({
            "timestamp": timestamp.isoformat(),
            "value": value
        })
        self.last_updated = timestamp.isoformat()

    def get_data_points(self, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get data points within specified time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of matching data points
        """
        # If no time range, return all
        if not start_time and not end_time:
            return self.data_points
            
        # Parse start and end times
        start_ts = start_time.isoformat() if start_time else None
        end_ts = end_time.isoformat() if end_time else None
        
        # Filter data points by time
        result = []
        for point in self.data_points:
            if start_ts and point["timestamp"] < start_ts:
                continue
            if end_ts and point["timestamp"] > end_ts:
                continue
            result.append(point)
            
        return result

    def aggregate_data(self, 
                      window: str = "hourly",
                      function: str = "sum") -> Dict[str, Any]:
        """
        Aggregate data points based on window and function
        
        Args:
            window: Aggregation window (hourly, daily, weekly)
            function: Aggregation function (sum, avg, min, max)
            
        Returns:
            Dictionary with aggregated results
        """
        # Would implement actual aggregation logic in real use
        return {
            "window": window,
            "function": function,
            "result": [ 
                { "time": "now", "value": len(self.data_points) } 
            ]
        }

    def clear_data(self) -> None:
        """Clear all data points"""
        self.data_points = []
        self.last_updated = None


class ComponentHealth:
    """
    Health status for a component
    """
    def __init__(self, 
                 component_name: str,
                 status: str = "healthy",
                 score: float = 1.0,
                 last_checked: Optional[datetime] = None):
        self.component_name = component_name
        self.status = status
        self.score = score
        self.last_checked = last_checked or datetime.now().isoformat()
        self.failures = []  # type: List[Dict[str, Any]]
        self.restarts = 0

    def add_failure(self, error: str) -> None:
        """
        Record a component failure
        
        Args:
            error: Description of error
        """
        self.failures.append({
            "timestamp": datetime.now().isoformat(),
            "error": error
        })
        
        # Update status based on failures
        if len(self.failures) > 3:
            self.status = "unhealthy"
            self.score = max(0.1, self.score - 0.2)

    def record_restart(self) -> None:
        """Record a component restart"""
        self.restarts += 1
        self.status = "recovering"
        self.score = min(1.0, self.score + 0.3)

    def check_health(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            "component": self.component_name,
            "status": self.status,
            "health_score": self.score,
            "last_checked": self.last_checked,
            "failures": self.failures,
            "restarts": self.restarts
        }


class SystemMonitor:
    """
    Central system monitoring with health checks
    """
    def __init__(self):
        # Component health metrics
        self.health_metrics = {}  # type: Dict[str, ComponentHealth]
        
        # Performance metrics
        self.performance_metrics = {}  # type: Dict[str, SystemMetric]
        
        # Alert handlers
        self.alert_handlers = []  # type: List[Callable[[Dict[str, Any]], None]]
        
        # Monitoring configuration
        self.monitoring_interval = 60  # seconds
        self.alert_threshold = 0.5  # health score threshold
        self.log_level = 3  # Default severity level

    def register_component(self, name: str) -> None:
        """
        Register a component for monitoring
        
        Args:
            name: Name of component
        """
        if name not in self.health_metrics:
            self.health_metrics[name] = ComponentHealth(name)
            
        if name not in self.performance_metrics:
            self.performance_metrics[name] = SystemMetric(
                name=f"{name}_performance",
                description="Component performance metrics",
                unit="ms",
                aggregation="avg"
            )

    def add_metric_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a handler for processing metrics
        
        Args:
            handler: Function to call for each metric
        """
        self.metric_handlers.append(handler)

    def remove_metric_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a metric handler
        
        Args:
            handler: Handler function to remove
        """
        if handler in self.metric_handlers:
            self.metric_handlers.remove(handler)

    def log_performance(self, 
                       component: str,
                       duration: float,
                       operation: str = "unknown") -> None:
        """
        Log performance metric for a component
        
        Args:
            component: Component name
            duration: Duration in milliseconds
            operation: Operation type
        """
        # Register component if needed
        if component not in self.health_metrics:
            self.register_component(component)
            
        # Create metric key
        metric_key = f"{component}_{operation}"
        
        # Create metric if needed
        if metric_key not in self.performance_metrics:
            self.performance_metrics[metric_key] = SystemMetric(
                name=metric_key,
                description=f"{component} {operation} performance",
                unit="ms",
                aggregation="avg"
            )
            
        # Add data point
        self.performance_metrics[metric_key].add_data_point(duration)
        
        # Notify handlers
        self._notify_metric_handlers(metric_key, duration)

    def _notify_metric_handlers(self, metric_key: str, value: float) -> None:
        """
        Notify metric handlers about new metric data
        
        Args:
            metric_key: Key of metric
            value: New metric value
        """
        # In real implementation would notify handlers
        pass

    def check_component_health(self, component: str) -> Dict[str, Any]:
        """
        Check health of a specific component
        
        Args:
            component: Component name
            
        Returns:
            Health information
        """
        # Would perform actual health checks in real implementation
        if component in self.health_metrics:
            return self.health_metrics[component].check_health()
            
        return {
            "component": component,
            "status": "unknown",
            "error": "Component not registered"
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        # Calculate overall health
        total_components = len(self.health_metrics)
        healthy_count = sum(1 for h in self.health_metrics.values() if h.status == "healthy")
        
        # Build component health info
        components_health = {
            name: health.check_health() 
            for name, health in self.health_metrics.items()
        }
        
        # Determine system status
        system_status = "healthy"
        if healthy_count / total_components < 0.7:
            system_status = "critical"
        elif healthy_count / total_components < 0.9:
            system_status = "degraded"
            
        return {
            "status": system_status,
            "overall_health_score": healthy_count / total_components if total_components else 1.0,
            "total_components": total_components,
            "healthy_components": healthy_count,
            "components": components_health,
            "last_checked": datetime.now().isoformat()
        }

    def get_performance_trend(self, component: str) -> Dict[str, Any]:
        """
        Get performance trend for a component
        
        Args:
            component: Component name
            
        Returns:
            Trend analysis
        """
        # Would analyze actual data in real implementation
        return {
            "component": component,
            "trend": "stable",
            "average": 0,
            "max": 0,
            "min": 0,
            "percentile_95": 0,
            "last_week_changes": [],
            "last_checked": datetime.now().isoformat()
        }

    def set_alert_threshold(self, threshold: float) -> None:
        """
        Set threshold for alert generation
        
        Args:
            threshold: Health score threshold for alerts
        """
        self.alert_threshold = max(0.0, min(1.0, threshold))

    def add_alert_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add an alert handler
        
        Args:
            handler: Function to call when alert is triggered
        """
        self.alert_handlers.append(handler)

    def remove_alert_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove an alert handler
        
        Args:
            handler: Handler function to remove
        """
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)

    def trigger_alert(self, 
                     severity: int,
                     message: str,
                     context: Dict[str, Any]) -> str:
        """
        Trigger an alert event
        
        Args:
            severity: Alert severity (1-5)
            message: Alert message
            context: Additional context
            
        Returns:
            ID of created alert
        """
        # Generate alert ID
        alert_id = str(uuid.uuid4())
        
        # Build alert details
        alert = {
            "alert_id": alert_id,
            "severity": severity,
            "message": message,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "handled": False
        }
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                # Don't let handler errors affect main flow
                pass
                
        return alert_id

    def monitor_component(self, 
                        component: str,
                        check_function: Callable[[], bool],
                        interval: int = 60) -> None:
        """
        Monitor a component with custom check function
        
        Args:
            component: Component name
            check_function: Function that returns True if healthy
            interval: Check interval in seconds
        """
        # Register component if needed
        if component not in self.health_metrics:
            self.register_component(component)
            
        # Perform health check
        try:
            is_healthy = check_function()
            
            # Update health metrics
            health_info = self.health_metrics[component]
            health_info.last_checked = datetime.now().isoformat()
            
            if is_healthy:
                health_info.status = "healthy"
                health_info.score = 1.0
            else:
                health_info.add_failure("Component failed health check")
                health_info.status = "unhealthy"
                health_info.score = max(0.1, health_info.score - 0.2)
                
                # Trigger alert if below threshold
                if health_info.score <= self.alert_threshold:
                    self.trigger_alert(
                        severity=3,
                        message=f"Component {component} is unhealthy",
                        context={
                            "component": component,
                            "current_status": health_info.status,
                            "score": health_info.score,
                            "last_check": health_info.last_checked
                        }
                    )
                    
        except Exception as e:
            # Record exception as failure
            self.health_metrics[component].add_failure(str(e))
            
            # Trigger alert if below threshold
            if self.health_metrics[component].score <= self.alert_threshold:
                self.trigger_alert(
                    severity=4,
                    message=f"Component {component} error: {str(e)}",
                    context={
                        "component": component,
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
                )
                
    def get_component_diagnostics(self, component: str) -> Dict[str, Any]:
        """
        Get diagnostic information for a component
        
        Args:
            component: Component name
            
        Returns:
            Diagnostic report
        """
        # Would collect actual diagnostics in real implementation
        return {
            "component": component,
            "health": self.check_component_health(component),
            "performance": self.get_performance_trend(component),
            "configuration": self._get_component_config(component),
            "dependencies": self._get_component_dependencies(component),
            "last_checked": datetime.now().isoformat()
        }

    def _get_component_config(self, component: str) -> Dict[str, Any]:
        """
        Get component configuration
        
        Args:
            component: Component name
            
        Returns:
            Configuration details
        """
        # Would retrieve actual config in real implementation
        return {
            "component": component,
            "configured": True,
            "settings": {}
        }

    def _get_component_dependencies(self, component: str) -> Dict[str, Any]:
        """
        Get component dependencies
        
        Args:
            component: Component name
            
        Returns:
            Dependency information
        """
        # Would analyze actual dependencies in real implementation
        return {
            "component": component,
            "dependencies": [],
            "dependency_status": "healthy"
        }

    def start_monitoring(self) -> None:
        """Start continuous system monitoring"""
        # Would start background monitoring thread in real implementation
        pass

    def stop_monitoring(self) -> None:
        """Stop continuous system monitoring"""
        # Would stop background monitoring thread in real implementation
        pass

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Generate complete system diagnostic report"""
        # Collect health information
        health_info = self.get_system_health()
        
        # Collect performance metrics
        performance_info = self._collect_performance_metrics()
        
        # Collect detailed diagnostics
        diagnostics = {
            comp: self.get_component_diagnostics(comp) 
            for comp in self.health_metrics.keys()
        }
        
        return {
            "system_health": health_info,
            "performance_metrics": performance_info,
            "component_diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations(health_info, performance_info)
        }

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from all components"""
        # Would collect actual metrics in real implementation
        return {
            "total_operations": 0,
            "avg_response_time": 0,
            "success_rate": 1.0,
            "last_checked": datetime.now().isoformat()
        }

    def _generate_recommendations(self, 
                               health_info: Dict[str, Any],
                               performance_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on system health
        
        Args:
            health_info: System health information
            performance_info: Performance metrics
            
        Returns:
            List of recommendations
        """
        # Would generate actual recommendations in real implementation
        return [{
            "priority": 1,
            "action": "Continue monitoring",
            "description": "No critical issues detected",
            "impact": "low"
        }]

    def log_event(self, 
                 event_type: str,
                 message: str,
                 component: str,
                 duration: Optional[float] = None) -> None:
        """
        Log an event with optional performance metric
        
        Args:
            event_type: Type of event
            message: Event description
            component: Component involved
            duration: Optional duration metric
        """
        # Register component if needed
        if component not in self.health_metrics:
            self.register_component(component)
            
        # Log performance if provided
        if duration is not None:
            self.log_performance(component, duration, event_type)
            
        # Record event
        if hasattr(self, "audit_logger"):
            self.audit_logger.log_event(
                event_type=event_type,
                message=message,
                context={"component": component},
                operation={
                    "type": event_type,
                    "component": component
                },
                severity=2,
                category="system"
            )

    def set_audit_logger(self, logger: Any) -> None:
        """
        Set audit logger for event logging
        
        Args:
            logger: Audit logger instance
        """
        self.audit_logger = logger

    def get_health_statistics(self) -> Dict[str, Any]:
        """Get statistics about component health"""
        # Count health statuses
        status_counts = {
            "healthy": 0,
            "unhealthy": 0,
            "degraded": 0,
            "unknown": 0
        }
        
        # Count component statuses
        for health in self.health_metrics.values():
            status_counts[health.status] += 1
            
        # Calculate health score
        total = len(self.health_metrics)
        healthy = status_counts["healthy"]
        degraded = status_counts["degraded"]
        
        health_score = 1.0
        if total > 0:
            health_score = (healthy * 1.0 + (degraded * 0.5)) / total
            
        return {
            "total_components": total,
            "healthy_components": status_counts["healthy"],
            "unhealthy_components": status_counts["unhealthy"],
            "degraded_components": status_counts["degraded"],
            "health_score": health_score,
            "last_checked": datetime.now().isoformat()
        }

    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics across all components"""
        # Calculate average response time
        total = 0
        count = 0
        
        # For real implementation, would process actual metrics
        avg_response_time = 0
        
        return {
            "total_operations": count,
            "average_response_time": avg_response_time,
            "performance_trend": "stable",
            "last_checked": datetime.now().isoformat()
        }

    def configure_alert(self, 
                      severity: int,
                      handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Configure alert handling for specific severity
        
        Args:
            severity: Severity level (1-5)
            handler: Function to handle alerts
        """
        # Would implement severity-based handlers in real code
        self.add_alert_handler(handler)

    def create_dashboard_data(self) -> Dict[str, Any]:
        """Create dashboard-ready data for UI"""
        return {
            "system_health": self.get_system_health(),
            "performance": self.get_performance_statistics(),
            "alerts": self._get_active_alerts(),
            "diagnostics": self.get_diagnostic_report(),
            "last_updated": datetime.now().isoformat()
        }

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        # Would return actual active alerts in real implementation
        return []