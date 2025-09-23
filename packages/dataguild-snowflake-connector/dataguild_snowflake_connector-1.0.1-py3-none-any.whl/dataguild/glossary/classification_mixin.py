"""
DataGuild Advanced Classification System (Enterprise Edition)

This module provides both configuration mixins for basic classification setup
and advanced ML-powered data classification with pattern matching, statistical analysis,
and comprehensive PII/sensitive data detection capabilities.

Features:
- Configuration mixins for easy source integration
- Pattern-based classification for common PII types
- Statistical analysis for numeric and temporal data
- ML-powered classification (mock implementation)
- Comprehensive confidence scoring and evidence tracking
- High-performance batch processing with caching
- Enhanced reporting capabilities with ClassificationReportMixin
"""

import re
import json
import hashlib
import statistics
from collections import defaultdict, Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Iterator, Union, Pattern
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, validator, root_validator

import logging

logger = logging.getLogger(__name__)


# =============================================
# Core Classification Types and Results
# =============================================

class ClassificationType(Enum):
    """Types of data classification with comprehensive PII and sensitive data coverage."""
    PII_EMAIL = "PII_EMAIL"
    PII_PHONE = "PII_PHONE"
    PII_SSN = "PII_SSN"
    PII_CREDIT_CARD = "PII_CREDIT_CARD"
    PII_NAME = "PII_NAME"
    PII_ADDRESS = "PII_ADDRESS"
    FINANCIAL_ACCOUNT = "FINANCIAL_ACCOUNT"
    FINANCIAL_ROUTING = "FINANCIAL_ROUTING"
    MEDICAL_ID = "MEDICAL_ID"
    SENSITIVE_ID = "SENSITIVE_ID"
    GEOGRAPHIC = "GEOGRAPHIC"
    TEMPORAL = "TEMPORAL"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(Enum):
    """Confidence levels for classification results."""
    VERY_HIGH = 0.95
    HIGH = 0.80
    MEDIUM = 0.60
    LOW = 0.40
    VERY_LOW = 0.20


