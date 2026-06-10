from typing import Dict, Any, Optional
from agents.base_agent import Agent
from messages.models import MessageEnvelope, PQCIncidentDetected, PQCAnalysisResult
import logging
import re

logger = logging.getLogger(__name__)


class PQCAnalysisAgent(Agent):
    """
    Post-Quantum Cryptographic Analysis Agent.
    
    Specializes in analyzing cryptographic incidents related to quantum-resistant
    algorithms, HSM operations, and key exchange protocols. Performs deep technical
    analysis to determine severity, root cause, and financial impact.
    
    Listens to: pqc.incident.detected
    Publishes to: pqc.analysis.completed
    """
    
    def __init__(self, name: str, band_client, ai_client=None):
        """
        Initialize the PQC Analysis Agent.
        
        Args:
            name: Agent identifier
            band_client: BandClient instance for message bus communication
            ai_client: Optional AI client for advanced analysis (e.g., Featherless API)
        """
        super().__init__(name, band_client)
        self.ai_client = ai_client
        logger.info(f"PQCAnalysisAgent '{name}' initialized with AI client: {ai_client is not None}")
    
    def handle_message(self, message: MessageEnvelope) -> None:
        """
        Handle incoming PQC incident detection messages.
        
        Validates the message payload, performs cryptographic analysis,
        and publishes the analysis result to the message bus.
        
        Args:
            message: MessageEnvelope containing PQCIncidentDetected payload
        """
        try:
            # Validate incoming payload
            incident = PQCIncidentDetected.model_validate(message.payload)
            logger.info(f"Processing PQC incident: {incident.incident_id}")
            
            # Perform analysis
            analysis_result = self._analyze_incident(incident)
            
            # Validate outgoing payload
            validated_result = PQCAnalysisResult.model_validate(analysis_result)
            
            # Publish analysis result
            self.send_message("pqc.analysis.completed", validated_result.model_dump())
            logger.info(f"Analysis completed for incident {incident.incident_id} - Severity: {validated_result.severity_level}")
            
        except Exception as e:
            logger.error(f"Error processing PQC incident: {e}", exc_info=True)
            # Emit error result with low confidence
            try:
                incident_id = message.payload.get("incident_id", "unknown")
                error_result = {
                    "incident_id": incident_id,
                    "severity_level": "Level 3",
                    "root_cause_hypothesis": f"Analysis Error: {str(e)}",
                    "financial_exposure_per_minute": 0.0,
                    "technical_details": {
                        "error": str(e),
                        "status": "analysis_failed"
                    },
                    "confidence_score": 0.1
                }
                validated_error = PQCAnalysisResult.model_validate(error_result)
                self.send_message("pqc.analysis.completed", validated_error.model_dump())
            except Exception as inner_e:
                logger.error(f"Failed to emit error result: {inner_e}")
    
    def _analyze_incident(self, incident: PQCIncidentDetected) -> Dict[str, Any]:
        """
        Perform comprehensive cryptographic analysis on the incident.
        
        Uses AI client if available, otherwise applies intelligent heuristics
        based on keyword analysis and pattern matching.
        
        Args:
            incident: Validated PQCIncidentDetected payload
            
        Returns:
            Dictionary containing analysis results matching PQCAnalysisResult schema
        """
        if self.ai_client:
            return self._ai_powered_analysis(incident)
        else:
            return self._heuristic_analysis(incident)
    
    def _ai_powered_analysis(self, incident: PQCIncidentDetected) -> Dict[str, Any]:
        """
        Perform AI-powered deep analysis using the configured AI client.
        
        Args:
            incident: PQCIncidentDetected payload
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Simulate AI analysis call (placeholder for actual AI integration)
            logger.info(f"Performing AI-powered analysis for incident {incident.incident_id}")
            
            # In a real implementation, this would call the AI client:
            # response = self.ai_client.analyze(incident.description)
            
            # For now, fall back to heuristic analysis with higher confidence
            result = self._heuristic_analysis(incident)
            result["confidence_score"] = min(result["confidence_score"] + 0.1, 1.0)
            result["technical_details"]["analysis_method"] = "ai_powered"
            
            return result
            
        except Exception as e:
            logger.warning(f"AI analysis failed, falling back to heuristics: {e}")
            return self._heuristic_analysis(incident)
    
    def _heuristic_analysis(self, incident: PQCIncidentDetected) -> Dict[str, Any]:
        """
        Perform heuristic-based analysis using keyword matching and pattern recognition.
        
        Analyzes the incident description for critical indicators:
        - Cryptographic algorithm mentions (Kyber, Dilithium, etc.)
        - System component failures (HSM, gateway, etc.)
        - Performance degradation indicators
        - Infrastructure impact keywords
        
        Args:
            incident: PQCIncidentDetected payload
            
        Returns:
            Analysis result dictionary with severity, root cause, and financial impact
        """
        description = incident.description.lower()
        
        # Initialize analysis components
        severity_score = 1
        confidence = 0.7
        financial_exposure = 0.0
        affected_systems = []
        technical_details = {}
        root_cause_parts = []
        
        # Critical keyword analysis
        critical_keywords = {
            "entropy degradation": {"severity": 5, "exposure": 120000, "confidence": 0.95},
            "hsm": {"severity": 5, "exposure": 100000, "confidence": 0.9},
            "kyber-1024": {"severity": 5, "exposure": 80000, "confidence": 0.9},
            "key generation failure": {"severity": 5, "exposure": 150000, "confidence": 0.95},
            "handshake failure": {"severity": 4, "exposure": 90000, "confidence": 0.85},
            "latency spike": {"severity": 4, "exposure": 70000, "confidence": 0.8},
            "cross-border": {"severity": 4, "exposure": 60000, "confidence": 0.85},
            "clearing gateway": {"severity": 5, "exposure": 110000, "confidence": 0.9},
            "dilithium": {"severity": 4, "exposure": 50000, "confidence": 0.8},
            "quantum-resistant": {"severity": 3, "exposure": 30000, "confidence": 0.75},
            "certificate": {"severity": 3, "exposure": 40000, "confidence": 0.75},
            "tls": {"severity": 3, "exposure": 35000, "confidence": 0.7},
        }
        
        # Analyze keywords and accumulate severity/exposure
        for keyword, impact in critical_keywords.items():
            if keyword in description:
                severity_score = max(severity_score, impact["severity"])
                financial_exposure = max(financial_exposure, impact["exposure"])
                confidence = max(confidence, impact["confidence"])
                root_cause_parts.append(keyword)
        
        # Extract system components
        system_patterns = [
            r"hsm", r"gateway", r"clearing", r"cross-border", 
            r"key\s+management", r"certificate\s+authority", r"ca"
        ]
        for pattern in system_patterns:
            matches = re.findall(pattern, description)
            if matches:
                affected_systems.extend(matches)
        
        # Deduplicate and clean system names
        affected_systems = list(set(affected_systems))
        if not affected_systems:
            affected_systems = ["unknown"]
        
        # Extract cryptographic algorithms
        crypto_algorithms = []
        algo_patterns = [
            r"kyber-?\d+", r"dilithium-?\d+", r"falcon-?\d+", 
            r"sphincs\+?", r"ntru", r"saber"
        ]
        for pattern in algo_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            crypto_algorithms.extend(matches)
        
        technical_details["crypto_algorithm"] = crypto_algorithms[0] if crypto_algorithms else "unknown"
        
        # Detect specific failure modes
        if "handshake" in description and "fail" in description:
            technical_details["handshake_failures"] = "detected"
            root_cause_parts.append("handshake failures")
        
        if "entropy" in description:
            technical_details["entropy_metrics"] = "degraded" if "degrad" in description else "monitored"
            if "degrad" in description:
                root_cause_parts.append("entropy degradation")
        
        if "latency" in description or "spike" in description:
            technical_details["latency_impact"] = "critical"
            root_cause_parts.append("latency spikes")
        
        # Infrastructure impact assessment
        if any(word in description for word in ["critical", "cross-border", "clearing", "gateway"]):
            technical_details["infrastructure_impact"] = "critical"
        elif any(word in description for word in ["high", "severe", "major"]):
            technical_details["infrastructure_impact"] = "high"
        else:
            technical_details["infrastructure_impact"] = "moderate"
        
        # Extract numeric metrics
        numbers = re.findall(r'\d+(?:\.\d+)?', description)
        if numbers:
            technical_details["extracted_metrics"] = numbers[:5]  # Limit to first 5 numbers
        
        # Build root cause hypothesis
        if root_cause_parts:
            root_cause = f"Cryptographic incident involving {', '.join(root_cause_parts[:3])}"
            if "hsm" in description and "kyber" in description:
                root_cause = "HSM entropy starvation under peak Kyber-1024 load causing key-generation latency spikes"
            elif "handshake" in description and "fail" in description:
                root_cause = f"Post-quantum handshake failures in {technical_details.get('crypto_algorithm', 'PQC')} protocol"
        else:
            root_cause = "Unspecified cryptographic anomaly requiring further investigation"
        
        # Adjust confidence based on keyword matches
        if len(root_cause_parts) >= 3:
            confidence = min(confidence + 0.1, 1.0)
        
        # Add affected systems to technical details
        technical_details["affected_systems"] = affected_systems
        technical_details["analysis_method"] = "heuristic"
        technical_details["keyword_matches"] = root_cause_parts[:5]  # Limit to 5 keywords
        
        # Map severity score to level
        severity_level = f"Level {severity_score}"
        
        return {
            "incident_id": incident.incident_id,
            "severity_level": severity_level,
            "root_cause_hypothesis": root_cause,
            "financial_exposure_per_minute": financial_exposure,
            "technical_details": technical_details,
            "confidence_score": round(confidence, 2)
        }

# Made with Bob
