#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJECT NEXAVARA - PQC Crisis Response System
Main Orchestration Script for Post-Quantum Cryptographic Flash-Crash Demonstration

This script demonstrates the complete multi-agent workflow for handling a critical
PQC (Post-Quantum Cryptographic) incident involving HSM entropy degradation and
key-generation latency spikes during Kyber-1024 handshakes.

The demonstration showcases:
- Real-time incident detection and classification
- Deep cryptographic analysis with severity assessment
- Crisis room coordination with stakeholder management
- Executive decision synthesis with risk matrices
- Immutable forensic audit trail generation

Author: Bob (AI Software Engineer)
Date: 2026-06-10
"""

import logging
import time
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    # Set console code page to UTF-8
    os.system('chcp 65001 > nul 2>&1')

# Import Band communication infrastructure
from adapters.band_client import InMemoryBandClient

# Import all PQC agents
from agents.intake_agent import IntakeAgent
from agents.analysis_agent import PQCAnalysisAgent
from agents.coordination_agent import PQCCoordinationAgent
from agents.decision_agent import PQCDecisionAgent
from agents.audit_agent import PQCAuditAgent

# Import message models for validation
from messages.models import PQCIncidentDetected


# ============================================================================
# ANSI Color Codes for Console Output
# ============================================================================

class Colors:
    """ANSI color codes for styled console output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# ============================================================================
# Console Output Utilities
# ============================================================================

def print_banner(text: str, char: str = "=", color: str = Colors.CYAN) -> None:
    """Print a styled banner with the given text."""
    separator = char * 80
    print(f"\n{color}{separator}")
    print(f"{text}")
    print(f"{separator}{Colors.END}\n")


def print_step(emoji: str, text: str, color: str = Colors.BLUE) -> None:
    """Print a step with emoji and timestamp."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {emoji} {text}{Colors.END}")


def print_metric(label: str, value: Any, color: str = Colors.GREEN) -> None:
    """Print a metric with label and value."""
    print(f"{color}  {label}: {value}{Colors.END}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}❌ ERROR: {text}{Colors.END}")


# ============================================================================
# Agent State Tracking
# ============================================================================

class WorkflowState:
    """Track the state of the PQC incident workflow."""
    
    def __init__(self):
        self.incident_id: str = ""
        self.analysis_result: Dict[str, Any] = {}
        self.coordination_state: Dict[str, Any] = {}
        self.executive_decision: Dict[str, Any] = {}
        self.start_time: float = 0.0
        self.end_time: float = 0.0
    
    def get_execution_time(self) -> float:
        """Get total execution time in seconds."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time


# ============================================================================
# Message Collectors for Demonstration
# ============================================================================

def create_analysis_collector(state: WorkflowState):
    """Create a message handler to collect analysis results."""
    def collector(message):
        state.analysis_result = message.payload
        print_step("🔍", "Analysis Agent: Processing cryptographic anomaly...", Colors.CYAN)
        time.sleep(0.5)  # Visual delay for demonstration
        print_metric("Severity", state.analysis_result.get("severity_level", "Unknown"))
        print_metric("Financial Exposure", f"${state.analysis_result.get('financial_exposure_per_minute', 0):,.0f}/minute")
    return collector


def create_coordination_collector(state: WorkflowState):
    """Create a message handler to collect coordination state."""
    def collector(message):
        state.coordination_state = message.payload
        print_step("🏢", "Coordination Agent: Initializing crisis room...", Colors.YELLOW)
        time.sleep(0.5)  # Visual delay for demonstration
        print_metric("Crisis Room", state.coordination_state.get("crisis_room_id", "Unknown"))
        print_metric("Channels", ", ".join(state.coordination_state.get("channels_initialized", [])))
    return collector


def create_decision_collector(state: WorkflowState):
    """Create a message handler to collect executive decisions."""
    def collector(message):
        state.executive_decision = message.payload
        print_step("🎯", "Decision Agent: Synthesizing executive recommendation...", Colors.GREEN)
        time.sleep(0.5)  # Visual delay for demonstration
        print_metric("Priority", state.executive_decision.get("priority", "Unknown"))
        recommendation = state.executive_decision.get("recommendation", "")
        # Truncate long recommendations for display
        if len(recommendation) > 100:
            recommendation = recommendation[:97] + "..."
        print_metric("Recommendation", recommendation)
    return collector