class ClassificationSeverity(Enum):
    """Severity levels for classification violations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ClassificationResult:
    """Result of data classification with comprehensive metadata."""
    column_name: str
    classification_type: ClassificationType
    confidence: float
    method: str
    evidence: Dict[str, Any]
    sample_size: int
    timestamp: datetime = field(default_factory=datetime.now)

    def is_high_confidence(self) -> bool:
        """Check if classification has high confidence."""
        return self.confidence >= ConfidenceLevel.HIGH.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "column_name": self.column_name,
            "classification_type": self.classification_type.value,
            "confidence": self.confidence,
            "method": self.method,
            "evidence": self.evidence,
            "sample_size": self.sample_size,
            "timestamp": self.timestamp.isoformat(),
            "is_high_confidence": self.is_high_confidence()
        }


@dataclass
class ComplianceViolation:
    """Represents a compliance violation found during classification."""
    entity_name: str
    violation_type: str
    description: str
    severity: ClassificationSeverity
    regulation: Optional[str] = None
    remediation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entity_name": self.entity_name,
            "violation_type": self.violation_type,
            "description": self.description,
            "severity": self.severity.value,
            "regulation": self.regulation,
            "remediation": self.remediation,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================
# Classification Report Mixin
# =============================================

class ClassificationReportMixin:
    """
    Enhanced mixin class providing comprehensive classification reporting capabilities.

    This mixin can be added to any report class to track data classification
    results, compliance status, governance metadata, and detailed analytics.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classification tracking
        self._classification_results: List[ClassificationResult] = []
        self._compliance_violations: List[ComplianceViolation] = []
        self._governance_tags: Set[str] = set()
        self._classification_stats: Dict[str, int] = {}
        self._processing_metrics: Dict[str, Any] = {
            "total_columns_processed": 0,
            "total_tables_processed": 0,
            "processing_time_ms": 0,
            "high_confidence_results": 0,
            "pii_columns_detected": 0,
            "sensitive_tables_identified": 0
        }

        # Pattern and rule tracking
        self._detected_patterns: Dict[str, int] = {}
        self._classification_rules_applied: List[str] = []
        self._failed_classifications: List[Dict[str, Any]] = []

        # Risk assessment
        self._risk_assessment: Dict[str, Any] = {
            "overall_risk_score": 0.0,
            "critical_violations": 0,
            "high_risk_entities": [],
            "compliance_status": "UNKNOWN"
        }

    def add_classification_result(
        self,
        column_name: str,
        classification_type: Union[ClassificationType, str],
        confidence: float,
        method: str,
        evidence: Optional[Dict[str, Any]] = None,
        sample_size: int = 0
    ) -> None:
        """
        Add a classification result to the report.

        Args:
            column_name: Name of the classified column
            classification_type: Type of classification detected
            confidence: Confidence score (0.0-1.0)
            method: Method used for classification
            evidence: Supporting evidence for the classification
            sample_size: Number of samples analyzed
        """
        # Convert string to enum if necessary
        if isinstance(classification_type, str):
            try:
                classification_type = ClassificationType(classification_type.upper())
            except ValueError:
                classification_type = ClassificationType.UNKNOWN

        result = ClassificationResult(
            column_name=column_name,
            classification_type=classification_type,
            confidence=confidence,
            method=method,
            evidence=evidence or {},
            sample_size=sample_size
        )

        self._classification_results.append(result)

        # Update statistics
        type_key = classification_type.value
        self._classification_stats[type_key] = self._classification_stats.get(type_key, 0) + 1

        if result.is_high_confidence():
            self._processing_metrics["high_confidence_results"] += 1

        # Track PII detection
        if "PII_" in classification_type.value:
            self._processing_metrics["pii_columns_detected"] += 1

        # Add info message if available
        if hasattr(self, 'add_info'):
            self.add_info(
                f"Classified column '{column_name}' as {classification_type.value} (confidence: {confidence:.2f})",
                context={
                    "column": column_name,
                    "type": classification_type.value,
                    "confidence": confidence,
                    "method": method
                }
            )

    def add_compliance_violation(
        self,
        entity_name: str,
        violation_type: str,
        description: str,
        severity: Union[ClassificationSeverity, str] = ClassificationSeverity.MEDIUM,
        regulation: Optional[str] = None,
        remediation: Optional[str] = None
    ) -> None:
        """
        Add a compliance violation to the report.

        Args:
            entity_name: Entity with the violation
            violation_type: Type of violation
            description: Detailed description
            severity: Severity level
            regulation: Applicable regulation (GDPR, CCPA, etc.)
            remediation: Suggested remediation steps
        """
        # Convert string to enum if necessary
        if isinstance(severity, str):
            try:
                severity = ClassificationSeverity(severity.upper())
            except ValueError:
                severity = ClassificationSeverity.MEDIUM

        violation = ComplianceViolation(
            entity_name=entity_name,
            violation_type=violation_type,
            description=description,
            severity=severity,
            regulation=regulation,
            remediation=remediation
        )

        self._compliance_violations.append(violation)

        # Update risk assessment
        if severity == ClassificationSeverity.CRITICAL:
            self._risk_assessment["critical_violations"] += 1
            if entity_name not in self._risk_assessment["high_risk_entities"]:
                self._risk_assessment["high_risk_entities"].append(entity_name)

        # Add error/warning message if available
        if hasattr(self, 'add_error') and severity in [ClassificationSeverity.CRITICAL, ClassificationSeverity.HIGH]:
            self.add_error(
                f"Compliance violation in {entity_name}: {description}",
                context=violation.to_dict()
            )
        elif hasattr(self, 'add_warning'):
            self.add_warning(
                f"Compliance issue in {entity_name}: {description}",
                context=violation.to_dict()
            )

    def add_governance_tag(self, tag: str) -> None:
        """Add a governance tag to the report."""
        self._governance_tags.add(tag)

    def add_classification_rule(self, rule_name: str) -> None:
        """Track that a classification rule was applied."""
        if rule_name not in self._classification_rules_applied:
            self._classification_rules_applied.append(rule_name)

    def add_pattern_detection(self, pattern_name: str, count: int = 1) -> None:
        """Track detected patterns and their frequency."""
        self._detected_patterns[pattern_name] = self._detected_patterns.get(pattern_name, 0) + count

    def add_failed_classification(
        self,
        column_name: str,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track failed classification attempts."""
        self._failed_classifications.append({
            "column_name": column_name,
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        })

    def update_processing_metrics(
        self,
        columns_processed: Optional[int] = None,
        tables_processed: Optional[int] = None,
        processing_time_ms: Optional[float] = None
    ) -> None:
        """Update processing performance metrics."""
        if columns_processed is not None:
            self._processing_metrics["total_columns_processed"] += columns_processed
        if tables_processed is not None:
            self._processing_metrics["total_tables_processed"] += tables_processed
        if processing_time_ms is not None:
            self._processing_metrics["processing_time_ms"] += processing_time_ms

    def calculate_risk_score(self) -> float:
        """Calculate overall risk score based on classifications and violations."""
        if not self._classification_results and not self._compliance_violations:
            return 0.0

        risk_score = 0.0

        # Factor in PII classifications
        pii_count = sum(1 for r in self._classification_results if "PII_" in r.classification_type.value)
        if self._classification_results:
            pii_ratio = pii_count / len(self._classification_results)
            risk_score += pii_ratio * 30  # Up to 30 points for PII presence

        # Factor in compliance violations
        violation_score = 0
        for violation in self._compliance_violations:
            if violation.severity == ClassificationSeverity.CRITICAL:
                violation_score += 25
            elif violation.severity == ClassificationSeverity.HIGH:
                violation_score += 15
            elif violation.severity == ClassificationSeverity.MEDIUM:
                violation_score += 10
            else:
                violation_score += 5

        risk_score += min(violation_score, 50)  # Cap violation score at 50

        # Factor in high confidence sensitive data
        high_conf_sensitive = sum(
            1 for r in self._classification_results
            if r.is_high_confidence() and r.classification_type.value in [
                "PII_SSN", "PII_CREDIT_CARD", "FINANCIAL_ACCOUNT", "MEDICAL_ID"
            ]
        )
        risk_score += min(high_conf_sensitive * 5, 20)  # Up to 20 points

        self._risk_assessment["overall_risk_score"] = min(risk_score, 100.0)
        return self._risk_assessment["overall_risk_score"]

    def get_classification_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of classification results."""
        total_classified = len(self._classification_results)

        # Count by classification type
        type_counts = dict(self._classification_stats)

        # Count by confidence level
        confidence_distribution = {
            "very_high": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "very_low": 0
        }

        total_confidence = 0.0
        for result in self._classification_results:
            total_confidence += result.confidence
            if result.confidence >= ConfidenceLevel.VERY_HIGH.value:
                confidence_distribution["very_high"] += 1
            elif result.confidence >= ConfidenceLevel.HIGH.value:
                confidence_distribution["high"] += 1
            elif result.confidence >= ConfidenceLevel.MEDIUM.value:
                confidence_distribution["medium"] += 1
            elif result.confidence >= ConfidenceLevel.LOW.value:
                confidence_distribution["low"] += 1
            else:
                confidence_distribution["very_low"] += 1

        avg_confidence = total_confidence / total_classified if total_classified > 0 else 0.0

        return {
            "total_classified_entities": total_classified,
            "classification_types": type_counts,
            "confidence_distribution": confidence_distribution,
            "average_confidence_score": round(avg_confidence, 3),
            "high_confidence_results": self._processing_metrics["high_confidence_results"],
            "pii_columns_detected": self._processing_metrics["pii_columns_detected"],
            "governance_tags": list(self._governance_tags),
            "compliance_violations": len(self._compliance_violations),
            "detected_patterns": dict(self._detected_patterns),
            "rules_applied": len(self._classification_rules_applied),
            "failed_classifications": len(self._failed_classifications),
            "processing_metrics": dict(self._processing_metrics)
        }

    def get_sensitive_entities(self) -> List[ClassificationResult]:
        """Get entities classified as sensitive data."""
        sensitive_types = {
            ClassificationType.PII_SSN,
            ClassificationType.PII_CREDIT_CARD,
            ClassificationType.FINANCIAL_ACCOUNT,
            ClassificationType.MEDICAL_ID,
            ClassificationType.PII_EMAIL,
            ClassificationType.PII_PHONE
        }
        return [
            result for result in self._classification_results
            if result.classification_type in sensitive_types
        ]

    def get_pii_entities(self) -> List[ClassificationResult]:
        """Get entities containing PII data."""
        return [
            result for result in self._classification_results
            if "PII_" in result.classification_type.value
        ]

    def get_compliance_violations_by_severity(self, severity: ClassificationSeverity) -> List[ComplianceViolation]:
        """Get compliance violations by severity level."""
        return [
            violation for violation in self._compliance_violations
            if violation.severity == severity
        ]

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment."""
        self.calculate_risk_score()  # Update risk score

        # Determine compliance status
        critical_violations = len(self.get_compliance_violations_by_severity(ClassificationSeverity.CRITICAL))
        high_violations = len(self.get_compliance_violations_by_severity(ClassificationSeverity.HIGH))

        if critical_violations > 0:
            compliance_status = "NON_COMPLIANT"
        elif high_violations > 0:
            compliance_status = "AT_RISK"
        elif self._compliance_violations:
            compliance_status = "NEEDS_ATTENTION"
        else:
            compliance_status = "COMPLIANT"

        self._risk_assessment["compliance_status"] = compliance_status

        return {
            **self._risk_assessment,
            "sensitive_entities_count": len(self.get_sensitive_entities()),
            "pii_entities_count": len(self.get_pii_entities()),
            "critical_violations": critical_violations,
            "high_violations": high_violations,
            "total_violations": len(self._compliance_violations),
        }

    def export_classification_results(self) -> List[Dict[str, Any]]:
        """Export all classification results as dictionaries."""
        return [result.to_dict() for result in self._classification_results]

    def export_compliance_violations(self) -> List[Dict[str, Any]]:
        """Export all compliance violations as dictionaries."""
        return [violation.to_dict() for violation in self._compliance_violations]

    def get_classification_report(self) -> Dict[str, Any]:
        """Get comprehensive classification report."""
        summary = self.get_classification_summary()
        risk_assessment = self.get_risk_assessment()

        return {
            "summary": summary,
            "risk_assessment": risk_assessment,
            "classification_results": self.export_classification_results(),
            "compliance_violations": self.export_compliance_violations(),
            "governance_tags": list(self._governance_tags),
            "applied_rules": self._classification_rules_applied,
            "failed_classifications": self._failed_classifications,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on classification results."""
        recommendations = []

        # Recommend encryption for sensitive data
        sensitive_count = len(self.get_sensitive_entities())
        if sensitive_count > 0:
            recommendations.append({
                "type": "SECURITY",
                "priority": "HIGH",
                "title": "Encrypt Sensitive Data",
                "description": f"Found {sensitive_count} columns with sensitive data that should be encrypted",
                "action": "Implement column-level encryption for PII and sensitive data"
            })

        # Recommend access controls
        pii_count = len(self.get_pii_entities())
        if pii_count > 0:
            recommendations.append({
                "type": "ACCESS_CONTROL",
                "priority": "HIGH",
                "title": "Implement PII Access Controls",
                "description": f"Found {pii_count} PII columns requiring access restrictions",
                "action": "Configure role-based access controls for PII data"
            })

        # Recommend compliance review for violations
        critical_violations = len(self.get_compliance_violations_by_severity(ClassificationSeverity.CRITICAL))
        if critical_violations > 0:
            recommendations.append({
                "type": "COMPLIANCE",
                "priority": "CRITICAL",
                "title": "Address Compliance Violations",
                "description": f"Found {critical_violations} critical compliance violations",
                "action": "Immediate review and remediation of critical compliance issues required"
            })

        return recommendations

    def has_sensitive_data(self) -> bool:
        """Check if any sensitive data was classified."""
        return len(self.get_sensitive_entities()) > 0

    def has_pii_data(self) -> bool:
        """Check if any PII data was classified."""
        return len(self.get_pii_entities()) > 0

    def has_compliance_violations(self) -> bool:
        """Check if there are any compliance violations."""
        return len(self._compliance_violations) > 0

    def has_critical_violations(self) -> bool:
        """Check if there are any critical compliance violations."""
        return len(self.get_compliance_violations_by_severity(ClassificationSeverity.CRITICAL)) > 0

    def get_highest_classification_risk(self) -> Optional[ClassificationType]:
        """Get the highest risk classification type found."""
        if not self._classification_results:
            return None

        risk_order = [
            ClassificationType.UNKNOWN,
            ClassificationType.GEOGRAPHIC,
            ClassificationType.TEMPORAL,
            ClassificationType.SENSITIVE_ID,
            ClassificationType.PII_NAME,
            ClassificationType.PII_ADDRESS,
            ClassificationType.PII_EMAIL,
            ClassificationType.PII_PHONE,
            ClassificationType.FINANCIAL_ROUTING,
            ClassificationType.FINANCIAL_ACCOUNT,
            ClassificationType.MEDICAL_ID,
            ClassificationType.PII_CREDIT_CARD,
            ClassificationType.PII_SSN,
        ]

        highest_risk = ClassificationType.UNKNOWN
        for result in self._classification_results:
            if risk_order.index(result.classification_type) > risk_order.index(highest_risk):
                highest_risk = result.classification_type

        return highest_risk


# =============================================
# Configuration Classes (Keeping existing code)
# =============================================

class AllowDenyPattern(BaseModel):
    """Configuration for allow/deny regex patterns."""

    allow: List[str] = Field(
        default=[".*"],
        description="List of regex patterns to include"
    )

    deny: List[str] = Field(
        default_factory=list,
        description="List of regex patterns to exclude"
    )

    ignoreCase: bool = Field(
        default=True,
        description="Whether to ignore case sensitivity during pattern matching"
    )

    def matches(self, value: str) -> bool:
        """Check if a value matches the allow/deny patterns."""
        flags = re.IGNORECASE if self.ignoreCase else 0

        # Check deny patterns first
        for deny_pattern in self.deny:
            if re.match(deny_pattern, value, flags):
                return False

        # Check allow patterns
        for allow_pattern in self.allow:
            if re.match(allow_pattern, value, flags):
                return True

        return False


class ClassifierConfig(BaseModel):
    """Configuration for individual classifiers."""

    type: str = Field(
        description="Type of classifier (e.g., 'datahub', 'custom', 'regex')"
    )

    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Classifier-specific configuration parameters"
    )

    confidence_threshold: float = Field(
        default=0.68,
        description="Minimum confidence level for predictions (0.0-1.0)"
    )

    @validator('confidence_threshold')
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        return v


