from typing import Dict, Any, Optional, List
from agents.base_agent import Agent
from messages.models import MessageEnvelope, PQCAnalysisResult, PQCCoordinationState, PQCExecutiveDecision
import logging

logger = logging.getLogger(__name__)


class PQCDecisionAgent(Agent):
    """
    Executive Decision Agent for Post-Quantum Cryptographic (PQC) incidents.
    
    This agent synthesizes analysis results and coordination state to generate
    executive-ready business recommendations with comprehensive risk matrices.
    It listens to both analysis and coordination topics, aggregates data per
    incident, and produces actionable directives when both data sources are available.
    
    Key Responsibilities:
    - Aggregate analysis and coordination data per incident_id
    - Generate executive-level recommendations with risk assessment
    - Produce comprehensive risk matrices for decision-making
    - Determine priority levels (P0-P3) based on severity and impact
    - Estimate downtime and approval requirements
    """

    def __init__(self, name: str, band_client, ai_client=None):
        """
        Initialize the PQC Decision Agent.
        
        Args:
            name: Agent identifier
            band_client: BandClient instance for message bus communication
            ai_client: Optional AI client for decision synthesis (uses heuristics if None)
        """
        super().__init__(name, band_client)
        self.ai_client = ai_client
        
        # State management for aggregating data per incident
        self._analysis_results: Dict[str, Dict[str, Any]] = {}
        self._coordination_states: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"PQCDecisionAgent '{name}' initialized with AI client: {ai_client is not None}")

    def handle_message(self, message: MessageEnvelope):
        """
        Handle incoming messages from analysis and coordination agents.
        
        Routes messages based on topic:
        - "pqc.analysis.completed": Stores analysis results
        - "pqc.coordination.updated": Stores coordination state
        
        When both analysis and coordination data are available for an incident,
        triggers decision synthesis and publishes executive decision.
        
        Args:
            message: MessageEnvelope containing the message data
        """
        try:
            topic = message.topic
            payload = message.payload
            
            if topic == "pqc.analysis.completed":
                self._handle_analysis_completed(payload)
            elif topic == "pqc.coordination.updated":
                self._handle_coordination_updated(payload)
            else:
                logger.warning(f"Received unexpected topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    def _handle_analysis_completed(self, payload: Dict[str, Any]):
        """
        Handle analysis completion messages.
        
        Validates the payload, stores it, and checks if decision can be synthesized.
        
        Args:
            payload: Analysis result payload
        """
        try:
            # Validate payload structure
            analysis = PQCAnalysisResult.model_validate(payload)
            incident_id = analysis.incident_id
            
            logger.info(f"Received analysis for incident {incident_id}: Severity {analysis.severity_level}")
            
            # Store analysis result
            self._analysis_results[incident_id] = analysis.model_dump()
            
            # Check if we can synthesize decision
            self._check_and_synthesize(incident_id)
            
        except Exception as e:
            logger.error(f"Error handling analysis completed: {e}", exc_info=True)

    def _handle_coordination_updated(self, payload: Dict[str, Any]):
        """
        Handle coordination update messages.
        
        Validates the payload, stores it, and checks if decision can be synthesized.
        
        Args:
            payload: Coordination state payload
        """
        try:
            # Validate payload structure
            coordination = PQCCoordinationState.model_validate(payload)
            incident_id = coordination.incident_id
            
            logger.info(f"Received coordination for incident {incident_id}: Status {coordination.coordination_status}")
            
            # Store coordination state
            self._coordination_states[incident_id] = coordination.model_dump()
            
            # Check if we can synthesize decision
            self._check_and_synthesize(incident_id)
            
        except Exception as e:
            logger.error(f"Error handling coordination updated: {e}", exc_info=True)

    def _check_and_synthesize(self, incident_id: str):
        """
        Check if both analysis and coordination data exist for an incident.
        
        If both are available, synthesizes executive decision and publishes it.
        Clears state after decision is made to prevent memory leaks.
        
        Args:
            incident_id: The incident identifier to check
        """
        # Check if we have both analysis and coordination data
        if incident_id not in self._analysis_results or incident_id not in self._coordination_states:
            logger.debug(f"Waiting for complete data for incident {incident_id}")
            return
        
        try:
            analysis = self._analysis_results[incident_id]
            coordination = self._coordination_states[incident_id]
            
            logger.info(f"Synthesizing executive decision for incident {incident_id}")
            
            # Generate decision components
            recommendation = self._generate_recommendation(analysis, coordination)
            risk_matrix = self._build_risk_matrix(analysis, coordination)
            priority = self._determine_priority(
                analysis['severity_level'],
                analysis['financial_exposure_per_minute']
            )
            estimated_downtime = self._estimate_downtime(
                analysis['severity_level'],
                analysis['technical_details'].get('affected_systems', [])
            )
            
            # Determine if approval is required (P0 or high financial exposure)
            approval_required = (
                priority == "P0" or
                analysis['financial_exposure_per_minute'] > 100000
            )
            
            # Construct decision payload
            decision_payload = {
                "incident_id": incident_id,
                "recommendation": recommendation,
                "risk_matrix": risk_matrix,
                "estimated_downtime_minutes": estimated_downtime,
                "approval_required": approval_required,
                "priority": priority
            }
            
            # Validate decision structure
            decision = PQCExecutiveDecision.model_validate(decision_payload)
            
            # Publish decision
            self.send_message("pqc.decision.made", decision.model_dump())
            
            logger.info(f"Executive decision published for incident {incident_id}: Priority {priority}")
            
            # Clear state to prevent memory leaks
            del self._analysis_results[incident_id]
            del self._coordination_states[incident_id]
            
        except Exception as e:
            logger.error(f"Error synthesizing decision for incident {incident_id}: {e}", exc_info=True)
            
            # Emit error decision with lower confidence
            try:
                error_decision = {
                    "incident_id": incident_id,
                    "recommendation": f"Decision synthesis failed: {str(e)}. Manual review required.",
                    "risk_matrix": {
                        "immediate_action": "Escalate to manual review",
                        "fallback_mechanism": "Pending manual assessment",
                        "compliance_risks": "Unable to assess automatically",
                        "regulatory_impact": "Requires manual compliance review"
                    },
                    "estimated_downtime_minutes": None,
                    "approval_required": True,
                    "priority": "P1"
                }
                self.send_message("pqc.decision.made", error_decision)
            except Exception as publish_error:
                logger.error(f"Failed to publish error decision: {publish_error}", exc_info=True)

    def _generate_recommendation(self, analysis: Dict[str, Any], coordination: Dict[str, Any]) -> str:
        """
        Generate actionable recommendation based on analysis and coordination data.
        
        Uses AI client if available, otherwise applies intelligent heuristics based on
        severity level, affected systems, and financial impact.
        
        Args:
            analysis: Analysis result dictionary
            coordination: Coordination state dictionary
            
        Returns:
            Actionable recommendation string
        """
        if self.ai_client:
            try:
                # Use AI for sophisticated recommendation synthesis
                prompt = f"""Generate an executive-level recommendation for a PQC cryptographic incident.

Analysis:
- Severity: {analysis['severity_level']}
- Root Cause: {analysis['root_cause_hypothesis']}
- Financial Exposure: ${analysis['financial_exposure_per_minute']}/minute
- Technical Details: {analysis['technical_details']}

Coordination:
- Crisis Room: {coordination['crisis_room_id']}
- Channels: {coordination['channels_initialized']}
- Status: {coordination['coordination_status']}
- Stakeholders: {coordination['stakeholders_notified']}

Provide a clear, actionable directive for executive decision-making."""

                recommendation = self.ai_client.generate_text(prompt)
                return recommendation.strip()
            except Exception as e:
                logger.warning(f"AI recommendation failed, falling back to heuristics: {e}")
        
        # Heuristic-based recommendation
        severity = analysis['severity_level']
        financial_exposure = analysis['financial_exposure_per_minute']
        technical_details = analysis['technical_details']
        affected_systems = technical_details.get('affected_systems', [])
        
        # Level 5 severity + HSM issues → Immediate fallback
        if severity == "Level 5" and any('HSM' in sys for sys in affected_systems):
            return (
                "Issue emergency fallback to classical hybrid elliptic-curve cryptography (ECDH) "
                "to restore transaction clearance speed. Activate HSM redundancy protocols immediately. "
                "This is a critical system failure requiring immediate action to prevent cascading failures."
            )
        
        # High financial exposure → Prioritize with urgency
        if financial_exposure > 100000:
            return (
                f"Critical financial exposure detected (${financial_exposure:,.0f}/minute). "
                "Implement immediate containment measures and activate business continuity protocols. "
                "Escalate to C-level executives for approval of emergency response procedures."
            )
        
        # Cross-border/clearing gateway → Regulatory focus
        if any('gateway' in sys.lower() or 'clearing' in sys.lower() for sys in affected_systems):
            return (
                "Cross-border clearing gateway affected. Implement regulatory-compliant fallback mechanisms "
                "while maintaining transaction integrity. Notify relevant financial regulators within required "
                "timeframes and document all mitigation steps for compliance audit trail."
            )
        
        # Level 4-5 severity → Aggressive response
        if severity in ["Level 4", "Level 5"]:
            return (
                f"High-severity incident ({severity}) detected. Activate crisis response team and implement "
                "pre-approved fallback mechanisms. Monitor system stability closely and prepare for "
                "potential extended recovery procedures."
            )
        
        # Level 3 severity → Controlled response
        if severity == "Level 3":
            return (
                "Moderate-severity incident requiring controlled response. Implement staged fallback "
                "procedures while maintaining service continuity. Coordinate with technical teams "
                "for root cause analysis and permanent remediation."
            )
        
        # Level 1-2 severity → Standard response
        return (
            f"Standard incident response for {severity} severity. Monitor situation closely and "
            "implement standard operating procedures. Coordinate with technical teams for "
            "assessment and resolution within normal SLA timeframes."
        )

    def _build_risk_matrix(self, analysis: Dict[str, Any], coordination: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive risk matrix for executive decision-making.
        
        Includes immediate actions, fallback mechanisms, compliance risks,
        and regulatory impact based on severity and system criticality.
        
        Args:
            analysis: Analysis result dictionary
            coordination: Coordination state dictionary
            
        Returns:
            Risk matrix dictionary with required fields
        """
        severity = analysis['severity_level']
        financial_exposure = analysis['financial_exposure_per_minute']
        technical_details = analysis['technical_details']
        affected_systems = technical_details.get('affected_systems', [])
        
        risk_matrix = {
            "immediate_action": "",
            "fallback_mechanism": "",
            "compliance_risks": "",
            "regulatory_impact": ""
        }
        
        # Determine immediate action based on severity
        if severity == "Level 5":
            risk_matrix["immediate_action"] = "Switch to fallback mechanism within 5 minutes; activate all redundancy systems"
        elif severity == "Level 4":
            risk_matrix["immediate_action"] = "Initiate controlled fallback within 15 minutes; notify stakeholders"
        elif severity == "Level 3":
            risk_matrix["immediate_action"] = "Prepare fallback procedures; monitor system stability closely"
        else:
            risk_matrix["immediate_action"] = "Continue monitoring; implement standard response procedures"
        
        # Determine fallback mechanism based on affected systems
        if any('HSM' in sys for sys in affected_systems):
            risk_matrix["fallback_mechanism"] = "Classical ECDH with AES-256-GCM for session encryption; activate HSM redundancy"
        elif any('gateway' in sys.lower() for sys in affected_systems):
            risk_matrix["fallback_mechanism"] = "Hybrid classical-quantum protocol with RSA-4096 backup"
        else:
            risk_matrix["fallback_mechanism"] = "Standard cryptographic fallback to pre-quantum algorithms"
        
        # Assess compliance risks
        if severity in ["Level 4", "Level 5"]:
            risk_matrix["compliance_risks"] = (
                "Temporary reduction in post-quantum readiness; document exception and mitigation timeline. "
                "Potential audit findings if extended beyond approved timeframes."
            )
        else:
            risk_matrix["compliance_risks"] = (
                "Minimal compliance impact; maintain documentation of incident response for audit trail"
            )
        
        # Determine regulatory impact
        regulatory_impacts = []
        
        if any('payment' in sys.lower() or 'transaction' in sys.lower() for sys in affected_systems):
            regulatory_impacts.append("PCI-DSS compliance maintained with fallback mechanisms")
        
        if financial_exposure > 50000:
            regulatory_impacts.append("SOX reporting required for material financial impact")
        
        if any('gateway' in sys.lower() or 'clearing' in sys.lower() for sys in affected_systems):
            regulatory_impacts.append("Notify financial regulators within 24 hours per regulatory requirements")
        
        if any('customer' in sys.lower() or 'data' in sys.lower() for sys in affected_systems):
            regulatory_impacts.append("GDPR data protection measures remain in effect")
        
        if not regulatory_impacts:
            regulatory_impacts.append("Standard regulatory compliance maintained; no special notifications required")
        
        risk_matrix["regulatory_impact"] = "; ".join(regulatory_impacts)
        
        return risk_matrix

    def _determine_priority(self, severity: str, financial_exposure: float) -> str:
        """
        Determine priority level (P0-P3) based on severity and financial impact.
        
        Priority levels:
        - P0: Critical, immediate action required
        - P1: High priority, urgent response needed
        - P2: Medium priority, timely response required
        - P3: Low priority, standard response
        
        Args:
            severity: Severity level string (Level 1-5)
            financial_exposure: Financial exposure per minute in dollars
            
        Returns:
            Priority level string (P0, P1, P2, or P3)
        """
        # P0: Level 5 severity OR very high financial exposure
        if severity == "Level 5" or financial_exposure > 100000:
            return "P0"
        
        # P1: Level 4 severity OR high financial exposure
        if severity == "Level 4" or financial_exposure > 50000:
            return "P1"
        
        # P2: Level 3 severity OR moderate financial exposure
        if severity == "Level 3" or financial_exposure > 10000:
            return "P2"
        
        # P3: Level 1-2 severity with low financial exposure
        return "P3"

    def _estimate_downtime(self, severity: str, systems: List[str]) -> Optional[int]:
        """
        Estimate downtime in minutes based on severity and system complexity.
        
        Considers both the severity level and the complexity/criticality of
        affected systems to provide realistic downtime estimates.
        
        Args:
            severity: Severity level string (Level 1-5)
            systems: List of affected system names
            
        Returns:
            Estimated downtime in minutes, or None if not applicable
        """
        # Base downtime by severity
        base_downtime = {
            "Level 5": 15,
            "Level 4": 30,
            "Level 3": 60,
            "Level 2": 120,
            "Level 1": 240
        }
        
        downtime = base_downtime.get(severity, 60)
        
        # Adjust for system complexity
        complexity_multiplier = 1.0
        
        # HSM systems are complex and require careful handling
        if any('HSM' in sys for sys in systems):
            complexity_multiplier *= 1.5
        
        # Gateway systems affect multiple downstream services
        if any('gateway' in sys.lower() or 'clearing' in sys.lower() for sys in systems):
            complexity_multiplier *= 1.3
        
        # Multiple systems increase coordination overhead
        if len(systems) > 3:
            complexity_multiplier *= 1.2
        
        estimated = int(downtime * complexity_multiplier)
        
        # Return None for low-severity incidents that may not require downtime
        if severity in ["Level 1", "Level 2"] and estimated > 180:
            return None
        
        return estimated

# Made with Bob
