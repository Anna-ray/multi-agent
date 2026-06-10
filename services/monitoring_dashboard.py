"""
Real-Time Monitoring Dashboard for Multi-Agent System

Provides live visualization and monitoring of:
- Agent performance metrics
- Incident processing pipeline
- System health and status
- Memory and learning statistics
- AI integration status
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """
    Advanced Monitoring Dashboard for Multi-Agent System.
    
    Features:
    - Real-time agent performance tracking
    - Incident pipeline visualization
    - System health monitoring
    - Alert management
    - Performance analytics
    - Trend analysis
    """
    
    def __init__(self):
        """Initialize the monitoring dashboard."""
        self.metrics: Dict[str, Any] = {
            "agents": {},
            "incidents": [],
            "system": {
                "start_time": datetime.now(timezone.utc).isoformat(),
                "total_messages": 0,
                "total_incidents": 0,
                "active_crisis_rooms": 0
            },
            "alerts": [],
            "performance": defaultdict(list)
        }
        
        logger.info("📊 Monitoring Dashboard initialized")
    
    def record_agent_action(
        self,
        agent_name: str,
        action_type: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record an agent action for monitoring.
        
        Args:
            agent_name: Name of the agent
            action_type: Type of action performed
            duration: Action duration in seconds
            success: Whether action succeeded
            metadata: Additional metadata
        """
        if agent_name not in self.metrics["agents"]:
            self.metrics["agents"][agent_name] = {
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "avg_duration": 0.0,
                "last_action": None,
                "action_history": []
            }
        
        agent_metrics = self.metrics["agents"][agent_name]
        agent_metrics["total_actions"] += 1
        
        if success:
            agent_metrics["successful_actions"] += 1
        else:
            agent_metrics["failed_actions"] += 1
        
        # Update average duration
        total = agent_metrics["total_actions"]
        agent_metrics["avg_duration"] = (
            (agent_metrics["avg_duration"] * (total - 1) + duration) / total
        )
        
        # Record action
        action_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "duration": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        agent_metrics["last_action"] = action_record
        agent_metrics["action_history"].append(action_record)
        
        # Keep only last 100 actions
        if len(agent_metrics["action_history"]) > 100:
            agent_metrics["action_history"] = agent_metrics["action_history"][-100:]
        
        # Check for performance issues
        if duration > 5.0:  # Slow action threshold
            self._create_alert(
                "performance",
                f"Slow action detected: {agent_name} - {action_type} took {duration:.2f}s",
                "warning"
            )
    
    def record_incident(
        self,
        incident_id: str,
        severity: str,
        status: str,
        agents_involved: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record incident processing for monitoring.
        
        Args:
            incident_id: Incident identifier
            severity: Incident severity
            status: Current status
            agents_involved: List of agents handling the incident
            metadata: Additional metadata
        """
        incident_record = {
            "incident_id": incident_id,
            "severity": severity,
            "status": status,
            "agents_involved": agents_involved,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.metrics["incidents"].append(incident_record)
        self.metrics["system"]["total_incidents"] += 1
        
        # Keep only last 1000 incidents
        if len(self.metrics["incidents"]) > 1000:
            self.metrics["incidents"] = self.metrics["incidents"][-1000:]
        
        # Create alert for critical incidents
        if severity.lower() == "critical":
            self._create_alert(
                "incident",
                f"Critical incident detected: {incident_id}",
                "critical"
            )
    
    def record_message(self, topic: str, source: str) -> None:
        """
        Record message bus activity.
        
        Args:
            topic: Message topic
            source: Message source
        """
        self.metrics["system"]["total_messages"] += 1
        
        # Track performance by topic
        self.metrics["performance"][topic].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source
        })
    
    def update_crisis_rooms(self, count: int) -> None:
        """
        Update active crisis room count.
        
        Args:
            count: Number of active crisis rooms
        """
        self.metrics["system"]["active_crisis_rooms"] = count
        
        if count > 5:  # High crisis room threshold
            self._create_alert(
                "capacity",
                f"High number of active crisis rooms: {count}",
                "warning"
            )
    
    def _create_alert(self, alert_type: str, message: str, severity: str) -> None:
        """
        Create a monitoring alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity
        """
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.metrics["alerts"].append(alert)
        
        # Keep only last 100 alerts
        if len(self.metrics["alerts"]) > 100:
            self.metrics["alerts"] = self.metrics["alerts"][-100:]
        
        logger.warning(f"🚨 ALERT [{severity.upper()}]: {message}")
    
    def get_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Performance metrics dictionary
        """
        if agent_name not in self.metrics["agents"]:
            return {
                "agent_name": agent_name,
                "status": "not_found",
                "total_actions": 0
            }
        
        agent_metrics = self.metrics["agents"][agent_name]
        
        success_rate = 0.0
        if agent_metrics["total_actions"] > 0:
            success_rate = (
                agent_metrics["successful_actions"] / agent_metrics["total_actions"]
            )
        
        return {
            "agent_name": agent_name,
            "status": "active",
            "total_actions": agent_metrics["total_actions"],
            "success_rate": round(success_rate, 3),
            "avg_duration": round(agent_metrics["avg_duration"], 3),
            "last_action": agent_metrics["last_action"]
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            System health metrics
        """
        total_agents = len(self.metrics["agents"])
        active_agents = sum(
            1 for agent in self.metrics["agents"].values()
            if agent["total_actions"] > 0
        )
        
        # Calculate overall success rate
        total_actions = sum(
            agent["total_actions"] for agent in self.metrics["agents"].values()
        )
        successful_actions = sum(
            agent["successful_actions"] for agent in self.metrics["agents"].values()
        )
        
        overall_success_rate = 0.0
        if total_actions > 0:
            overall_success_rate = successful_actions / total_actions
        
        # Determine health status
        health_status = "healthy"
        if overall_success_rate < 0.8:
            health_status = "degraded"
        if overall_success_rate < 0.5:
            health_status = "critical"
        
        return {
            "status": health_status,
            "uptime_seconds": self._calculate_uptime(),
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_messages": self.metrics["system"]["total_messages"],
            "total_incidents": self.metrics["system"]["total_incidents"],
            "active_crisis_rooms": self.metrics["system"]["active_crisis_rooms"],
            "overall_success_rate": round(overall_success_rate, 3),
            "recent_alerts": len([
                a for a in self.metrics["alerts"]
                if a["severity"] in ["critical", "warning"]
            ])
        }
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """
        Get incident processing statistics.
        
        Returns:
            Incident statistics
        """
        if not self.metrics["incidents"]:
            return {
                "total": 0,
                "by_severity": {},
                "by_status": {},
                "avg_agents_per_incident": 0.0
            }
        
        by_severity = defaultdict(int)
        by_status = defaultdict(int)
        total_agents = 0
        
        for incident in self.metrics["incidents"]:
            by_severity[incident["severity"]] += 1
            by_status[incident["status"]] += 1
            total_agents += len(incident["agents_involved"])
        
        return {
            "total": len(self.metrics["incidents"]),
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
            "avg_agents_per_incident": round(
                total_agents / len(self.metrics["incidents"]), 2
            )
        }
    
    def get_performance_trends(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance trends over time.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            Performance trend data
        """
        if agent_name:
            if agent_name not in self.metrics["agents"]:
                return {"error": "Agent not found"}
            
            history = self.metrics["agents"][agent_name]["action_history"]
            
            return {
                "agent_name": agent_name,
                "total_actions": len(history),
                "recent_actions": history[-10:],
                "success_trend": self._calculate_success_trend(history)
            }
        
        # Overall system trends
        all_actions = []
        for agent_metrics in self.metrics["agents"].values():
            all_actions.extend(agent_metrics["action_history"])
        
        all_actions.sort(key=lambda x: x["timestamp"])
        
        return {
            "total_actions": len(all_actions),
            "recent_actions": all_actions[-20:],
            "success_trend": self._calculate_success_trend(all_actions)
        }
    
    def _calculate_success_trend(self, actions: List[Dict[str, Any]]) -> List[float]:
        """Calculate success rate trend over time."""
        if not actions:
            return []
        
        # Calculate success rate in windows of 10 actions
        window_size = 10
        trends = []
        
        for i in range(0, len(actions), window_size):
            window = actions[i:i + window_size]
            if window:
                success_count = sum(1 for a in window if a["success"])
                trends.append(round(success_count / len(window), 2))
        
        return trends
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime in seconds."""
        start_time = datetime.fromisoformat(self.metrics["system"]["start_time"])
        now = datetime.now(timezone.utc)
        return (now - start_time).total_seconds()
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get system alerts.
        
        Args:
            severity: Optional severity filter
            
        Returns:
            List of alerts
        """
        alerts = self.metrics["alerts"]
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        
        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive monitoring report.
        
        Returns:
            Formatted report string
        """
        health = self.get_system_health()
        incident_stats = self.get_incident_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MULTI-AGENT SYSTEM MONITORING REPORT                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 SYSTEM HEALTH: {health['status'].upper()}
   • Uptime: {health['uptime_seconds']:.0f} seconds
   • Total Agents: {health['total_agents']} ({health['active_agents']} active)
   • Success Rate: {health['overall_success_rate']:.1%}
   • Messages Processed: {health['total_messages']}

🚨 INCIDENTS:
   • Total Processed: {incident_stats['total']}
   • Active Crisis Rooms: {health['active_crisis_rooms']}
   • By Severity: {json.dumps(incident_stats['by_severity'], indent=6)}
   • Avg Agents/Incident: {incident_stats['avg_agents_per_incident']}

⚠️  ALERTS:
   • Recent Alerts: {health['recent_alerts']}
   • Critical: {len([a for a in self.metrics['alerts'] if a['severity'] == 'critical'])}
   • Warnings: {len([a for a in self.metrics['alerts'] if a['severity'] == 'warning'])}

👥 AGENT PERFORMANCE:
"""
        
        for agent_name in self.metrics["agents"]:
            perf = self.get_agent_performance(agent_name)
            report += f"""
   • {agent_name}:
     - Actions: {perf['total_actions']}
     - Success Rate: {perf['success_rate']:.1%}
     - Avg Duration: {perf['avg_duration']:.3f}s
"""
        
        report += "\n" + "═" * 80 + "\n"
        
        return report
    
    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to export file
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"📁 Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def clear_metrics(self) -> None:
        """Clear all metrics (useful for testing)."""
        self.metrics = {
            "agents": {},
            "incidents": [],
            "system": {
                "start_time": datetime.now(timezone.utc).isoformat(),
                "total_messages": 0,
                "total_incidents": 0,
                "active_crisis_rooms": 0
            },
            "alerts": [],
            "performance": defaultdict(list)
        }
        logger.info("🧹 Metrics cleared")


# Global dashboard instance
_dashboard_instance = None


def get_dashboard() -> MonitoringDashboard:
    """Get or create the global dashboard instance."""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = MonitoringDashboard()
    return _dashboard_instance


# Made with Bob - Advanced Monitoring System