class InfoTypeConfig(BaseModel):
    """Configuration for specific information types."""

    name: str = Field(
        description="Name of the information type"
    )

    prediction_factors_and_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Factors and their weights for prediction"
    )

    exclude_names: Optional[List[str]] = Field(
        default=None,
        description="List of names to exclude from classification"
    )

    regex_patterns: Optional[List[str]] = Field(
        default=None,
        description="Regex patterns for value-based detection"
    )

    data_types: Optional[List[str]] = Field(
        default=None,
        description="Applicable data types for this info type"
    )

    custom_properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom properties for this info type"
    )


class ClassificationSourceConfig(BaseModel):
    """Configuration for automatic data classification in DataGuild sources."""

    enabled: bool = Field(
        default=False,
        description="Whether classification should be used to auto-detect glossary terms"
    )

    sample_size: int = Field(
        default=100,
        description="Number of sample values used for classification"
    )

    max_workers: Optional[int] = Field(
        default=None,
        description="Number of worker processes to use for classification"
    )

    classifiers: List[ClassifierConfig] = Field(
        default_factory=lambda: [ClassifierConfig(type="datahub")],
        description="Classifiers to use for auto-detecting glossary terms"
    )

    info_type_to_term: Dict[str, str] = Field(
        default_factory=dict,
        description="Optional mapping to provide glossary term identifier for info type"
    )

    info_types_config: Dict[str, InfoTypeConfig] = Field(
        default_factory=dict,
        description="Configuration details for specific information types"
    )

    table_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern,
        description="Regex patterns to filter tables for classification"
    )

    column_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern,
        description="Regex patterns to filter columns for classification"
    )

    minimum_values_threshold: int = Field(
        default=50,
        description="Minimum number of non-null column values required for classification"
    )

    batch_size: int = Field(
        default=1000,
        description="Number of columns to process in each batch"
    )

    cache_classification_results: bool = Field(
        default=True,
        description="Whether to cache classification results for performance"
    )

    strip_exclusion_formatting: bool = Field(
        default=True,
        description="Whether to strip formatting when checking exclusion lists"
    )

    include_column_names: bool = Field(
        default=True,
        description="Whether to include column names in classification analysis"
    )

    include_column_descriptions: bool = Field(
        default=True,
        description="Whether to include column descriptions in classification analysis"
    )

    include_data_types: bool = Field(
        default=True,
        description="Whether to include data types in classification analysis"
    )

    include_sample_values: bool = Field(
        default=True,
        description="Whether to include sample values in classification analysis"
    )

    @validator('sample_size', 'minimum_values_threshold', 'batch_size')
    def validate_positive_values(cls, v):
        """Validate that numeric values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


# =============================================
# Advanced Pattern-Based Classification
# =============================================

class ClassificationPattern(ABC):
    """Abstract base class for classification patterns."""

    def __init__(self, name: str, classification_type: ClassificationType, confidence: float):
        self.name = name
        self.classification_type = classification_type
        self.base_confidence = confidence

    @abstractmethod
    def matches_column_name(self, column_name: str) -> bool:
        """Check if pattern matches column name."""
        pass

    @abstractmethod
    def matches_sample_data(self, sample_data: List[Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """Check if pattern matches sample data. Returns (matches, confidence, evidence)."""
        pass

    def classify(self, column_name: str, sample_data: List[Any]) -> Optional[ClassificationResult]:
        """Perform classification using this pattern."""
        name_match = self.matches_column_name(column_name)
        data_matches, data_confidence, evidence = self.matches_sample_data(sample_data)

        if name_match or data_matches:
            # Calculate combined confidence
            confidence = self.base_confidence
            if name_match and data_matches:
                confidence = min(1.0, confidence * 1.2)  # Boost for both matches
            elif name_match:
                confidence *= 0.8  # Name-only match
            elif data_matches:
                confidence = data_confidence

            return ClassificationResult(
                column_name=column_name,
                classification_type=self.classification_type,
                confidence=confidence,
                method=f"pattern:{self.name}",
                evidence={
                    "name_match": name_match,
                    "data_match": data_matches,
                    **evidence
                },
                sample_size=len(sample_data)
            )

        return None


class EmailPattern(ClassificationPattern):
    """Pattern for detecting email addresses."""

    def __init__(self):
        super().__init__("email", ClassificationType.PII_EMAIL, 0.95)
        self.name_patterns = [
            re.compile(r'email', re.IGNORECASE),
            re.compile(r'e_mail', re.IGNORECASE),
            re.compile(r'mail', re.IGNORECASE),
            re.compile(r'address.*email', re.IGNORECASE)
        ]
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def matches_column_name(self, column_name: str) -> bool:
        return any(pattern.search(column_name) for pattern in self.name_patterns)

    def matches_sample_data(self, sample_data: List[Any]) -> Tuple[bool, float, Dict[str, Any]]:
        if not sample_data:
            return False, 0.0, {}

        valid_emails = 0
        total_non_null = 0

        for value in sample_data[:100]:  # Sample first 100 values
            if value is not None and str(value).strip():
                total_non_null += 1
                if self.email_regex.match(str(value).strip()):
                    valid_emails += 1

        if total_non_null == 0:
            return False, 0.0, {"reason": "no_non_null_values"}

        match_rate = valid_emails / total_non_null
        confidence = match_rate * 0.95

        evidence = {
            "valid_emails": valid_emails,
            "total_samples": total_non_null,
            "match_rate": match_rate
        }

        return match_rate > 0.8, confidence, evidence


class PhonePattern(ClassificationPattern):
    """Pattern for detecting phone numbers."""

    def __init__(self):
        super().__init__("phone", ClassificationType.PII_PHONE, 0.90)
        self.name_patterns = [
            re.compile(r'phone', re.IGNORECASE),
            re.compile(r'mobile', re.IGNORECASE),
            re.compile(r'tel', re.IGNORECASE),
            re.compile(r'number.*phone', re.IGNORECASE)
        ]
        self.phone_patterns = [
            re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'),  # US format
            re.compile(r'^\+?[1-9]\d{1,14}$'),  # International format
            re.compile(r'^[0-9]{10}$'),  # 10-digit format
        ]

    def matches_column_name(self, column_name: str) -> bool:
        return any(pattern.search(column_name) for pattern in self.name_patterns)

    def matches_sample_data(self, sample_data: List[Any]) -> Tuple[bool, float, Dict[str, Any]]:
        if not sample_data:
            return False, 0.0, {}

        valid_phones = 0
        total_non_null = 0

        for value in sample_data[:100]:
            if value is not None and str(value).strip():
                total_non_null += 1
                value_str = re.sub(r'[^\d+\-.\s()]', '', str(value).strip())
                if any(pattern.match(value_str) for pattern in self.phone_patterns):
                    valid_phones += 1

        if total_non_null == 0:
            return False, 0.0, {"reason": "no_non_null_values"}

        match_rate = valid_phones / total_non_null
        confidence = match_rate * 0.90

        evidence = {
            "valid_phones": valid_phones,
            "total_samples": total_non_null,
            "match_rate": match_rate
        }

        return match_rate > 0.8, confidence, evidence


class SSNPattern(ClassificationPattern):
    """Pattern for detecting Social Security Numbers."""

    def __init__(self):
        super().__init__("ssn", ClassificationType.PII_SSN, 0.99)
        self.name_patterns = [
            re.compile(r'ssn', re.IGNORECASE),
            re.compile(r'social.*security', re.IGNORECASE),
            re.compile(r'social.*number', re.IGNORECASE)
        ]
        self.ssn_regex = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')

    def matches_column_name(self, column_name: str) -> bool:
        return any(pattern.search(column_name) for pattern in self.name_patterns)

    def matches_sample_data(self, sample_data: List[Any]) -> Tuple[bool, float, Dict[str, Any]]:
        if not sample_data:
            return False, 0.0, {}

        valid_ssns = 0
        total_non_null = 0

        for value in sample_data[:50]:  # Smaller sample for sensitive data
            if value is not None and str(value).strip():
                total_non_null += 1
                if self.ssn_regex.match(str(value).strip()):
                    valid_ssns += 1

        if total_non_null == 0:
            return False, 0.0, {"reason": "no_non_null_values"}

        match_rate = valid_ssns / total_non_null
        confidence = match_rate * 0.99

        evidence = {
            "valid_ssns": valid_ssns,
            "total_samples": total_non_null,
            "match_rate": match_rate
        }

        return match_rate > 0.9, confidence, evidence


class CreditCardPattern(ClassificationPattern):
    """Pattern for detecting credit card numbers."""

    def __init__(self):
        super().__init__("credit_card", ClassificationType.PII_CREDIT_CARD, 0.95)
        self.name_patterns = [
            re.compile(r'credit.*card', re.IGNORECASE),
            re.compile(r'card.*number', re.IGNORECASE),
            re.compile(r'cc.*num', re.IGNORECASE)
        ]
        self.cc_regex = re.compile(r'^[0-9]{13,19}$')

    def matches_column_name(self, column_name: str) -> bool:
        return any(pattern.search(column_name) for pattern in self.name_patterns)

    def matches_sample_data(self, sample_data: List[Any]) -> Tuple[bool, float, Dict[str, Any]]:
        if not sample_data:
            return False, 0.0, {}

        valid_cards = 0
        total_non_null = 0

        for value in sample_data[:50]:
            if value is not None:
                value_str = re.sub(r'[^\d]', '', str(value))
                if value_str:
                    total_non_null += 1
                    if self.cc_regex.match(value_str) and self._luhn_check(value_str):
                        valid_cards += 1

        if total_non_null == 0:
            return False, 0.0, {"reason": "no_non_null_values"}

        match_rate = valid_cards / total_non_null
        confidence = match_rate * 0.95

        evidence = {
            "valid_cards": valid_cards,
            "total_samples": total_non_null,
            "match_rate": match_rate
        }

        return match_rate > 0.8, confidence, evidence

    def _luhn_check(self, card_number: str) -> bool:
        """Perform Luhn algorithm check for credit card validation."""
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0


# =============================================
# Statistical and ML Classification
# =============================================

class StatisticalClassifier:
    """Statistical analysis for data type classification."""

    def __init__(self):
        self.numeric_threshold = 0.8
        self.temporal_keywords = ['date', 'time', 'timestamp', 'created', 'updated', 'modified']

    def classify_numeric(self, column_name: str, sample_data: List[Any]) -> Optional[ClassificationResult]:
        """Classify numeric columns for potential financial or ID data."""
        if not sample_data:
            return None

        numeric_values = []
        for value in sample_data:
            try:
                if value is not None:
                    numeric_values.append(float(value))
            except (ValueError, TypeError):
                continue

        if len(numeric_values) / len(sample_data) < self.numeric_threshold:
            return None

        if len(numeric_values) < 2:
            return None

        # Check for ID patterns (sequential, high cardinality)
        unique_count = len(set(numeric_values))
        if unique_count / len(numeric_values) > 0.9 and all(v == int(v) for v in numeric_values):
            return ClassificationResult(
                column_name=column_name,
                classification_type=ClassificationType.SENSITIVE_ID,
                confidence=0.7,
                method="statistical:numeric_id",
                evidence={
                    "unique_ratio": unique_count / len(numeric_values),
                    "all_integers": True,
                    "sample_count": len(numeric_values)
                },
                sample_size=len(sample_data)
            )

        return None

    def classify_temporal(self, column_name: str, sample_data: List[Any]) -> Optional[ClassificationResult]:
        """Classify temporal data."""
        if not any(keyword in column_name.lower() for keyword in self.temporal_keywords):
            return None

        temporal_count = 0
        for value in sample_data[:100]:
            if value is not None:
                value_str = str(value)
                if re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{4}/\d{2}/\d{2}', value_str):
                    temporal_count += 1

        if temporal_count > 0:
            confidence = (temporal_count / min(100, len(sample_data))) * 0.8
            return ClassificationResult(
                column_name=column_name,
                classification_type=ClassificationType.TEMPORAL,
                confidence=confidence,
                method="statistical:temporal",
                evidence={
                    "temporal_matches": temporal_count,
                    "sample_size": min(100, len(sample_data))
                },
                sample_size=len(sample_data)
            )

        return None


class MLClassificationModel:
    """Mock ML classification model interface."""

    def __init__(self):
        self.model_name = "DataGuild_PII_Classifier_v1.0"
        self.enabled = False  # Would be True if real model is loaded
        self.feature_extractors = self._init_feature_extractors()

    def _init_feature_extractors(self) -> Dict[str, Any]:
        """Initialize feature extraction functions."""
        return {
            "name_features": self._extract_name_features,
            "statistical_features": self._extract_statistical_features,
            "pattern_features": self._extract_pattern_features
        }

    def classify(self, column_name: str, sample_data: List[Any]) -> Optional[ClassificationResult]:
        """Classify using ML model (mock implementation)."""
        if not self.enabled or not sample_data:
            return None

        features = self._extract_features(column_name, sample_data)
        prediction = self._mock_predict(features)

        if prediction["confidence"] > 0.8:
            return ClassificationResult(
                column_name=column_name,
                classification_type=ClassificationType(prediction["type"]),
                confidence=prediction["confidence"],
                method=f"ml:{self.model_name}",
                evidence={
                    "features": features,
                    "model_version": "1.0"
                },
                sample_size=len(sample_data)
            )

        return None

    def _extract_features(self, column_name: str, sample_data: List[Any]) -> Dict[str, float]:
        """Extract features for ML classification."""
        features = {}
        for name, extractor in self.feature_extractors.items():
            features.update(extractor(column_name, sample_data))
        return features

    def _extract_name_features(self, column_name: str, sample_data: List[Any]) -> Dict[str, float]:
        """Extract name-based features."""
        return {
            "name_length": len(column_name) / 50.0,
            "has_underscore": 1.0 if "_" in column_name else 0.0,
            "has_id": 1.0 if "id" in column_name.lower() else 0.0
        }

    def _extract_statistical_features(self, column_name: str, sample_data: List[Any]) -> Dict[str, float]:
        """Extract statistical features from sample data."""
        non_null_count = sum(1 for x in sample_data if x is not None)
        if non_null_count == 0:
            return {"null_ratio": 1.0}

        return {
            "null_ratio": 1.0 - (non_null_count / len(sample_data)),
            "unique_ratio": len(set(str(x) for x in sample_data if x is not None)) / non_null_count,
            "avg_length": sum(len(str(x)) for x in sample_data if x is not None) / non_null_count / 100.0
        }

    def _extract_pattern_features(self, column_name: str, sample_data: List[Any]) -> Dict[str, float]:
        """Extract pattern-based features."""
        features = {}

        patterns = {
            "digits": r'\d',
            "letters": r'[a-zA-Z]',
            "special_chars": r'[^a-zA-Z0-9]',
            "email_like": r'@',
            "phone_like": r'\d{3}.*\d{3}.*\d{4}'
        }

        for pattern_name, pattern in patterns.items():
            count = 0
            for value in sample_data[:50]:
                if value is not None and re.search(pattern, str(value)):
                    count += 1
            features[f"pattern_{pattern_name}"] = count / min(50, len(sample_data))

        return features

    def _mock_predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Mock ML prediction."""
        if features.get("pattern_email_like", 0) > 0.5:
            return {"type": "PII_EMAIL", "confidence": 0.9}
        elif features.get("pattern_phone_like", 0) > 0.3:
            return {"type": "PII_PHONE", "confidence": 0.85}
        elif features.get("has_id", 0) > 0 and features.get("unique_ratio", 0) > 0.8:
            return {"type": "SENSITIVE_ID", "confidence": 0.75}

        return {"type": "UNKNOWN", "confidence": 0.1}


