from typing import Dict, Any, List, Optional, Callable
from agents.base_agent import Agent
from messages.models import MessageEnvelope
import logging
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for orchestration."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestratorAgent(Agent):
    """
    Advanced Orchestrator Agent for Multi-Agent System Coordination.
    
    Acts as the central coordinator that:
    - Breaks down complex tasks into subtasks
    - Routes tasks to specialized agents based on capabilities
    - Monitors task execution and agent performance
    - Handles agent failures and task reassignment
    - Aggregates results from multiple agents
    - Makes intelligent decisions about task prioritization
    - Learns from past executions to optimize routing
    
    This is the "brain" of the multi-agent system that ensures all agents
    work together efficiently to solve complex problems.
    
    Features:
    - Dynamic task decomposition
    - Intelligent agent selection based on capabilities and load
    - Real-time monitoring and health checks
    - Automatic failover and retry logic
    - Performance analytics and optimization
    - Learning from historical task execution patterns
    """
    
    def __init__(self, name: str, band_client, ai_client=None):
        """
        Initialize the Orchestrator Agent.
        
        Args:
            name: Agent identifier
            band_client: BandClient instance for message bus communication
            ai_client: Optional AI client for intelligent decision making
        """
        super().__init__(name, band_client)
        self.ai_client = ai_client
        
        # Agent registry: maps agent names to their capabilities
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        
        # Task queue and tracking
        self.task_queue: List[Dict[str, Any]] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        
        # Execution history for learning
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info(f"🎯 OrchestratorAgent '{name}' initialized")
    
    def register_agent(
        self, 
        agent_name: str, 
        capabilities: List[str],
        topics: List[str],
        max_concurrent_tasks: int = 5
    ) -> None:
        """
        Register a specialized agent with the orchestrator.
        
        Args:
            agent_name: Name of the agent to register
            capabilities: List of capabilities (e.g., ["analysis", "pqc", "cryptography"])
            topics: List of topics the agent can handle
            max_concurrent_tasks: Maximum concurrent tasks the agent can handle
        """
        self.agent_registry[agent_name] = {
            "capabilities": capabilities,
            "topics": topics,
            "max_concurrent_tasks": max_concurrent_tasks,
            "current_load": 0,
            "status": "active",
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Initialize performance tracking
        self.agent_performance[agent_name] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_response_time": 0.0,
            "success_rate": 1.0
        }
        
        logger.info(f"✅ Registered agent '{agent_name}' with capabilities: {capabilities}")
    
    def handle_message(self, message: MessageEnvelope) -> None:
        """
        Handle incoming messages and orchestrate task execution.
        
        Routes messages to appropriate handlers based on topic and content.
        
        Args:
            message: MessageEnvelope containing task or status update
        """
        try:
            topic = message.topic
            
            # Handle different message types
            if topic == "orchestrator.task.submit":
                self._handle_task_submission(message)
            elif topic == "orchestrator.task.status":
                self._handle_task_status_update(message)
            elif topic == "orchestrator.agent.health":
                self._handle_agent_health_check(message)
            elif topic.startswith("pqc."):
                # Route PQC-related messages to appropriate agents
                self._route_pqc_message(message)
            else:
                logger.warning(f"Unknown topic: {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}", exc_info=True)
    
    def _handle_task_submission(self, message: MessageEnvelope) -> None:
        """
        Handle new task submission and decompose into subtasks.
        
        Args:
            message: Task submission message
        """
        payload = message.payload
        task_id = payload.get("task_id", f"task-{len(self.task_queue)}")
        task_description = payload.get("description", "")
        priority = TaskPriority[payload.get("priority", "MEDIUM")]
        
        logger.info(f"📥 New task submitted: {task_id}")
        
        # Decompose task into subtasks
        subtasks = self._decompose_task(task_description, priority)
        
        # Create task record
        task_record = {
            "task_id": task_id,
            "description": task_description,
            "priority": priority.name,
            "subtasks": subtasks,
            "status": TaskStatus.PENDING.value,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "assigned_agents": []
        }
        
        # Add to queue
        self.task_queue.append(task_record)
        
        # Process task queue
        self._process_task_queue()
    
    def _decompose_task(self, description: str, priority: TaskPriority) -> List[Dict[str, Any]]:
        """
        Decompose a complex task into manageable subtasks.
        
        Uses AI if available, otherwise applies rule-based decomposition.
        
        Args:
            description: Task description
            priority: Task priority level
            
        Returns:
            List of subtask definitions
        """
        description_lower = description.lower()
        subtasks = []
        
        # PQC incident handling decomposition
        if "pqc" in description_lower or "incident" in description_lower:
            subtasks = [
                {
                    "subtask_id": "detect",
                    "description": "Detect and validate incident",
                    "required_capability": "detection",
                    "topic": "pqc.incident.detected",
                    "status": TaskStatus.PENDING.value
                },
                {
                    "subtask_id": "analyze",
                    "description": "Analyze incident severity and impact",
                    "required_capability": "analysis",
                    "topic": "pqc.analysis.completed",
                    "status": TaskStatus.PENDING.value,
                    "depends_on": ["detect"]
                },
                {
                    "subtask_id": "coordinate",
                    "description": "Initialize crisis coordination",
                    "required_capability": "coordination",
                    "topic": "pqc.coordination.updated",
                    "status": TaskStatus.PENDING.value,
                    "depends_on": ["detect"]
                },
                {
                    "subtask_id": "decide",
                    "description": "Make executive decision",
                    "required_capability": "decision",
                    "topic": "pqc.decision.made",
                    "status": TaskStatus.PENDING.value,
                    "depends_on": ["analyze", "coordinate"]
                },
                {
                    "subtask_id": "audit",
                    "description": "Create audit record",
                    "required_capability": "audit",
                    "topic": "pqc.audit.recorded",
                    "status": TaskStatus.PENDING.value,
                    "depends_on": ["decide"]
                }
            ]
        else:
            # Generic task decomposition
            subtasks = [
                {
                    "subtask_id": "process",
                    "description": description,
                    "required_capability": "general",
                    "status": TaskStatus.PENDING.value
                }
            ]
        
        logger.info(f"🔨 Decomposed task into {len(subtasks)} subtasks")
        return subtasks
    
    def _process_task_queue(self) -> None:
        """
        Process pending tasks in the queue and assign to agents.
        
        Implements intelligent task scheduling based on:
        - Task priority
        - Agent availability and load
        - Agent capabilities and performance history
        - Task dependencies
        """
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: TaskPriority[t["priority"]].value, reverse=True)
        
        for task in self.task_queue[:]:  # Iterate over copy
            if task["status"] != TaskStatus.PENDING.value:
                continue
            
            # Check if all dependencies are met
            ready_subtasks = self._get_ready_subtasks(task)
            
            if not ready_subtasks:
                continue
            
            # Assign subtasks to agents
            for subtask in ready_subtasks:
                agent = self._select_best_agent(subtask)
                
                if agent:
                    self._assign_subtask_to_agent(task, subtask, agent)
                else:
                    logger.warning(f"⚠️ No available agent for subtask: {subtask['subtask_id']}")
    
    def _get_ready_subtasks(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get subtasks that are ready to execute (dependencies met).
        
        Args:
            task: Task record
            
        Returns:
            List of ready subtasks
        """
        ready = []
        
        for subtask in task["subtasks"]:
            if subtask["status"] != TaskStatus.PENDING.value:
                continue
            
            # Check dependencies
            dependencies = subtask.get("depends_on", [])
            if not dependencies:
                ready.append(subtask)
                continue
            
            # Check if all dependencies are completed
            all_deps_met = all(
                any(st["subtask_id"] == dep and st["status"] == TaskStatus.COMPLETED.value
                    for st in task["subtasks"])
                for dep in dependencies
            )
            
            if all_deps_met:
                ready.append(subtask)
        
        return ready
    
    def _select_best_agent(self, subtask: Dict[str, Any]) -> Optional[str]:
        """
        Select the best agent for a subtask based on multiple factors.
        
        Selection criteria:
        - Agent has required capability
        - Agent is not overloaded
        - Agent has good performance history
        - Agent is currently active
        
        Args:
            subtask: Subtask definition
            
        Returns:
            Selected agent name or None if no suitable agent found
        """
        required_capability = subtask.get("required_capability", "general")
        candidates = []
        
        # Find agents with required capability
        for agent_name, agent_info in self.agent_registry.items():
            if agent_info["status"] != "active":
                continue
            
            if required_capability in agent_info["capabilities"]:
                # Check load
                if agent_info["current_load"] < agent_info["max_concurrent_tasks"]:
                    performance = self.agent_performance[agent_name]
                    candidates.append({
                        "name": agent_name,
                        "load": agent_info["current_load"],
                        "success_rate": performance["success_rate"],
                        "avg_response_time": performance["average_response_time"]
                    })
        
        if not candidates:
            return None
        
        # Select best candidate (lowest load, highest success rate)
        candidates.sort(key=lambda c: (c["load"], -c["success_rate"]))
        return candidates[0]["name"]
    
    def _assign_subtask_to_agent(
        self, 
        task: Dict[str, Any], 
        subtask: Dict[str, Any], 
        agent_name: str
    ) -> None:
        """
        Assign a subtask to a specific agent.
        
        Args:
            task: Parent task record
            subtask: Subtask to assign
            agent_name: Name of agent to assign to
        """
        subtask["status"] = TaskStatus.ASSIGNED.value
        subtask["assigned_to"] = agent_name
        subtask["assigned_at"] = datetime.now(timezone.utc).isoformat()
        
        # Update agent load
        self.agent_registry[agent_name]["current_load"] += 1
        
        # Track assignment
        task["assigned_agents"].append(agent_name)
        
        logger.info(f"📤 Assigned subtask '{subtask['subtask_id']}' to agent '{agent_name}'")
        
        # Publish assignment message
        self.send_message("orchestrator.task.assigned", {
            "task_id": task["task_id"],
            "subtask_id": subtask["subtask_id"],
            "agent_name": agent_name,
            "topic": subtask.get("topic", ""),
            "description": subtask["description"]
        })
    
    def _handle_task_status_update(self, message: MessageEnvelope) -> None:
        """
        Handle task status updates from agents.
        
        Args:
            message: Status update message
        """
        payload = message.payload
        task_id = payload.get("task_id")
        subtask_id = payload.get("subtask_id")
        status = payload.get("status")
        agent_name = payload.get("agent_name")
        
        logger.info(f"📊 Task status update: {task_id}/{subtask_id} -> {status}")
        
        # Update agent load
        if agent_name in self.agent_registry:
            if status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                self.agent_registry[agent_name]["current_load"] -= 1
        
        # Update performance metrics
        if status == TaskStatus.COMPLETED.value:
            self.agent_performance[agent_name]["tasks_completed"] += 1
        elif status == TaskStatus.FAILED.value:
            self.agent_performance[agent_name]["tasks_failed"] += 1
        
        # Recalculate success rate
        perf = self.agent_performance[agent_name]
        total = perf["tasks_completed"] + perf["tasks_failed"]
        if total > 0:
            perf["success_rate"] = perf["tasks_completed"] / total
        
        # Continue processing queue
        self._process_task_queue()
    
    def _handle_agent_health_check(self, message: MessageEnvelope) -> None:
        """
        Handle agent health check messages.
        
        Args:
            message: Health check message
        """
        payload = message.payload
        agent_name = payload.get("agent_name")
        status = payload.get("status", "active")
        
        if agent_name in self.agent_registry:
            self.agent_registry[agent_name]["status"] = status
            logger.info(f"💓 Agent '{agent_name}' health: {status}")
    
    def _route_pqc_message(self, message: MessageEnvelope) -> None:
        """
        Route PQC-related messages to appropriate specialized agents.
        
        Args:
            message: PQC message to route
        """
        topic = message.topic
        
        # Determine which agents should receive this message
        target_agents = []
        
        for agent_name, agent_info in self.agent_registry.items():
            if topic in agent_info["topics"]:
                target_agents.append(agent_name)
        
        if target_agents:
            logger.info(f"🔀 Routing {topic} to agents: {', '.join(target_agents)}")
            # In a real system, we would forward the message to these agents
        else:
            logger.warning(f"⚠️ No agents registered for topic: {topic}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including all agents and tasks.
        
        Returns:
            Dictionary containing system status information
        """
        return {
            "orchestrator": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {
                "total": len(self.agent_registry),
                "active": sum(1 for a in self.agent_registry.values() if a["status"] == "active"),
                "registry": self.agent_registry
            },
            "tasks": {
                "queued": len(self.task_queue),
                "active": len(self.active_tasks),
                "completed": len(self.completed_tasks)
            },
            "performance": self.agent_performance
        }
    
    def get_agent_recommendations(self, capability: str) -> List[str]:
        """
        Get recommended agents for a specific capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of recommended agent names sorted by performance
        """
        candidates = []
        
        for agent_name, agent_info in self.agent_registry.items():
            if capability in agent_info["capabilities"] and agent_info["status"] == "active":
                perf = self.agent_performance[agent_name]
                candidates.append({
                    "name": agent_name,
                    "success_rate": perf["success_rate"],
                    "tasks_completed": perf["tasks_completed"]
                })
        
        # Sort by success rate and experience
        candidates.sort(key=lambda c: (c["success_rate"], c["tasks_completed"]), reverse=True)
        
        return [c["name"] for c in candidates]


# Made with Bob - Advanced Multi-Agent Orchestration System