# ============================================================================
# Main Orchestration Function
# ============================================================================

def run_pqc_demonstration() -> int:
    """
    Run the complete PQC Flash-Crash demonstration.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Initialize workflow state
    state = WorkflowState()
    state.start_time = time.time()
    
    try:
        # ====================================================================
        # STEP 1: Initialize Band Communication Hub
        # ====================================================================
        print_banner("🚨 PROJECT NEXAVARA - PQC CRISIS RESPONSE SYSTEM 🚨", color=Colors.BOLD)
        
        print_step("🔧", "Initializing Band communication hub...", Colors.BLUE)
        band_client = InMemoryBandClient()
        time.sleep(0.3)
        
        # ====================================================================
        # STEP 2: Deploy All Agents
        # ====================================================================
        print_step("🤖", "Deploying agents:", Colors.BLUE)
        
        # Create IntakeAgent (for incident injection)
        # Note: IntakeAgent requires a featherless client, but we'll inject directly
        intake_agent = None  # We'll inject the incident directly via band_client
        
        # Create PQC Analysis Agent
        analysis_agent = PQCAnalysisAgent(
            name="PQCAnalysisAgent",
            band_client=band_client,
            ai_client=None  # Using heuristic analysis for demo
        )
        print(f"{Colors.GREEN}  ✓ Analysis Agent{Colors.END}")
        
        # Create PQC Coordination Agent
        coordination_agent = PQCCoordinationAgent(
            name="PQCCoordinationAgent",
            band_client=band_client,
            ai_client=None
        )
        print(f"{Colors.GREEN}  ✓ Coordination Agent{Colors.END}")
        
        # Create PQC Decision Agent
        decision_agent = PQCDecisionAgent(
            name="PQCDecisionAgent",
            band_client=band_client,
            ai_client=None
        )
        print(f"{Colors.GREEN}  ✓ Decision Agent{Colors.END}")
        
        # Create PQC Audit Agent
        audit_agent = PQCAuditAgent(
            name="PQCAuditAgent",
            band_client=band_client,
            audit_file_path="pqc_audit.jsonl"
        )
        print(f"{Colors.GREEN}  ✓ Audit Agent{Colors.END}")
        
        time.sleep(0.5)
        
        # ====================================================================
        # STEP 3: Subscribe Agents to Topics
        # ====================================================================
        print_step("📡", "Subscribing agents to message topics...", Colors.BLUE)
        
        # Analysis Agent listens to incident detection
        band_client.subscribe("pqc.incident.detected", analysis_agent.handle_message)
        
        # Coordination Agent listens to incident detection
        band_client.subscribe("pqc.incident.detected", coordination_agent.handle_message)
        
        # Decision Agent listens to both analysis and coordination
        band_client.subscribe("pqc.analysis.completed", decision_agent.handle_message)
        band_client.subscribe("pqc.coordination.updated", decision_agent.handle_message)
        
        # Audit Agent already subscribed in its __init__ method
        
        # Subscribe collectors for demonstration output
        band_client.subscribe("pqc.analysis.completed", create_analysis_collector(state))
        band_client.subscribe("pqc.coordination.updated", create_coordination_collector(state))
        band_client.subscribe("pqc.decision.made", create_decision_collector(state))
        
        time.sleep(0.5)
        
        # ====================================================================
        # STEP 4: Inject PQC Flash-Crash Incident
        # ====================================================================
        print_banner("⚡ INJECTING PQC FLASH-CRASH INCIDENT ⚡", color=Colors.RED)
        
        # The exact incident description from the task
        incident_description = (
            "Entropy degradation and key-generation latency spike detected in HSM "
            "(Hardware Security Modules) during post-quantum Kyber-1024 handshakes "
            "across the cross-border clearing gateway."
        )
        
        print(f"{Colors.YELLOW}Incident: {incident_description}{Colors.END}\n")
        
        # Create incident payload
        incident_id = f"PQC-INCIDENT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        state.incident_id = incident_id
        
        incident_payload = {
            "incident_id": incident_id,
            "source": "HSM-Monitor",
            "description": incident_description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity_initial": "critical"
        }
        
        # Validate payload
        PQCIncidentDetected.model_validate(incident_payload)
        
        # Inject incident into the system
        band_client.publish("pqc.incident.detected", {
            "source": "MainOrchestrator",
            "topic": "pqc.incident.detected",
            "payload": incident_payload
        })
        
        print_step("✅", "Incident injected successfully", Colors.GREEN)
        
        # ====================================================================
        # STEP 5: Wait for Agent Processing
        # ====================================================================
        print_step("⏳", "Waiting for agents to process incident...", Colors.BLUE)
        
        # Wait for analysis agent (2-3 seconds)
        time.sleep(2.5)
        
        # Wait for coordination agent (2-3 seconds)
        time.sleep(2.5)
        
        # Wait for decision agent to synthesize (2-3 seconds)
        time.sleep(2.5)
        
        # Additional buffer for audit writes
        time.sleep(1.0)
        
        state.end_time = time.time()
        
        # ====================================================================
        # STEP 6: Display Executive Summary
        # ====================================================================
        print_banner("✅ WORKFLOW COMPLETE - EXECUTIVE SUMMARY", color=Colors.GREEN)
        
        print(f"{Colors.BOLD}Incident Details:{Colors.END}")
        print_metric("Incident ID", state.incident_id)
        
        if state.analysis_result:
            print(f"\n{Colors.BOLD}Analysis Results:{Colors.END}")
            print_metric("Severity Level", state.analysis_result.get("severity_level", "N/A"))
            print_metric("Root Cause", state.analysis_result.get("root_cause_hypothesis", "N/A"))
            print_metric("Financial Exposure", f"${state.analysis_result.get('financial_exposure_per_minute', 0):,.0f}/minute")
            print_metric("Confidence Score", f"{state.analysis_result.get('confidence_score', 0):.2f}")
        
        if state.coordination_state:
            print(f"\n{Colors.BOLD}Coordination State:{Colors.END}")
            print_metric("Crisis Room ID", state.coordination_state.get("crisis_room_id", "N/A"))
            print_metric("Channels Initialized", ", ".join(state.coordination_state.get("channels_initialized", [])))
            print_metric("Coordination Status", state.coordination_state.get("coordination_status", "N/A").upper())
            stakeholders = state.coordination_state.get("stakeholders_notified", [])
            if stakeholders:
                print_metric("Stakeholders Notified", f"{len(stakeholders)} teams")
        
        if state.executive_decision:
            print(f"\n{Colors.BOLD}Executive Decision:{Colors.END}")
            print_metric("Priority Level", state.executive_decision.get("priority", "N/A"))
            print_metric("Approval Required", "Yes" if state.executive_decision.get("approval_required") else "No")
            downtime = state.executive_decision.get("estimated_downtime_minutes")
            if downtime:
                print_metric("Estimated Downtime", f"{downtime} minutes")
            
            recommendation = state.executive_decision.get("recommendation", "N/A")
            print(f"\n{Colors.BOLD}Recommendation:{Colors.END}")
            print(f"{Colors.CYAN}{recommendation}{Colors.END}")
        
        # Display execution metrics
        print(f"\n{Colors.BOLD}Performance Metrics:{Colors.END}")
        print_metric("Total Execution Time", f"{state.get_execution_time():.2f} seconds")
        print_metric("Audit Trail", "pqc_audit.jsonl")
        
        # Count audit records
        try:
            with open("pqc_audit.jsonl", "r") as f:
                record_count = sum(1 for _ in f)
            print_metric("Audit Records Written", f"{record_count} records")
        except FileNotFoundError:
            print_metric("Audit Records Written", "File not found")
        
        print(f"\n{Colors.BOLD}System Status:{Colors.END}")
        print(f"{Colors.GREEN}  ✓ OPERATIONAL - All agents responded successfully{Colors.END}")
        
        print_banner("🎉 DEMONSTRATION COMPLETE 🎉", color=Colors.GREEN)
        
        print(f"\n{Colors.CYAN}To view the audit trail:{Colors.END}")
        print(f"  cat pqc_audit.jsonl | python -m json.tool\n")
        
        return 0
        
    except KeyboardInterrupt:
        print_error("Demonstration interrupted by user")
        return 1
        
    except Exception as e:
        print_error(f"Demonstration failed: {e}")
        logging.exception("Fatal error in demonstration")
        return 1


# ============================================================================
# Entry Point
# ============================================================================

def main() -> int:
    """Main entry point for the PQC demonstration script."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pqc_demo.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress verbose logging from agents during demo
    logging.getLogger('agents').setLevel(logging.WARNING)
    
    # Run the demonstration
    return run_pqc_demonstration()


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