# =============================================
# Main Classification Handler with Enhanced Reporting
# =============================================

class ClassificationHandler:
    """
    Advanced classification handler with pattern matching, statistical analysis,
    ML-based classification capabilities, and comprehensive reporting.
    """

    def __init__(self, config: Any, report: Any):
        self.config = config
        self.report = report
        self.enabled = getattr(config, 'enable_classification', False)

        # Initialize classification patterns
        self.patterns = [
            EmailPattern(),
            PhonePattern(),
            SSNPattern(),
            CreditCardPattern(),
        ]

        # Initialize statistical classifier
        self.statistical_classifier = StatisticalClassifier()

        # Initialize ML classifier
        self.ml_classifier = MLClassificationModel()

        # Performance tracking
        self.classifications_performed = 0
        self.high_confidence_results = 0
        self.processing_time_ms = 0

    def is_classification_enabled(self) -> bool:
        """Check if classification is enabled."""
        return self.enabled

    def classify_dataset(
            self,
            dataset_urn: str,
            data_reader: Any,
            table_path: List[str]
    ) -> List[ClassificationResult]:
        """Classify all columns in a dataset with enhanced reporting."""
        if not self.enabled:
            return []

        start_time = datetime.now()
        results = []

        try:
            # Get sample data from data reader
            sample_data = data_reader.get_sample_data(dataset_urn, limit=1000)

            if not sample_data:
                logger.debug(f"No sample data available for classification: {dataset_urn}")
                return []

            # Add to report if it has the mixin
            if hasattr(self.report, 'update_processing_metrics'):
                self.report.update_processing_metrics(tables_processed=1)

            # Classify each column
            for column_name, column_data in sample_data.items():
                column_results = self.classify_column(column_name, column_data)
                results.extend(column_results)
                self.classifications_performed += 1

                # Add results to report if it has the mixin
                if hasattr(self.report, 'add_classification_result'):
                    for result in column_results:
                        self.report.add_classification_result(
                            column_name=result.column_name,
                            classification_type=result.classification_type,
                            confidence=result.confidence,
                            method=result.method,
                            evidence=result.evidence,
                            sample_size=result.sample_size
                        )

                        # Add compliance violations for sensitive data
                        if result.classification_type in [ClassificationType.PII_SSN, ClassificationType.PII_CREDIT_CARD]:
                            if hasattr(self.report, 'add_compliance_violation'):
                                self.report.add_compliance_violation(
                                    entity_name=f"{dataset_urn}.{column_name}",
                                    violation_type="SENSITIVE_DATA_UNPROTECTED",
                                    description=f"Column contains {result.classification_type.value} data that may require special protection",
                                    severity=ClassificationSeverity.HIGH,
                                    remediation="Consider implementing encryption, access controls, or data masking"
                                )

            # Update metrics
            self.high_confidence_results += sum(1 for r in results if r.is_high_confidence())

            # Update report metrics
            if hasattr(self.report, 'update_processing_metrics'):
                self.report.update_processing_metrics(columns_processed=len(sample_data))

        except Exception as e:
            logger.error(f"Classification failed for dataset {dataset_urn}: {e}")

            # Add failed classification to report
            if hasattr(self.report, 'add_failed_classification'):
                self.report.add_failed_classification(
                    column_name=dataset_urn,
                    error=str(e),
                    context={"dataset_urn": dataset_urn, "table_path": table_path}
                )

        # Track processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.processing_time_ms += processing_time

        if hasattr(self.report, 'update_processing_metrics'):
            self.report.update_processing_metrics(processing_time_ms=processing_time)

        if results:
            logger.info(f"Classification completed: {len(results)} classifications found for {dataset_urn}")

        return results

    def classify_column(self, column_name: str, sample_data: List[Any]) -> List[ClassificationResult]:
        """Classify a single column using multiple methods."""
        results = []

        if not sample_data:
            return results

        # 1. Pattern-based classification
        for pattern in self.patterns:
            result = pattern.classify(column_name, sample_data)
            if result:
                results.append(result)

                # Track pattern detection in report
                if hasattr(self.report, 'add_pattern_detection'):
                    self.report.add_pattern_detection(pattern.name)

        # 2. Statistical classification
        stat_result = self.statistical_classifier.classify_numeric(column_name, sample_data)
        if stat_result:
            results.append(stat_result)

        temporal_result = self.statistical_classifier.classify_temporal(column_name, sample_data)
        if temporal_result:
            results.append(temporal_result)

        # 3. ML-based classification
        ml_result = self.ml_classifier.classify(column_name, sample_data)
        if ml_result:
            results.append(ml_result)

        # Return only high-confidence results to avoid noise
        high_confidence_results = [r for r in results if r.confidence >= ConfidenceLevel.MEDIUM.value]

        # If multiple results, keep the highest confidence one
        if len(high_confidence_results) > 1:
            high_confidence_results.sort(key=lambda r: r.confidence, reverse=True)
            return [high_confidence_results[0]]

        return high_confidence_results

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification performance statistics."""
        return {
            "enabled": self.enabled,
            "classifications_performed": self.classifications_performed,
            "high_confidence_results": self.high_confidence_results,
            "total_processing_time_ms": self.processing_time_ms,
            "avg_processing_time_ms": (
                self.processing_time_ms / self.classifications_performed
                if self.classifications_performed > 0 else 0
            ),
            "high_confidence_rate": (
                self.high_confidence_results / self.classifications_performed
                if self.classifications_performed > 0 else 0
            )
        }


# =============================================
# Configuration Mixin Classes
# =============================================

class ClassificationSourceConfigMixin(BaseModel):
    """Mixin class that adds classification configuration to source configs."""

    classification: Optional[ClassificationSourceConfig] = Field(
        default=None,
        description="Configuration for automatic data classification"
    )

    def is_classification_enabled(self) -> bool:
        """Check if classification is enabled for this source."""
        return (
            self.classification is not None
            and self.classification.enabled
        )

    def get_classification_sample_size(self) -> int:
        """Get the sample size for classification."""
        if not self.is_classification_enabled():
            return 100
        return self.classification.sample_size

    def get_classification_max_workers(self) -> Optional[int]:
        """Get the maximum number of workers for classification."""
        if not self.is_classification_enabled():
            return None
        return self.classification.max_workers

    def should_classify_table(self, table_name: str) -> bool:
        """Check if a specific table should be classified."""
        if not self.is_classification_enabled():
            return False
        return self.classification.table_pattern.matches(table_name)

    def should_classify_column(self, column_name: str) -> bool:
        """Check if a specific column should be classified."""
        if not self.is_classification_enabled():
            return False
        return self.classification.column_pattern.matches(column_name)

    def get_classification_info_types(self) -> List[str]:
        """Get the list of configured information types."""
        if not self.is_classification_enabled():
            return []
        return list(self.classification.info_types_config.keys())

    def get_classification_glossary_term(self, info_type: str) -> str:
        """Get the glossary term for a detected information type."""
        if not self.is_classification_enabled():
            return info_type
        return self.classification.info_type_to_term.get(info_type, info_type)

    def create_default_classification_config(self) -> ClassificationSourceConfig:
        """Create a default classification configuration."""
        if self.classification is None:
            self.classification = ClassificationSourceConfig()
        return self.classification


# =============================================
# Workunit Processing Integration
# =============================================

def classification_workunit_processor(
        workunit_generator: Iterator[Any],
        classification_handler: ClassificationHandler,
        data_reader: Any,
        table_path: List[str]
) -> Iterator[Any]:
    """
    Process workunits with classification enhancement.

    This function wraps the original workunit generator and adds
    classification workunits when classification is enabled.
    """
    for workunit in workunit_generator:
        # Always yield the original workunit
        yield workunit

        # Add classification if enabled
        if not classification_handler.is_classification_enabled():
            continue

        # Extract dataset URN from workunit
        dataset_urn = getattr(workunit, 'entityUrn', None)
        if not dataset_urn:
            continue

        try:
            # Perform classification
            classification_results = classification_handler.classify_dataset(
                dataset_urn, data_reader, table_path
            )

            # Generate classification workunits
            for result in classification_results:
                classification_workunit = _create_classification_workunit(result, dataset_urn)
                if classification_workunit:
                    yield classification_workunit

        except Exception as e:
            logger.error(f"Classification processing failed for {dataset_urn}: {e}")


def _create_classification_workunit(
        classification_result: ClassificationResult,
        dataset_urn: str
) -> Optional[Any]:
    """Create a classification workunit from classification result."""
    try:
        from dataguild.emitter.mcp import MetadataChangeProposalWrapper
        from dataguild.metadata.schemas import DatasetClassification

        # Create classification aspect
        classification_aspect = DatasetClassification(
            classificationName=classification_result.classification_type.value,
            confidence=classification_result.confidence,
            method=classification_result.method,
            evidence=classification_result.evidence,
            timestamp=classification_result.timestamp
        )

        # Create workunit
        return MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=classification_aspect
        ).as_workunit()

    except Exception as e:
        logger.error(f"Failed to create classification workunit: {e}")
        return None


# =============================================
# Utility Functions
# =============================================

def create_datahub_classifier(confidence_threshold: float = 0.68) -> ClassifierConfig:
    """Create a DataHub classifier configuration."""
    return ClassifierConfig(
        type="datahub",
        confidence_threshold=confidence_threshold,
        config={
            "strip_exclusion_formatting": True,
            "minimum_values_threshold": 50
        }
    )


def create_regex_classifier(
    info_type: str,
    regex_patterns: List[str],
    confidence_threshold: float = 0.9
) -> ClassifierConfig:
    """Create a regex-based classifier configuration."""
    return ClassifierConfig(
        type="regex",
        confidence_threshold=confidence_threshold,
        config={
            "info_type": info_type,
            "patterns": regex_patterns
        }
    )


def create_pii_classification_config(
    enabled: bool = True,
    sample_size: int = 100,
    confidence_threshold: float = 0.75
) -> ClassificationSourceConfig:
    """Create a classification configuration optimized for PII detection."""
    return ClassificationSourceConfig(
        enabled=enabled,
        sample_size=sample_size,
        classifiers=[
            create_datahub_classifier(confidence_threshold)
        ],
        info_types_config={
            "Email_Address": InfoTypeConfig(
                name="Email_Address",
                prediction_factors_and_weights={
                    "name": 0.3,
                    "values": 0.7
                }
            ),
            "Phone_Number": InfoTypeConfig(
                name="Phone_Number",
                prediction_factors_and_weights={
                    "name": 0.4,
                    "values": 0.6
                }
            ),
            "US_Social_Security_Number": InfoTypeConfig(
                name="US_Social_Security_Number",
                prediction_factors_and_weights={
                    "name": 0.5,
                    "values": 0.5
                }
            )
        },
        minimum_values_threshold=25,
        include_sample_values=True,
        include_column_names=True
    )


# Export all classes and functions
__all__ = [
    # Core types and results
    'ClassificationType',
    'ConfidenceLevel',
    'ClassificationSeverity',
    'ClassificationResult',
    'ComplianceViolation',

    # Enhanced reporting mixin
    'ClassificationReportMixin',

    # Configuration classes
    'AllowDenyPattern',
    'ClassifierConfig',
    'InfoTypeConfig',
    'ClassificationSourceConfig',
    'ClassificationSourceConfigMixin',

    # Pattern classes
    'ClassificationPattern',
    'EmailPattern',
    'PhonePattern',
    'SSNPattern',
    'CreditCardPattern',

    # Classification engines
    'StatisticalClassifier',
    'MLClassificationModel',
    'ClassificationHandler',

    # Workunit processing
    'classification_workunit_processor',

    # Utility functions
    'create_datahub_classifier',
    'create_regex_classifier',
    'create_pii_classification_config',
]
