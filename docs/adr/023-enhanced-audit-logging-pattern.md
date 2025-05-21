# ADR-023: Enhanced Audit Logging Pattern

## Status
**Accepted** - 2025-05-20

## Context
While ADR-016 (Structured Logging and Observability Pattern) established general JSON logging guidelines, the Storage Service implementation revealed the need for more sophisticated audit logging patterns for data governance and compliance.

Storage operations involve varying levels of risk and business impact. Standard informational logging is insufficient for tracking destructive operations, compliance events, and data lifecycle changes that require detailed audit trails.

## Decision
Implement enhanced audit logging with operation-specific log levels, risk indicators, and contextual metadata that supports compliance, governance, and operational monitoring requirements.

## Implementation

### Log Level Strategy by Operation Type

#### Read Operations (INFO Level)
```python
logger.info(
    f"Fetching {len(record_ids)} records",
    extra={
        "record_count": len(record_ids),
        "operation": "fetch_records",
        "attributes": attributes
    }
)
```

#### Write Operations (INFO Level)
```python
logger.info(
    f"Creating/updating {len(records)} records",
    extra={
        "record_count": len(records),
        "operation": "create_update_records",
        "has_ids": any(record.get("id") for record in records),
        "skip_dupes": skip_dupes
    }
)
```

#### Delete Operations (WARNING Level)
```python
logger.warning(
    f"Deleting record {id}",
    extra={
        "record_id": id,
        "operation": "delete_record",
        "destructive": True
    }
)
```

#### Purge Operations (ERROR Level)
```python
logger.error(
    f"Purging record {id} permanently",
    extra={
        "record_id": id,
        "operation": "purge_record",
        "destructive": True,
        "permanent": True
    }
)
```

### Risk Indicator Pattern

#### Destructive Operation Markers
```python
# Standard metadata for all destructive operations
{
    "destructive": True,           # Indicates data loss potential
    "permanent": True,            # Indicates irreversible operation (for purge)
    "operation": "purge_record",  # Standardized operation identifier
    "record_id": "123456",        # Entity identifier for audit trail
}
```

#### Business Impact Indicators
```python
# For operations affecting multiple entities
{
    "operation": "delete_legal_tag",
    "tag_name": "opendes-Private-US-Data",
    "partition": "opendes",
    "warning": "Associated data is now invalid",
    "cascading_effect": True      # Indicates broader impact
}
```

### Contextual Metadata Standards

#### Required Fields for All Operations
- `operation`: Standardized operation identifier
- `partition`: Data partition context
- `user`: Authenticated user context (when available)

#### Entity-Specific Fields
- `record_id`: For single record operations
- `record_count`: For batch operations
- `tag_name`: For legal tag operations
- `schema_id`: For schema operations

#### Operation-Specific Fields
- `destructive`: Boolean indicator for destructive operations
- `permanent`: Boolean indicator for irreversible operations
- `cascading_effect`: Boolean indicator for operations affecting multiple entities
- `has_ids`: Boolean indicator for batch operations with pre-assigned IDs
- `skip_dupes`: Boolean indicator for duplicate handling strategy

### Audit Trail Integration

#### Structured Audit Logging
```python
# Audit-specific logging (beyond operational logging)
logger.audit(
    "Legal tag deleted",
    extra={
        "operation": "delete_legal_tag",
        "tag_name": name,
        "partition": partition,
        "user": "authenticated_user",  # Should be extracted from auth context
        "warning": "Associated data is now invalid"
    }
)
```

#### Success vs. Failure Logging
```python
try:
    result = await self.delete_record(id)
    logger.warning(
        f"Successfully deleted record {id}",
        extra={
            "record_id": id,
            "operation": "delete_record",
            "destructive": True,
            "status": "success"
        }
    )
except Exception as e:
    logger.error(
        f"Failed to delete record {id}: {e}",
        extra={
            "record_id": id,
            "operation": "delete_record",
            "destructive": True,
            "status": "failure",
            "error": str(e)
        }
    )
    raise
```

