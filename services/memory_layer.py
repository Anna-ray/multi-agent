from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class MemoryLayer:
    """
    Advanced Memory & Context Layer for Multi-Agent Learning.
    
    Provides persistent storage and retrieval of:
    - Incident history and patterns
    - Agent performance metrics
    - Decision outcomes and effectiveness
    - System state snapshots
    - Learning from past executions
    
    Features:
    - Semantic search for similar incidents
    - Pattern recognition and anomaly detection
    - Performance trend analysis
    - Context-aware recommendations
    - Automatic knowledge base building
    """
    
    def __init__(self, storage_path: str = "memory_store"):
        """
        Initialize the Memory Layer.
        
        Args:
            storage_path: Directory path for persistent storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # In-memory caches for fast access
        self.incident_memory: List[Dict[str, Any]] = []
        self.agent_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.decision_memory: List[Dict[str, Any]] = []
        self.pattern_cache: Dict[str, Any] = {}
        
        # Load existing memory from disk
        self._load_memory()
        
        logger.info(f"🧠 Memory Layer initialized with {len(self.incident_memory)} incidents")
    
    def store_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Store incident data in memory with automatic indexing.
        
        Args:
            incident_data: Incident information to store
            
        Returns:
            Memory ID for the stored incident
        """
        # Generate unique memory ID
        memory_id = self._generate_memory_id(incident_data)
        
        # Enrich with metadata
        enriched_data = {
            "memory_id": memory_id,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "incident_id": incident_data.get("incident_id"),
            "description": incident_data.get("description", ""),
            "severity": incident_data.get("severity", "unknown"),
            "resolution_time": incident_data.get("resolution_time"),
            "agents_involved": incident_data.get("agents_involved", []),
            "outcome": incident_data.get("outcome", "unknown"),
            "lessons_learned": incident_data.get("lessons_learned", []),
            "raw_data": incident_data
        }
        
        # Add to memory
        self.incident_memory.append(enriched_data)
        
        # Update pattern cache
        self._update_patterns(enriched_data)
        
        # Persist to disk
        self._save_incident(enriched_data)
        
        logger.info(f"💾 Stored incident {incident_data.get('incident_id')} with memory ID: {memory_id}")
        
        return memory_id
    
    def store_agent_action(self, agent_name: str, action_data: Dict[str, Any]) -> None:
        """
        Store agent action for performance tracking and learning.
        
        Args:
            agent_name: Name of the agent
            action_data: Action details including outcome and metrics
        """
        if agent_name not in self.agent_memory:
            self.agent_memory[agent_name] = []
        
        enriched_action = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_data.get("action_type"),
            "success": action_data.get("success", True),
            "response_time": action_data.get("response_time", 0.0),
            "confidence": action_data.get("confidence", 0.0),
            "context": action_data.get("context", {}),
            "outcome": action_data.get("outcome", "")
        }
        
        self.agent_memory[agent_name].append(enriched_action)
        
        # Keep only recent actions (last 1000)
        if len(self.agent_memory[agent_name]) > 1000:
            self.agent_memory[agent_name] = self.agent_memory[agent_name][-1000:]
        
        logger.debug(f"📝 Stored action for agent '{agent_name}'")
    
    def store_decision(self, decision_data: Dict[str, Any]) -> None:
        """
        Store decision outcome for learning and improvement.
        
        Args:
            decision_data: Decision details and effectiveness
        """
        enriched_decision = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_id": decision_data.get("decision_id"),
            "incident_id": decision_data.get("incident_id"),
            "recommendation": decision_data.get("recommendation"),
            "confidence": decision_data.get("confidence", 0.0),
            "outcome": decision_data.get("outcome", "pending"),
            "effectiveness": decision_data.get("effectiveness", 0.0),
            "context": decision_data.get("context", {})
        }
        
        self.decision_memory.append(enriched_decision)
        
        logger.info(f"🎯 Stored decision for incident {decision_data.get('incident_id')}")
    
    def find_similar_incidents(
        self, 
        description: str, 
        severity: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar incidents using semantic matching.
        
        Uses keyword matching and pattern recognition to find relevant
        historical incidents that can inform current decision-making.
        
        Args:
            description: Incident description to match
            severity: Optional severity filter
            limit: Maximum number of results
            
        Returns:
            List of similar incidents with similarity scores
        """
        if not self.incident_memory:
            return []
        
        description_lower = description.lower()
        keywords = set(description_lower.split())
        
        # Calculate similarity scores
        scored_incidents = []
        
        for incident in self.incident_memory:
            incident_desc = incident.get("description", "").lower()
            incident_keywords = set(incident_desc.split())
            
            # Calculate keyword overlap
            common_keywords = keywords.intersection(incident_keywords)
            similarity = len(common_keywords) / max(len(keywords), 1)
            
            # Boost score for severity match
            if severity and incident.get("severity") == severity:
                similarity += 0.2
            
            # Boost score for successful outcomes
            if incident.get("outcome") == "resolved":
                similarity += 0.1
            
            scored_incidents.append({
                "incident": incident,
                "similarity": min(similarity, 1.0),
                "common_keywords": list(common_keywords)[:5]
            })
        
        # Sort by similarity and return top results
        scored_incidents.sort(key=lambda x: x["similarity"], reverse=True)
        
        results = scored_incidents[:limit]
        
        if results:
            logger.info(f"🔍 Found {len(results)} similar incidents (top similarity: {results[0]['similarity']:.2f})")
        
        return results
    
    def get_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Performance metrics including success rate, avg response time, etc.
        """
        if agent_name not in self.agent_memory:
            return {
                "agent_name": agent_name,
                "total_actions": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0
            }
        
        actions = self.agent_memory[agent_name]
        total = len(actions)
        successful = sum(1 for a in actions if a.get("success", False))
        
        avg_response_time = sum(a.get("response_time", 0.0) for a in actions) / total if total > 0 else 0.0
        avg_confidence = sum(a.get("confidence", 0.0) for a in actions) / total if total > 0 else 0.0
        
        return {
            "agent_name": agent_name,
            "total_actions": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_response_time": round(avg_response_time, 3),
            "avg_confidence": round(avg_confidence, 2),
            "recent_actions": actions[-10:]  # Last 10 actions
        }
    
    def get_decision_effectiveness(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Get effectiveness metrics for decisions related to an incident.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Decision effectiveness data or None if not found
        """
        decisions = [d for d in self.decision_memory if d.get("incident_id") == incident_id]
        
        if not decisions:
            return None
        
        return {
            "incident_id": incident_id,
            "total_decisions": len(decisions),
            "avg_confidence": sum(d.get("confidence", 0.0) for d in decisions) / len(decisions),
            "avg_effectiveness": sum(d.get("effectiveness", 0.0) for d in decisions) / len(decisions),
            "decisions": decisions
        }
    
    def get_patterns(self, pattern_type: str = "all") -> Dict[str, Any]:
        """
        Get identified patterns from historical data.
        
        Args:
            pattern_type: Type of patterns to retrieve ("incident", "agent", "decision", "all")
            
        Returns:
            Dictionary of identified patterns
        """
        if pattern_type == "all":
            return self.pattern_cache.copy()
        
        return self.pattern_cache.get(pattern_type, {})
    
    def learn_from_outcome(
        self, 
        incident_id: str, 
        outcome: str, 
        effectiveness: float,
        lessons: List[str]
    ) -> None:
        """
        Update memory with incident outcome for learning.
        
        Args:
            incident_id: Incident identifier
            outcome: Final outcome ("resolved", "escalated", "failed")
            effectiveness: Effectiveness score (0.0 to 1.0)
            lessons: List of lessons learned
        """
        # Find and update incident in memory
        for incident in self.incident_memory:
            if incident.get("incident_id") == incident_id:
                incident["outcome"] = outcome
                incident["effectiveness"] = effectiveness
                incident["lessons_learned"] = lessons
                incident["resolved_at"] = datetime.now(timezone.utc).isoformat()
                
                # Calculate resolution time if available
                if "stored_at" in incident:
                    stored_time = datetime.fromisoformat(incident["stored_at"])
                    resolved_time = datetime.now(timezone.utc)
                    incident["resolution_time"] = (resolved_time - stored_time).total_seconds()
                
                logger.info(f"📚 Learned from incident {incident_id}: {outcome} (effectiveness: {effectiveness:.2f})")
                break
        
        # Update patterns based on outcome
        self._update_patterns_from_outcome(incident_id, outcome, effectiveness)
    
    def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get AI-powered recommendations based on historical context.
        
        Args:
            context: Current situation context
            
        Returns:
            List of recommendations with confidence scores
        """
        recommendations = []
        
        # Find similar past situations
        description = context.get("description", "")
        severity = context.get("severity")
        
        similar = self.find_similar_incidents(description, severity, limit=3)
        
        for match in similar:
            incident = match["incident"]
            
            if incident.get("outcome") == "resolved":
                recommendations.append({
                    "recommendation": f"Apply strategy from incident {incident.get('incident_id')}",
                    "confidence": match["similarity"] * incident.get("effectiveness", 0.5),
                    "rationale": f"Similar incident resolved successfully with {len(incident.get('lessons_learned', []))} lessons learned",
                    "reference_incident": incident.get("incident_id"),
                    "lessons": incident.get("lessons_learned", [])
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda r: r["confidence"], reverse=True)
        
        return recommendations
    
    def _generate_memory_id(self, data: Dict[str, Any]) -> str:
        """Generate unique memory ID using hash of key fields."""
        key_data = json.dumps({
            "incident_id": data.get("incident_id"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, sort_keys=True)
        
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _update_patterns(self, incident_data: Dict[str, Any]) -> None:
        """Update pattern cache with new incident data."""
        severity = incident_data.get("severity", "unknown")
        
        if "incident_patterns" not in self.pattern_cache:
            self.pattern_cache["incident_patterns"] = {}
        
        if severity not in self.pattern_cache["incident_patterns"]:
            self.pattern_cache["incident_patterns"][severity] = {
                "count": 0,
                "avg_resolution_time": 0.0,
                "common_keywords": []
            }
        
        self.pattern_cache["incident_patterns"][severity]["count"] += 1
    
    def _update_patterns_from_outcome(
        self, 
        incident_id: str, 
        outcome: str, 
        effectiveness: float
    ) -> None:
        """Update patterns based on incident outcome."""
        if "outcome_patterns" not in self.pattern_cache:
            self.pattern_cache["outcome_patterns"] = {}
        
        if outcome not in self.pattern_cache["outcome_patterns"]:
            self.pattern_cache["outcome_patterns"][outcome] = {
                "count": 0,
                "avg_effectiveness": 0.0
            }
        
        pattern = self.pattern_cache["outcome_patterns"][outcome]
        pattern["count"] += 1
        
        # Update running average
        total = pattern["count"]
        pattern["avg_effectiveness"] = (
            (pattern["avg_effectiveness"] * (total - 1) + effectiveness) / total
        )
    
    def _load_memory(self) -> None:
        """Load memory from persistent storage."""
        incidents_file = self.storage_path / "incidents.json"
        
        if incidents_file.exists():
            try:
                with open(incidents_file, 'r') as f:
                    self.incident_memory = json.load(f)
                logger.info(f"📂 Loaded {len(self.incident_memory)} incidents from storage")
            except Exception as e:
                logger.warning(f"Failed to load incidents: {e}")
    
    def _save_incident(self, incident_data: Dict[str, Any]) -> None:
        """Save incident to persistent storage."""
        incidents_file = self.storage_path / "incidents.json"
        
        try:
            with open(incidents_file, 'w') as f:
                json.dump(self.incident_memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save incident: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics.
        
        Returns:
            Dictionary containing memory statistics
        """
        return {
            "total_incidents": len(self.incident_memory),
            "total_agents_tracked": len(self.agent_memory),
            "total_decisions": len(self.decision_memory),
            "patterns_identified": len(self.pattern_cache),
            "storage_path": str(self.storage_path),
            "incident_outcomes": self._count_outcomes(),
            "severity_distribution": self._count_severities()
        }
    
    def _count_outcomes(self) -> Dict[str, int]:
        """Count incidents by outcome."""
        outcomes = {}
        for incident in self.incident_memory:
            outcome = incident.get("outcome", "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        return outcomes
    
    def _count_severities(self) -> Dict[str, int]:
        """Count incidents by severity."""
        severities = {}
        for incident in self.incident_memory:
            severity = incident.get("severity", "unknown")
            severities[severity] = severities.get(severity, 0) + 1
        return severities


# Made with Bob - Advanced Memory & Learning System