"""
Audit Logging System for NobleLogic Trading
Comprehensive audit trail for compliance, monitoring, and debugging
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum
import os
import threading
from pathlib import Path

class AuditEvent(Enum):
    """Audit event types for structured logging"""
    TRADE_EXECUTION = "trade_execution"
    RISK_ASSESSMENT = "risk_assessment"
    ML_PREDICTION = "ml_prediction"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIG_CHANGE = "config_change"
    USER_ACTION = "user_action"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"
    DATA_ACCESS = "data_access"
    MODEL_UPDATE = "model_update"

class AuditLogger:
    """
    Centralized audit logging system with structured JSON logging
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.logger = None
        self.log_directory = Path("logs/audit")
        self.setup_logger()

    def setup_logger(self):
        """Setup the audit logger with rotating file handler"""
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('noblelogic_audit')
        self.logger.setLevel(logging.INFO)

        # Remove any existing handlers
        self.logger.handlers.clear()

        # Create rotating file handler
        log_file = self.log_directory / "audit.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=30  # Keep 30 days of logs
        )
        handler.setLevel(logging.INFO)

        # Create formatter for structured JSON logging
        formatter = AuditFormatter()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # Also log to console for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(event_type)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_event(self, event_type: AuditEvent, message: str,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  component: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  severity: str = "INFO"):
        """
        Log an audit event

        Args:
            event_type: Type of audit event
            message: Human-readable message
            user_id: User identifier (if applicable)
            session_id: Session identifier
            component: System component (e.g., 'ml_engine', 'risk_assessment')
            metadata: Additional structured data
            severity: Log level (INFO, WARNING, ERROR, CRITICAL)
        """
        if self.logger is None:
            self.setup_logger()

        # Create audit record
        audit_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value,
            'message': message,
            'severity': severity,
            'component': component or 'unknown',
            'user_id': user_id,
            'session_id': session_id,
            'metadata': metadata or {},
            'process_id': os.getpid(),
            'thread_id': threading.get_ident()
        }

        # Log based on severity
        log_method = {
            'DEBUG': self.logger.debug,
            'INFO': self.logger.info,
            'WARNING': self.logger.warning,
            'ERROR': self.logger.error,
            'CRITICAL': self.logger.critical
        }.get(severity.upper(), self.logger.info)

        # Use the message as the log message, audit record goes in extra
        log_method(message, extra={'audit_record': audit_record})

    def log_trade_execution(self, symbol: str, side: str, quantity: float,
                           price: float, order_type: str,
                           strategy: str = None, confidence: float = None,
                           user_id: str = None, session_id: str = None):
        """Log trade execution events"""
        self.log_event(
            AuditEvent.TRADE_EXECUTION,
            f"Trade executed: {side} {quantity} {symbol} at {price}",
            user_id=user_id,
            session_id=session_id,
            component="trading_engine",
            metadata={
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'order_type': order_type,
                'strategy': strategy,
                'confidence': confidence
            }
        )

    def log_risk_assessment(self, symbol: str, risk_level: str,
                           position_size: float, confidence: float,
                           risk_metrics: Dict[str, Any],
                           user_id: str = None, session_id: str = None):
        """Log risk assessment events"""
        self.log_event(
            AuditEvent.RISK_ASSESSMENT,
            f"Risk assessment: {symbol} - Level: {risk_level}, Position: {position_size}",
            user_id=user_id,
            session_id=session_id,
            component="risk_assessment",
            metadata={
                'symbol': symbol,
                'risk_level': risk_level,
                'position_size': position_size,
                'confidence': confidence,
                'risk_metrics': risk_metrics
            }
        )

    def log_ml_prediction(self, symbol: str, prediction: Dict[str, Any],
                         confidence: float, features_used: list,
                         model_version: str = None,
                         user_id: str = None, session_id: str = None):
        """Log ML prediction events"""
        self.log_event(
            AuditEvent.ML_PREDICTION,
            f"ML prediction: {symbol} - Action: {prediction.get('action', 'unknown')}, Confidence: {confidence:.3f}",
            user_id=user_id,
            session_id=session_id,
            component="ml_engine",
            metadata={
                'symbol': symbol,
                'prediction': prediction,
                'confidence': confidence,
                'features_used': features_used,
                'model_version': model_version
            }
        )

    def log_error(self, error_message: str, error_type: str,
                  component: str, stack_trace: str = None,
                  user_id: str = None, session_id: str = None):
        """Log error events"""
        self.log_event(
            AuditEvent.ERROR_OCCURRED,
            f"Error in {component}: {error_message}",
            user_id=user_id,
            session_id=session_id,
            component=component,
            severity="ERROR",
            metadata={
                'error_type': error_type,
                'stack_trace': stack_trace
            }
        )

    def log_performance_metric(self, metric_name: str, value: Any,
                              component: str, metadata: Dict[str, Any] = None,
                              user_id: str = None, session_id: str = None):
        """Log performance metrics"""
        self.log_event(
            AuditEvent.PERFORMANCE_METRIC,
            f"Performance metric: {metric_name} = {value}",
            user_id=user_id,
            session_id=session_id,
            component=component,
            metadata={
                'metric_name': metric_name,
                'value': value,
                'additional_data': metadata or {}
            }
        )

    def log_security_event(self, event_type: str, description: str,
                          user_id: str = None, session_id: str = None,
                          ip_address: str = None, metadata: Dict[str, Any] = None):
        """Log security-related events"""
        self.log_event(
            AuditEvent.SECURITY_EVENT,
            f"Security event: {event_type} - {description}",
            user_id=user_id,
            session_id=session_id,
            component="security",
            severity="WARNING",
            metadata={
                'event_type': event_type,
                'ip_address': ip_address,
                'additional_data': metadata or {}
            }
        )

    def log_system_event(self, event_type: AuditEvent, message: str,
                        component: str = "system", metadata: Dict[str, Any] = None):
        """Log system-level events"""
        self.log_event(
            event_type,
            message,
            component=component,
            metadata=metadata or {}
        )

class AuditFormatter(logging.Formatter):
    """Custom formatter for audit logs"""

    def format(self, record):
        # Get the audit record from the log record
        audit_record = getattr(record, 'audit_record', None)
        if audit_record:
            # Return JSON formatted audit record
            return json.dumps(audit_record, default=str)
        else:
            # Fallback to standard formatting
            return super().format(record)

# Global audit logger instance
audit_logger = AuditLogger()

# Convenience functions for easy access
def log_trade_execution(*args, **kwargs):
    """Convenience function for trade execution logging"""
    audit_logger.log_trade_execution(*args, **kwargs)

def log_risk_assessment(*args, **kwargs):
    """Convenience function for risk assessment logging"""
    audit_logger.log_risk_assessment(*args, **kwargs)

def log_ml_prediction(*args, **kwargs):
    """Convenience function for ML prediction logging"""
    audit_logger.log_ml_prediction(*args, **kwargs)

def log_error(*args, **kwargs):
    """Convenience function for error logging"""
    audit_logger.log_error(*args, **kwargs)

def log_performance_metric(*args, **kwargs):
    """Convenience function for performance metric logging"""
    audit_logger.log_performance_metric(*args, **kwargs)

def log_security_event(*args, **kwargs):
    """Convenience function for security event logging"""
    audit_logger.log_security_event(*args, **kwargs)

def log_system_event(*args, **kwargs):
    """Convenience function for system event logging"""
    audit_logger.log_system_event(*args, **kwargs)

# Initialize audit logging on import
audit_logger.log_system_event(
    AuditEvent.SYSTEM_STARTUP,
    "Audit logging system initialized",
    component="audit_system"
)