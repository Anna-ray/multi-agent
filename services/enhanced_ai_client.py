import os
import requests
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class EnhancedAIClient:
    """
    Enhanced AI/ML Client with support for multiple AI providers.
    
    Integrates with:
    - AI/ML API for advanced analysis and synthesis
    - Featherless API for classification and inference
    - Fallback to local heuristics when APIs unavailable
    
    Features:
    - Intelligent incident analysis
    - Pattern recognition
    - Decision recommendation
    - Confidence scoring
    - Multi-model ensemble predictions
    """
    
    def __init__(
        self, 
        ai_ml_api_key: Optional[str] = None,
        featherless_api_key: Optional[str] = None,
        ai_ml_endpoint: Optional[str] = None,
        featherless_endpoint: Optional[str] = None
    ):
        """
        Initialize the Enhanced AI Client.
        
        Args:
            ai_ml_api_key: API key for AI/ML service
            featherless_api_key: API key for Featherless service
            ai_ml_endpoint: Custom endpoint for AI/ML service
            featherless_endpoint: Custom endpoint for Featherless service
        """
        self.ai_ml_api_key = ai_ml_api_key or os.getenv("AI_ML_API_KEY")
        self.featherless_api_key = featherless_api_key or os.getenv("FEATHERLESS_API_KEY")
        
        self.ai_ml_endpoint = ai_ml_endpoint or os.getenv(
            "AI_ML_ENDPOINT", 
            "https://api.aimlapi.com/v1/chat/completions"
        )
        self.featherless_endpoint = featherless_endpoint or os.getenv(
            "FEATHERLESS_ENDPOINT",
            "https://api.featherless.ai/v1/chat/completions"
        )
        
        self.timeout = 30
        self.max_retries = 2
        
        logger.info(f"🤖 Enhanced AI Client initialized")
        logger.info(f"   AI/ML API: {'✓' if self.ai_ml_api_key else '✗'}")
        logger.info(f"   Featherless API: {'✓' if self.featherless_api_key else '✗'}")
    
    def analyze_incident(
        self, 
        description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform deep AI-powered incident analysis.
        
        Args:
            description: Incident description
            context: Additional context information
            
        Returns:
            Analysis results with severity, root cause, and recommendations
        """
        logger.info("🔍 Performing AI-powered incident analysis...")
        
        # Try AI/ML API first
        if self.ai_ml_api_key:
            try:
                return self._analyze_with_aiml(description, context)
            except Exception as e:
                logger.warning(f"AI/ML analysis failed: {e}, trying Featherless...")
        
        # Fallback to Featherless
        if self.featherless_api_key:
            try:
                return self._analyze_with_featherless(description, context)
            except Exception as e:
                logger.warning(f"Featherless analysis failed: {e}, using heuristics...")
        
        # Final fallback to heuristics
        return self._heuristic_analysis(description, context)
    
    def _analyze_with_aiml(
        self, 
        description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze incident using AI/ML API.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            Analysis results
        """
        prompt = self._build_analysis_prompt(description, context)
        
        headers = {
            "Authorization": f"Bearer {self.ai_ml_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",  # or another model
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity analyst specializing in post-quantum cryptography incidents. Analyze incidents and provide structured assessments."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(
            self.ai_ml_endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse AI response
        return self._parse_ai_response(content, "aiml")
    
    def _analyze_with_featherless(
        self, 
        description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze incident using Featherless API.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            Analysis results
        """
        prompt = self._build_analysis_prompt(description, context)
        
        headers = {
            "Authorization": f"Bearer {self.featherless_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert analyzing cryptographic incidents. Provide concise, structured analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        response = requests.post(
            self.featherless_endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse AI response
        return self._parse_ai_response(content, "featherless")
    
    def _build_analysis_prompt(
        self, 
        description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build structured prompt for AI analysis.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze this cryptographic incident and provide a structured assessment:

INCIDENT DESCRIPTION:
{description}
"""
        
        if context:
            prompt += f"\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}\n"
        
        prompt += """
Please provide:
1. SEVERITY (Level 1-5, where 5 is most critical)
2. ROOT CAUSE (brief hypothesis)
3. FINANCIAL IMPACT (estimated $ per minute)
4. AFFECTED SYSTEMS (list)
5. RECOMMENDED ACTIONS (top 3)
6. CONFIDENCE (0.0 to 1.0)

Format your response as JSON with these exact keys: severity_level, root_cause, financial_exposure_per_minute, affected_systems, recommended_actions, confidence_score
"""
        
        return prompt
    
    def _parse_ai_response(self, content: str, source: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.
        
        Args:
            content: AI response content
            source: Source API ("aiml" or "featherless")
            
        Returns:
            Structured analysis results
        """
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            
            if json_match:
                parsed = json.loads(json_match.group())
                
                return {
                    "severity_level": parsed.get("severity_level", "Level 3"),
                    "root_cause": parsed.get("root_cause", "AI analysis in progress"),
                    "financial_exposure_per_minute": float(parsed.get("financial_exposure_per_minute", 50000)),
                    "affected_systems": parsed.get("affected_systems", ["unknown"]),
                    "recommended_actions": parsed.get("recommended_actions", []),
                    "confidence_score": float(parsed.get("confidence_score", 0.7)),
                    "ai_source": source,
                    "raw_response": content[:500]  # Store first 500 chars
                }
            else:
                # Fallback parsing
                return self._fallback_parse(content, source)
                
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return self._fallback_parse(content, source)
    
    def _fallback_parse(self, content: str, source: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        content_lower = content.lower()
        
        # Extract severity
        severity = "Level 3"
        for level in ["level 5", "level 4", "level 3", "level 2", "level 1"]:
            if level in content_lower:
                severity = level.title()
                break
        
        # Extract confidence
        confidence = 0.7
        import re
        conf_match = re.search(r'confidence[:\s]+([0-9.]+)', content_lower)
        if conf_match:
            confidence = float(conf_match.group(1))
        
        return {
            "severity_level": severity,
            "root_cause": "AI analysis completed - see raw response",
            "financial_exposure_per_minute": 50000.0,
            "affected_systems": ["multiple"],
            "recommended_actions": ["Review AI analysis", "Escalate to security team"],
            "confidence_score": confidence,
            "ai_source": source,
            "raw_response": content[:500]
        }
    
    def _heuristic_analysis(
        self, 
        description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fallback heuristic analysis when AI APIs unavailable.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            Heuristic analysis results
        """
        logger.info("📊 Using heuristic analysis (AI APIs unavailable)")
        
        description_lower = description.lower()
        
        # Severity assessment
        severity = "Level 3"
        financial_exposure = 50000.0
        
        if any(word in description_lower for word in ["critical", "emergency", "severe"]):
            severity = "Level 5"
            financial_exposure = 150000.0
        elif any(word in description_lower for word in ["high", "major", "significant"]):
            severity = "Level 4"
            financial_exposure = 100000.0
        
        # Root cause detection
        root_cause = "Cryptographic anomaly detected"
        if "hsm" in description_lower and "entropy" in description_lower:
            root_cause = "HSM entropy degradation affecting key generation"
        elif "handshake" in description_lower and "fail" in description_lower:
            root_cause = "Post-quantum handshake failures"
        
        # Affected systems
        affected_systems = []
        for system in ["hsm", "gateway", "network", "clearing", "infrastructure"]:
            if system in description_lower:
                affected_systems.append(system.upper())
        
        if not affected_systems:
            affected_systems = ["UNKNOWN"]
        
        return {
            "severity_level": severity,
            "root_cause": root_cause,
            "financial_exposure_per_minute": financial_exposure,
            "affected_systems": affected_systems,
            "recommended_actions": [
                "Initiate crisis response",
                "Notify security team",
                "Monitor system metrics"
            ],
            "confidence_score": 0.6,
            "ai_source": "heuristic",
            "raw_response": "Heuristic analysis based on keyword matching"
        }
    
    def classify_urgency(self, text: str) -> Dict[str, Any]:
        """
        Classify urgency level of incident.
        
        Args:
            text: Text to classify
            
        Returns:
            Classification result with level and score
        """
        if self.featherless_api_key:
            try:
                return self._classify_with_featherless(text)
            except Exception as e:
                logger.warning(f"Featherless classification failed: {e}")
        
        # Fallback heuristic
        return self._heuristic_classification(text)
    
    def _classify_with_featherless(self, text: str) -> Dict[str, Any]:
        """Classify using Featherless API."""
        headers = {
            "Authorization": f"Bearer {self.featherless_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": f"Classify the urgency of this incident as 'low', 'medium', 'high', or 'critical'. Respond with only the urgency level:\n\n{text}"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        response = requests.post(
            self.featherless_endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        level = result["choices"][0]["message"]["content"].strip().lower()
        
        score_map = {"low": 0.3, "medium": 0.6, "high": 0.85, "critical": 0.98}
        
        return {
            "level": level,
            "score": score_map.get(level, 0.5)
        }
    
    def _heuristic_classification(self, text: str) -> Dict[str, Any]:
        """Heuristic urgency classification."""
        text_lower = text.lower()
        
        score = 0.5
        level = "medium"
        
        if any(word in text_lower for word in ["critical", "emergency", "severe", "flash-crash"]):
            score = 0.95
            level = "critical"
        elif any(word in text_lower for word in ["high", "urgent", "major"]):
            score = 0.8
            level = "high"
        elif any(word in text_lower for word in ["low", "minor", "routine"]):
            score = 0.3
            level = "low"
        
        return {"level": level, "score": score}
    
    def generate_recommendation(
        self, 
        incident_data: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        historical_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent recommendations based on multiple inputs.
        
        Args:
            incident_data: Current incident information
            analysis_results: Results from analysis agents
            historical_context: Similar past incidents
            
        Returns:
            Recommendation with confidence and rationale
        """
        logger.info("💡 Generating AI-powered recommendations...")
        
        if self.ai_ml_api_key:
            try:
                return self._generate_with_aiml(incident_data, analysis_results, historical_context)
            except Exception as e:
                logger.warning(f"AI recommendation failed: {e}")
        
        # Fallback to heuristic recommendation
        return self._heuristic_recommendation(incident_data, analysis_results)
    
    def _generate_with_aiml(
        self,
        incident_data: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        historical_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate recommendation using AI/ML API."""
        prompt = f"""Based on the following incident and analysis, provide an executive recommendation:

INCIDENT:
{json.dumps(incident_data, indent=2)}

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2)}
"""
        
        if historical_context:
            prompt += f"\nHISTORICAL CONTEXT:\n{json.dumps(historical_context[:2], indent=2)}\n"
        
        prompt += """
Provide a clear, actionable recommendation with:
1. Primary action to take
2. Rationale for this action
3. Confidence level (0.0 to 1.0)
4. Risk assessment

Format as JSON with keys: recommendation, rationale, confidence, risks
"""
        
        headers = {
            "Authorization": f"Bearer {self.ai_ml_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an executive decision advisor for cybersecurity incidents."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        response = requests.post(
            self.ai_ml_endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse response
        import re
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "recommendation": parsed.get("recommendation", "Escalate to security team"),
                "rationale": parsed.get("rationale", "AI analysis suggests immediate action"),
                "confidence": float(parsed.get("confidence", 0.75)),
                "risks": parsed.get("risks", []),
                "ai_generated": True
            }
        
        return self._heuristic_recommendation(incident_data, analysis_results)
    
    def _heuristic_recommendation(
        self,
        incident_data: Dict[str, Any],
        analysis_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate heuristic recommendation."""
        # Aggregate severity from analyses
        avg_confidence = sum(a.get("confidence_score", 0.5) for a in analysis_results) / max(len(analysis_results), 1)
        
        return {
            "recommendation": "Initiate crisis response protocol and escalate to executive team",
            "rationale": f"Based on {len(analysis_results)} analysis results with average confidence {avg_confidence:.2f}",
            "confidence": avg_confidence,
            "risks": ["System downtime", "Financial exposure", "Regulatory impact"],
            "ai_generated": False
        }


# Made with Bob - Advanced AI Integration System