## Log Level Guidelines

### INFO Level
- **Read Operations**: Record retrieval, listing, querying
- **Successful Write Operations**: Create, update operations
- **Configuration Changes**: Non-destructive parameter changes
- **System Events**: Service startup, health checks

### WARNING Level
- **Logical Delete Operations**: Reversible delete operations
- **Permission Denials**: Write/delete operations blocked by permissions
- **Validation Failures**: Record validation errors
- **Configuration Issues**: Non-critical configuration problems

### ERROR Level
- **Permanent Delete Operations**: Irreversible purge operations
- **System Failures**: API errors, authentication failures
- **Data Integrity Issues**: Validation failures with data impact
- **Critical Permission Issues**: Security-related access denials

### CRITICAL Level (Reserved)
- **System Compromise**: Security breaches, unauthorized access
- **Data Corruption**: Detected data integrity violations
- **Service Outages**: Complete service failures

## Compliance Integration

### GDPR/Data Protection Logging
```python
# For operations involving personal data
{
    "operation": "purge_record",
    "record_id": id,
    "data_classification": "personal_data",
    "legal_basis": "gdpr_right_to_erasure",
    "retention_policy": "expired"
}
```

### SOX/Financial Compliance
```python
# For operations affecting financial data
{
    "operation": "update_record",
    "record_id": id,
    "financial_data": True,
    "approval_required": True,
    "compliance_framework": "sox"
}
```

## Rationale
1. **Compliance Support**: Detailed audit trails for regulatory requirements
2. **Risk-Based Logging**: Appropriate log levels based on operation risk
3. **Operational Monitoring**: Clear indicators for monitoring and alerting
4. **Forensic Analysis**: Rich context for incident investigation
5. **Data Governance**: Support for data lifecycle management
6. **Performance Optimization**: Structured logging enables efficient log analysis

## Implementation Guidelines

### Metadata Consistency
- Use consistent field names across all operations
- Include operation identifier in all log entries
- Provide entity identifiers for audit trail continuity
- Include user context when available

### Log Message Format
```
{operation_description} [{entity_identifier}]
```

Examples:
- "Creating/updating 5 records"
- "Deleting record rec123456"
- "Purging record rec789012 permanently"

### Context Preservation
- Include partition information for multi-tenant scenarios
- Preserve operation context through async call stacks
- Include correlation IDs for distributed tracing
- Maintain audit trail across service boundaries

## Monitoring and Alerting Integration

### Alert Triggers
- **ERROR Level**: Immediate alerts for destructive operations
- **WARNING Level**: Delayed alerts for operational issues
- **Pattern Detection**: Unusual patterns in destructive operations
- **Volume Thresholds**: Excessive deletion or purge operations

### Metrics Extraction
- Count of destructive operations by type
- Success/failure rates for critical operations
- User activity patterns for compliance monitoring
- Resource utilization trends

## Consequences

**Positive:**
- Enhanced compliance and audit capabilities
- Better operational visibility and monitoring
- Improved incident response with rich context
- Support for data governance requirements
- Structured format enables automated analysis
- Risk-appropriate logging reduces noise

**Negative:**
- Increased storage requirements for detailed logs
- Additional processing overhead for log generation
- Complexity in log configuration and management
- Potential performance impact for high-volume operations
- Need for log retention and archival strategies

## Related ADRs
- ADR-016: Structured Logging and Observability Pattern (base logging framework)
- ADR-020: Unified Write Protection with Dual Permission Model (permission context)
- ADR-022: Confirmation Requirement Pattern (confirmation logging)

## Future Enhancements
- **Log Aggregation**: Integration with centralized logging systems
- **Real-time Monitoring**: Stream processing for immediate alerts
- **Compliance Dashboards**: Automated compliance reporting
- **Anomaly Detection**: ML-based detection of unusual patterns
- **Log Anonymization**: Privacy-preserving logging techniques