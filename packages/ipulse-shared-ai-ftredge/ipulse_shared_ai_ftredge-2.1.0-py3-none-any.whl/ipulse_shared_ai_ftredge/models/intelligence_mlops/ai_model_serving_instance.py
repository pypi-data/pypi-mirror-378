# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import Optional, Dict, Any, ClassVar
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import ObjectOverallStatus, ComputeResourceStatus


class AIModelServingInstance(BaseDataModel):
    """
    🚀 AI MODEL SERVING INSTANCE - The Active Prediction Service

    CORE CONCEPT:
    This represents a specific serving instance of an AI model version that actively serves predictions.
    This is the actual running/callable service, not just the model artifact.
    ONE model version can have MULTIPLE serving instances with different serving patterns.

    KEY RELATIONSHIPS:
    • ONE model version → MULTIPLE serving instances (multi-region, multi-env, different serving patterns)
    • ONE serving instance → MANY predictions (served from this instance)

    SERVING PATTERNS:
    • Persistent: Always-on instances (24/7 web services, APIs)
    • Ephemeral: On-demand instances (batch jobs, scheduled tasks, local runs)
    • Hybrid: Auto-scaling instances (scale to zero when idle)

    SERVING SCENARIOS:
    • Multi-region: Same model version in us-east-1, europe-west1, asia-southeast1
    • Multi-environment: Same version in staging, production, canary
    • A/B Testing: Same version with different endpoint configurations
    • Batch Processing: Spin up → Process → Shut down pattern
    • Local Development: Run locally for testing/development
    
    INTERNAL vs EXTERNAL:
    • Internal: Your infrastructure (GCP Cloud Run, AWS Lambda, K8s, local machine)
    • External: Third-party APIs (OpenAI, Google AI, Anthropic)
    
    LIFECYCLE PATTERNS:
    PERSISTENT: PROVISIONING → HEALTHY → SERVING → RETIRING → TERMINATED
    EPHEMERAL: PROVISIONING → SERVING → COMPLETED → TERMINATED  
    EXTERNAL: REGISTERING → ACTIVE → SERVING → DEACTIVATED
    """

    VERSION: ClassVar[float] = 1.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aimodelservinginstance"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    # --- Core Identity ---
    model_serving_instance_id: str = Field(..., description="Unique identifier for this serving instance.")
    model_serving_instance_name: str = Field(..., description="Human-readable instance name, e.g., 'prod_us_east_primary', 'daily_batch_runner'.")
    model_version_id: str = Field(..., description="Reference to the AIModelVersion being served.")
    model_spec_id: Optional[str] = Field(None, description="Reference to the AIModelSpecification (denormalized from model version for query efficiency).")
    training_config_id: Optional[str] = Field(None, description="Reference to the training configuration (denormalized from model version for query efficiency).")
    training_run_id: Optional[str] = Field(None, description="Reference to the training run (denormalized from model version for query efficiency).")

    # --- Hosting Pattern ---
    hosting_environment: str = Field(..., description="Environment type, e.g., 'production', 'staging', 'development', 'local', 'batch'.")
    hosting_type: str = Field(..., description="Type of hosting: 'internal' (self-hosted infrastructure) or 'external' (third-party API service).")
    hosting_pattern: str = Field(..., description="Hosting pattern: 'persistent' (24/7), 'ephemeral' (on-demand), 'hybrid' (auto-scaling).")
    hosting_provider: str = Field(..., description="Hosting provider, e.g., 'gcp', 'aws', 'azure', 'local' (for internal) or 'openai', 'anthropic', 'google' (for external).")
    hosting_service: Optional[str] = Field(None, description="Specific service, e.g., 'cloud_run', 'lambda', 'local_python', 'batch_job' (internal) or 'api', 'vertex_ai' (external).")
    hosting_region: str = Field(..., description="Geographic region, e.g., 'us-east-1', 'europe-west1', 'local', or 'global' for external providers.")
    hosting_zone: Optional[str] = Field(None, description="Availability zone if applicable, e.g., 'us-east-1a' (internal hosting only).")

    # --- Compute Resources (Internal Hosting Only) ---
    compute_specification: Optional[Dict[str, Any]] = Field(None, description="Compute resources for internal hosting, e.g., {'cpu': '2 cores', 'memory': '8GB', 'gpu': 'T4', 'instances': 3}.")
    auto_scaling_config: Optional[Dict[str, Any]] = Field(None, description="Auto-scaling configuration for internal hosting, e.g., {'min_instances': 1, 'max_instances': 10, 'target_cpu': 70}.")

    # --- Network & Access (Universal) ---
    endpoint_url: str = Field(..., description="Primary endpoint URL - either internal deployment URL or external API endpoint.")
    endpoint_authentication: Optional[str] = Field(None, description="Auth method, e.g., 'api_key', 'oauth', 'service_account', 'iam', 'none'.")
    endpoint_configuration: Optional[Dict[str, Any]] = Field(None, description="Endpoint settings, e.g., {'timeout_seconds': 30, 'max_concurrent_requests': 100, 'rate_limit': '1000/min'}.")
    api_key_reference: Optional[str] = Field(None, description="Reference to stored API key (not actual key) - for both internal auth and external APIs.")

    # --- Hosting Lifecycle ---
    hosting_compute_resource_status: ComputeResourceStatus = Field(..., description="Infrastructure status of the hosting compute resources (RUNNING, STOPPED, PROVISIONING, ERROR, etc.).")
    pulse_status: ObjectOverallStatus = Field(..., description="Whether we are actively using this hosting instance: ACTIVE (in use) or INACTIVE (not in use but may still be running).")
    hosting_strategy: Optional[str] = Field(None, description="Hosting strategy, e.g., 'blue_green', 'canary', 'rolling', 'direct'.")
    
    # --- Ephemeral/Scheduled Configuration ---
    execution_trigger: Optional[str] = Field(None, description="How instance is triggered: 'always_on', 'manual', 'scheduled', 'api_request', 'batch_job'.")
    schedule_expression: Optional[str] = Field(None, description="Cron expression for scheduled instances, e.g., '0 9 * * 1' (every Monday at 9 AM).")
    max_execution_duration_minutes: Optional[int] = Field(None, description="Maximum allowed execution time in minutes before auto-termination.")
    auto_shutdown_after_completion: bool = Field(default=True, description="Whether to automatically shut down after completing execution (ephemeral pattern).")
    
    # --- Timestamps ---
    hosting_started_datetime: datetime = Field(..., description="When hosting process started.")
    hosting_completed_datetime: Optional[datetime] = Field(None, description="When hosting became ready for serving.")
    last_health_check_datetime: Optional[datetime] = Field(None, description="Last successful health check.")
    last_execution_datetime: Optional[datetime] = Field(None, description="Last time this instance executed/served predictions.")
    next_scheduled_execution_datetime: Optional[datetime] = Field(None, description="Next scheduled execution time (for scheduled instances).")
    hosting_terminated_datetime: Optional[datetime] = Field(None, description="When hosting was terminated.")

    # --- Performance & Monitoring ---
    health_check_endpoint: Optional[str] = Field(None, description="Health check URL for monitoring.")
    monitoring_configuration: Optional[Dict[str, Any]] = Field(None, description="Monitoring setup, e.g., {'metrics_enabled': True, 'logging_level': 'INFO', 'alerts': ['high_latency', 'error_rate']}.")
    traffic_percentage: Optional[float] = Field(None, description="Percentage of traffic routed to this hosting instance (for A/B testing).")

    # --- Operational Metadata ---
    hosting_notes: Optional[str] = Field(None, description="Hosting-specific notes and configuration details.")
    created_by: str = Field(..., description="Who created this hosting instance.")
    approved_by: Optional[str] = Field(None, description="Who approved this hosting instance for production.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization and management.")

    class Config:
        extra = "forbid"
