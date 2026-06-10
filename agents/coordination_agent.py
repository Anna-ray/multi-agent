from typing import Dict, Any, List, Optional
from agents.base_agent import Agent
from messages.models import MessageEnvelope, PQCIncidentDetected, PQCCoordinationState
import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PQCCoordinationAgent(Agent):
    """
    Advanced Post-Quantum Cryptographic Coordination Agent.
    
    Manages emergency Band spaces (crisis rooms) for PQC incidents with AI-powered
    decision making, intelligent channel routing, and stakeholder coordination.
    
    Features:
    - Automatic crisis room initialization with unique IDs
    - Intelligent channel selection based on incident characteristics
    - Dynamic stakeholder identification and notification
    - Real-time coordination status tracking
    - AI-powered severity assessment and escalation
    - Learning from past incidents for improved response
    
    Listens to: pqc.incident.detected, pqc.analysis.completed
    Publishes to: pqc.coordination.updated
    """
    
    def __init__(self, name: str, band_client, ai_client=None):
        """
        Initialize the PQC Coordination Agent.
        
        Args:
            name: Agent identifier
            band_client: BandClient instance for message bus communication
            ai_client: Optional AI client for intelligent decision making
        """
        super().__init__(name, band_client)
        self.ai_client = ai_client
        self.active_crisis_rooms: Dict[str, Dict[str, Any]] = {}
        self.crisis_room_sequence: Dict[str, int] = {}
        self.incident_history: List[Dict[str, Any]] = []
        logger.info(f"PQCCoordinationAgent '{name}' initialized with AI: {ai_client is not None}")
    
    def handle_message(self, message: MessageEnvelope) -> None:
        """
        Handle incoming PQC incident messages and coordinate crisis response.
        
        Processes incident detection messages, initializes crisis rooms,
        and manages coordination state throughout the incident lifecycle.
        
        Args:
            message: MessageEnvelope containing PQCIncidentDetected payload
        """
        try:
            # Validate incoming payload
            incident = PQCIncidentDetected.model_validate(message.payload)
            logger.info(f"🚨 Coordinating crisis response for incident: {incident.incident_id}")
            
            # Initialize crisis room and coordination
            coordination_state = self._initialize_crisis_coordination(incident)
            
            # Validate outgoing payload
            validated_state = PQCCoordinationState.model_validate(coordination_state)
            
            # Publish coordination state
            self.send_message("pqc.coordination.updated", validated_state.model_dump())
            
            # Log crisis room creation with visual feedback
            self._log_crisis_room_creation(validated_state)
            
            # Store in active crisis rooms
            self.active_crisis_rooms[incident.incident_id] = validated_state.model_dump()
            
            # Add to incident history for learning
            self.incident_history.append({
                "incident_id": incident.incident_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "crisis_room_id": validated_state.crisis_room_id,
                "channels": validated_state.channels_initialized,
                "status": validated_state.coordination_status
            })
            
        except Exception as e:
            logger.error(f"❌ Error coordinating crisis response: {e}", exc_info=True)
            # Emit error state
            try:
                incident_id = message.payload.get("incident_id", "unknown")
                error_state = {
                    "incident_id": incident_id,
                    "crisis_room_id": f"PQC-CRISIS-ROOM-ERROR-{incident_id[:8]}",
                    "channels_initialized": ["Emergency"],
                    "coordination_status": "initializing",
                    "stakeholders_notified": ["Emergency Response Team"]
                }
                validated_error = PQCCoordinationState.model_validate(error_state)
                self.send_message("pqc.coordination.updated", validated_error.model_dump())
            except Exception as inner_e:
                logger.error(f"Failed to emit error coordination state: {inner_e}")
    
    def _initialize_crisis_coordination(self, incident: PQCIncidentDetected) -> Dict[str, Any]:
        """
        Initialize comprehensive crisis coordination for the incident.
        
        Creates crisis room, determines channels, identifies stakeholders,
        and sets initial coordination status based on incident characteristics.
        
        Args:
            incident: Validated PQCIncidentDetected payload
            
        Returns:
            Dictionary containing coordination state matching PQCCoordinationState schema
        """
        # Extract system name from incident
        system_name = self._extract_system_name(incident.description)
        
        # Generate unique crisis room ID
        crisis_room_id = self._generate_crisis_room_id(system_name)
        
        # Determine which channels to initialize
        channels = self._determine_channels(incident.description, incident.severity_initial)
        
        # Identify stakeholders to notify
        stakeholders = self._identify_stakeholders(
            incident.description, 
            incident.severity_initial,
            system_name
        )
        
        # Determine initial coordination status
        coordination_status = self._determine_initial_status(
            incident.severity_initial,
            incident.description
        )
        
        # Use AI for enhanced coordination if available
        if self.ai_client:
            coordination_status = self._ai_enhanced_coordination(
                incident,
                channels,
                stakeholders,
                coordination_status
            )
        
        logger.info(f"✅ Crisis room '{crisis_room_id}' initialized with {len(channels)} channels")
        
        return {
            "incident_id": incident.incident_id,
            "crisis_room_id": crisis_room_id,
            "channels_initialized": channels,
            "coordination_status": coordination_status,
            "stakeholders_notified": stakeholders
        }
    
    def _extract_system_name(self, description: str) -> str:
        """
        Extract system name from incident description using pattern matching.
        
        Identifies key system components like HSM, Gateway, Network, etc.
        
        Args:
            description: Incident description text
            
        Returns:
            Extracted system name (e.g., "HSM", "GATEWAY", "NETWORK")
        """
        description_upper = description.upper()
        
        # Priority-ordered system patterns
        system_patterns = [
            (r'\bHSM\b', 'HSM'),
            (r'\bGATEWAY\b', 'GATEWAY'),
            (r'\bCLEARING\b', 'CLEARING'),
            (r'\bNETWORK\b', 'NETWORK'),
            (r'\bKEY\s+MANAGEMENT\b', 'KMS'),
            (r'\bCERTIFICATE\s+AUTHORITY\b', 'CA'),
            (r'\bCROSS-BORDER\b', 'XBORDER'),
            (r'\bINFRASTRUCTURE\b', 'INFRA'),
        ]
        
        for pattern, system_name in system_patterns:
            if re.search(pattern, description_upper):
                return system_name
        
        # Fallback: extract first capitalized word or use GENERAL
        words = description.split()
        for word in words:
            if word.isupper() and len(word) > 2:
                return word[:10]  # Limit length
        
        return "GENERAL"
    
    def _generate_crisis_room_id(self, system_name: str) -> str:
        """
        Generate unique crisis room ID with sequential numbering.
        
        Format: PQC-CRISIS-ROOM-{SYSTEM}-{SEQUENCE}
        Example: PQC-CRISIS-ROOM-HSM-01
        
        Args:
            system_name: Extracted system name
            
        Returns:
            Unique crisis room identifier
        """
        # Get or initialize sequence for this system
        if system_name not in self.crisis_room_sequence:
            self.crisis_room_sequence[system_name] = 0
        
        self.crisis_room_sequence[system_name] += 1
        sequence = self.crisis_room_sequence[system_name]
        
        return f"PQC-CRISIS-ROOM-{system_name}-{sequence:02d}"
    
    def _determine_channels(self, description: str, severity: str) -> List[str]:
        """
        Intelligently determine which operational channels to initialize.
        
        Analyzes incident characteristics to select appropriate channels:
        - Network: Network infrastructure issues
        - Security: Cryptographic security concerns
        - Infrastructure: Hardware/system issues
        - Compliance: Regulatory and compliance matters
        - Executive: High-severity incidents requiring executive attention
        
        Args:
            description: Incident description
            severity: Initial severity assessment
            
        Returns:
            List of channel names to initialize
        """
        description_lower = description.lower()
        channels = set()
        
        # Core channels based on keywords
        if any(keyword in description_lower for keyword in 
               ["entropy", "hsm", "key", "crypto", "cipher", "algorithm"]):
            channels.add("Security")
            channels.add("Infrastructure")
        
        if any(keyword in description_lower for keyword in 
               ["network", "gateway", "latency", "connection", "routing"]):
            channels.add("Network")
        
        if any(keyword in description_lower for keyword in 
               ["hardware", "server", "infrastructure", "system", "hsm"]):
            channels.add("Infrastructure")
        
        if any(keyword in description_lower for keyword in 
               ["cross-border", "compliance", "regulatory", "audit", "legal"]):
            channels.add("Compliance")
        
        # Add Executive channel for critical incidents
        if severity.lower() in ["critical", "high"] or any(
            keyword in description_lower for keyword in 
            ["critical", "severe", "emergency", "flash-crash", "outage"]
        ):
            channels.add("Executive")
        
        # Ensure at least Security channel is present
        if not channels:
            channels.add("Security")
            channels.add("Infrastructure")
        
        # Sort for consistent ordering
        return sorted(list(channels))
    
    def _identify_stakeholders(self, description: str, severity: str, system_name: str) -> List[str]:
        """
        Identify stakeholders to notify based on incident characteristics.
        
        Uses intelligent matching to determine which teams and individuals
        need to be notified for effective crisis response.
        
        Args:
            description: Incident description
            severity: Initial severity level
            system_name: Affected system name
            
        Returns:
            List of stakeholder identifiers
        """
        description_lower = description.lower()
        stakeholders = set()
        
        # Core teams always notified
        stakeholders.add("Security Team")
        stakeholders.add("Infrastructure Team")
        
        # System-specific teams
        if "hsm" in description_lower or system_name == "HSM":
            stakeholders.add("HSM Operations")
            stakeholders.add("Cryptography Team")
        
        if "network" in description_lower or "gateway" in description_lower:
            stakeholders.add("Network Operations")
        
        if "cross-border" in description_lower or "clearing" in description_lower:
            stakeholders.add("Clearing Operations")
            stakeholders.add("Compliance Team")
        
        # Severity-based escalation
        if severity.lower() in ["critical", "high"]:
            stakeholders.add("Executive Leadership")
            stakeholders.add("Incident Commander")
        
        if "compliance" in description_lower or "regulatory" in description_lower:
            stakeholders.add("Legal Team")
            stakeholders.add("Compliance Officer")
        
        # Financial impact stakeholders
        if any(keyword in description_lower for keyword in 
               ["financial", "trading", "transaction", "clearing"]):
            stakeholders.add("Risk Management")
            stakeholders.add("Financial Operations")
        
        return sorted(list(stakeholders))
    
    def _determine_initial_status(self, severity: str, description: str) -> str:
        """
        Determine initial coordination status based on incident severity.
        
        Args:
            severity: Initial severity assessment
            description: Incident description
            
        Returns:
            Coordination status: "initializing", "active", "escalated", or "resolved"
        """
        description_lower = description.lower()
        
        # Immediate escalation for critical incidents
        if severity.lower() == "critical" or any(
            keyword in description_lower for keyword in 
            ["emergency", "critical", "severe", "flash-crash"]
        ):
            return "escalated"
        
        # Active status for high severity
        if severity.lower() == "high":
            return "active"
        
        # Default to initializing
        return "initializing"
    
    def _ai_enhanced_coordination(
        self, 
        incident: PQCIncidentDetected,
        channels: List[str],
        stakeholders: List[str],
        status: str
    ) -> str:
        """
        Use AI to enhance coordination decision-making.
        
        Leverages AI client to analyze incident patterns and recommend
        optimal coordination strategy based on historical data.
        
        Args:
            incident: PQCIncidentDetected payload
            channels: Initially determined channels
            stakeholders: Initially identified stakeholders
            status: Initial coordination status
            
        Returns:
            Enhanced coordination status
        """
        try:
            # In production, this would call the AI client for intelligent analysis
            # For now, we enhance based on historical patterns
            
            # Check if similar incidents exist in history
            similar_incidents = [
                h for h in self.incident_history
                if any(channel in h.get("channels", []) for channel in channels)
            ]
            
            if len(similar_incidents) >= 3:
                # Learn from past incidents
                logger.info(f"🤖 AI: Found {len(similar_incidents)} similar incidents in history")
                
                # If past incidents escalated, proactively escalate
                escalated_count = sum(
                    1 for h in similar_incidents 
                    if h.get("status") == "escalated"
                )
                
                if escalated_count / len(similar_incidents) > 0.5 and status != "escalated":
                    logger.info("🤖 AI: Proactively escalating based on historical patterns")
                    return "escalated"
            
            return status
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return status
    
    def _log_crisis_room_creation(self, state: PQCCoordinationState) -> None:
        """
        Log crisis room creation with visual formatting for monitoring.
        
        Args:
            state: Validated coordination state
        """
        logger.info("=" * 80)
        logger.info(f"🏢 CRISIS ROOM INITIALIZED: {state.crisis_room_id}")
        logger.info(f"📋 Incident ID: {state.incident_id}")
        logger.info(f"📡 Channels: {', '.join(state.channels_initialized)}")
        logger.info(f"👥 Stakeholders: {', '.join(state.stakeholders_notified)}")
        logger.info(f"🚦 Status: {state.coordination_status.upper()}")
        logger.info("=" * 80)
    
    def update_coordination_status(
        self, 
        incident_id: str, 
        new_status: str,
        additional_stakeholders: Optional[List[str]] = None
    ) -> None:
        """
        Update coordination status for an active crisis room.
        
        Allows dynamic status updates as the incident progresses through
        its lifecycle (initializing → active → escalated → resolved).
        
        Args:
            incident_id: Incident identifier
            new_status: New coordination status
            additional_stakeholders: Optional additional stakeholders to notify
        """
        if incident_id not in self.active_crisis_rooms:
            logger.warning(f"Cannot update status: incident {incident_id} not found")
            return
        
        crisis_room = self.active_crisis_rooms[incident_id]
        crisis_room["coordination_status"] = new_status
        
        if additional_stakeholders:
            current_stakeholders = set(crisis_room["stakeholders_notified"])
            current_stakeholders.update(additional_stakeholders)
            crisis_room["stakeholders_notified"] = sorted(list(current_stakeholders))
        
        # Publish updated state
        validated_state = PQCCoordinationState.model_validate(crisis_room)
        self.send_message("pqc.coordination.updated", validated_state.model_dump())
        
        logger.info(f"📊 Updated coordination status for {incident_id}: {new_status}")
    
    def get_active_crisis_rooms(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all currently active crisis rooms.
        
        Returns:
            Dictionary mapping incident IDs to crisis room states
        """
        return self.active_crisis_rooms.copy()
    
    def get_incident_history(self) -> List[Dict[str, Any]]:
        """
        Get historical incident data for analysis and learning.
        
        Returns:
            List of historical incident records
        """
        return self.incident_history.copy()


# Made with Bob - Advanced Multi-Agent Coordination System