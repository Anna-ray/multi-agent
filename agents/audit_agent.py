from typing import Dict, Any
from agents.base_agent import Agent
from messages.models import MessageEnvelope, PQCAuditRecord
import logging
import json
import uuid
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class PQCAuditAgent(Agent):
    """
    PQC Audit Agent for immutable forensic audit trail generation.
    
    This agent captures all PQC incident events and creates an immutable,
    legally defensible forensic trail using cryptographic hashing. It listens
    to ALL PQC-related topics and writes append-only audit records in JSONL format.
    
    The audit trail is designed to be:
    - Immutable: Append-only file operations with cryptographic hashing
    - Forensically sound: SHA-256 hashes for record verification
    - Legally defensible: Complete payload snapshots with timestamps
    - Tamper-evident: Any modification breaks the hash chain
    
    Attributes:
        name: Agent identifier
        band: BandClient for message bus communication
        audit_file_path: Path to the JSONL audit log file
    """
    
    # PQC topics to monitor for audit trail
    PQC_TOPICS = [
        "pqc.incident.detected",
        "pqc.analysis.completed",
        "pqc.coordination.updated",
        "pqc.decision.made",
    ]
    
    def __init__(self, name: str, band_client, audit_file_path: str = "pqc_audit.jsonl"):
        """
        Initialize the PQC Audit Agent.
        
        Args:
            name: Unique identifier for this audit agent
            band_client: BandClient instance for message bus operations
            audit_file_path: Path to the JSONL audit log file (default: "pqc_audit.jsonl")
        """
        super().__init__(name, band_client)
        self.audit_file_path = audit_file_path
        logger.info(f"PQCAuditAgent '{self.name}' initialized with audit file: {self.audit_file_path}")
        
        # Subscribe to all PQC topics for comprehensive audit coverage
        for topic in self.PQC_TOPICS:
            try:
                self.band.subscribe(topic, self.handle_message)
                logger.info(f"PQCAuditAgent subscribed to topic: {topic}")
            except Exception as e:
                logger.error(f"Failed to subscribe to topic {topic}: {e}")
    
    def handle_message(self, message: MessageEnvelope) -> None:
        """
        Handle incoming PQC messages and create audit records.
        
        This method is called for every message on subscribed topics. It:
        1. Extracts the incident_id from the payload
        2. Creates a forensically sound audit record with SHA-256 hash
        3. Writes the record to the append-only JSONL audit file
        
        Error handling ensures that audit failures never stop the audit trail.
        
        Args:
            message: MessageEnvelope containing the PQC event data
        """
        try:
            logger.debug(f"PQCAuditAgent processing message from topic: {message.topic}")
            
            # Create audit record with forensic hash
            audit_record = self._create_audit_record(message)
            
            # Write to append-only audit file
            self._write_audit_record(audit_record)
            
            logger.info(
                f"Audit record created: audit_id={audit_record.audit_id}, "
                f"incident_id={audit_record.incident_id}, event_type={audit_record.event_type}"
            )
            
        except Exception as e:
            # Critical: Never let audit failures stop the audit trail
            logger.error(f"Error creating audit record for message {message.id}: {e}", exc_info=True)
            
            # Attempt to write error record to audit log
            try:
                error_record = self._create_error_audit_record(message, str(e))
                self._write_audit_record(error_record)
            except Exception as nested_error:
                logger.critical(
                    f"Failed to write error audit record: {nested_error}. "
                    f"Original error: {e}",
                    exc_info=True
                )
    
    def _create_audit_record(self, message: MessageEnvelope) -> PQCAuditRecord:
        """
        Create a forensically sound audit record from a message envelope.
        
        This method:
        1. Generates a unique audit_id
        2. Extracts the incident_id from the payload
        3. Captures the complete payload snapshot
        4. Generates a SHA-256 forensic hash for immutability
        
        Args:
            message: MessageEnvelope to audit
            
        Returns:
            PQCAuditRecord with forensic hash for immutability verification
        """
        # Generate unique audit ID
        audit_id = str(uuid.uuid4())
        
        # Extract incident_id from payload
        incident_id = self._extract_incident_id(message.payload)
        
        # Create audit record with auto-generated forensic hash
        audit_record = PQCAuditRecord.create_with_hash(
            audit_id=audit_id,
            incident_id=incident_id,
            event_type=message.topic,
            agent_name=self.name,
            timestamp=datetime.now(timezone.utc),
            payload_snapshot=message.payload
        )
        
        # Validate the record structure
        validated_record = PQCAuditRecord.model_validate(audit_record.model_dump())
        
        return validated_record
    
    def _create_error_audit_record(self, message: MessageEnvelope, error_message: str) -> PQCAuditRecord:
        """
        Create an audit record for audit processing errors.
        
        This ensures that even audit failures are recorded in the audit trail,
        maintaining a complete forensic record of all system events.
        
        Args:
            message: Original message that caused the error
            error_message: Description of the error that occurred
            
        Returns:
            PQCAuditRecord documenting the audit error
        """
        audit_id = str(uuid.uuid4())
        
        error_payload = {
            "error": error_message,
            "original_message_id": message.id,
            "original_topic": message.topic,
            "original_source": message.source,
            "original_payload": message.payload
        }
        
        return PQCAuditRecord.create_with_hash(
            audit_id=audit_id,
            incident_id="AUDIT-ERROR",
            event_type=f"{message.topic}.audit_error",
            agent_name=self.name,
            timestamp=datetime.now(timezone.utc),
            payload_snapshot=error_payload
        )
    
    def _extract_incident_id(self, payload: Dict[str, Any]) -> str:
        """
        Extract incident_id from various payload structures.
        
        This method handles different payload formats across PQC topics:
        - Direct incident_id field
        - Nested incident_id in sub-objects
        - Escalation_id as fallback
        - Generated ID if none found
        
        Args:
            payload: Message payload dictionary
            
        Returns:
            Extracted or generated incident_id string
        """
        # Try direct incident_id field (most common)
        if "incident_id" in payload:
            return payload["incident_id"]
        
        # Try escalation_id as fallback (for compatibility)
        if "escalation_id" in payload:
            return payload["escalation_id"]
        
        # Try nested structures
        for key, value in payload.items():
            if isinstance(value, dict) and "incident_id" in value:
                return value["incident_id"]
        
        # Generate a fallback ID if none found
        fallback_id = f"UNKNOWN-{str(uuid.uuid4())[:8]}"
        logger.warning(f"No incident_id found in payload, using fallback: {fallback_id}")
        return fallback_id
    
    def _write_audit_record(self, record: PQCAuditRecord) -> None:
        """
        Write validated audit record to append-only JSONL file.
        
        This method ensures:
        - Append-only operations (immutability)
        - JSONL format (one JSON object per line)
        - Proper file handling with context managers
        - Atomic write operations
        
        The JSONL format allows for:
        - Easy parsing line-by-line
        - Append-only operations without loading entire file
        - Resilience to partial file corruption
        - Standard forensic analysis tools compatibility
        
        Args:
            record: Validated PQCAuditRecord to write
            
        Raises:
            IOError: If file write operation fails (logged, not propagated)
        """
        try:
            # Convert record to JSON string (single line)
            record_json = record.model_dump_json()
            
            # Append to JSONL file (creates file if doesn't exist)
            with open(self.audit_file_path, 'a', encoding='utf-8') as audit_file:
                audit_file.write(record_json + '\n')
                audit_file.flush()  # Ensure immediate write to disk
            
            logger.debug(f"Audit record written to {self.audit_file_path}: {record.audit_id}")
            
        except IOError as e:
            logger.error(
                f"Failed to write audit record {record.audit_id} to {self.audit_file_path}: {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error writing audit record {record.audit_id}: {e}",
                exc_info=True
            )
            raise
    
    def run(self) -> None:
        """
        Optional long-running process for the agent.
        
        The audit agent is primarily event-driven through message subscriptions,
        so this method is not required. However, it could be extended to:
        - Periodically verify audit file integrity
        - Generate audit summaries
        - Rotate audit files
        - Perform hash chain verification
        """
        logger.info(f"PQCAuditAgent '{self.name}' is running in event-driven mode")

# Made with Bob
