# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, ClassVar
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import AIModelStatus, ObjectOverallStatus


class AIModelVersion(BaseDataModel):
    """
    📦 AI MODEL VERSION - The Trained Artifact
    
    CORE CONCEPT:
    This represents a specific, trained version of an AI model that is ready for deployment.
    It's the successful result of a training run, packaged and versioned for production use.
    
    KEY RELATIONSHIPS:
    • ONE training run → ZERO or ONE model version (if training succeeded)
    • ONE training configuration → MULTIPLE model versions (over time) 
    • ONE model specification → MULTIPLE model versions (across all training configs)
    
    VERSION LINEAGE:
    Model versions form lineages based on their training configuration:
    • Daily retrain config: v1.0.1, v1.0.2, v1.0.3... (daily versions)
    • Weekly retrain config: v1.1.0, v1.2.0, v1.3.0... (weekly versions)
    • Different configs can have different versioning schemes
    
    EXTERNAL MODEL VERSIONS:
    For external models (GPT, Gemini), versions track:
    • API endpoint configurations and authentication
    • Structured output schemas and inference parameters
    • Cost tracking and performance monitoring
    • Fallback strategies and reliability metrics
    
    LIFECYCLE STAGES:
    DRAFT → TRAINING → TRAINED → VALIDATED → DEPLOYED → SERVING → RETIRED
    
    PERFORMANCE TRACKING:
    Each version tracks its real-world performance to enable:
    • A/B testing between different training frequencies
    • Performance degradation detection
    • ROI analysis of different training strategies
    • Cost optimization for external model usage
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aimodelversion"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    # --- Identifiers and Relationships ---
    model_version_id: str = Field(..., description="The unique identifier for this specific model version.")
    model_version_name: Optional[str] = Field(None, description="Human-readable version name, e.g., 'Summer_2024_Production'.")
    model_version_number: str = Field(..., description="Semantic version number, e.g., '1.2.3' or '2024.08.06.1'.")
    model_spec_id: str = Field(..., description="Reference to the AIModelSpecification this version implements.")
    training_config_id: Optional[str] = Field(None, description="Reference to the AITrainingAndUpdateConfiguration following which this model was created. I.E. the training plan. (Unknown for external models)")
    training_run_id: Optional[str] = Field(None, description="Reference to the AITrainingOrUpdateRun that produced this version (Unknown for external models).")
    parent_version_id: Optional[str] = Field(None, description="Reference to the parent model version from which this one was retrained, fine-tuned or updated.")

    # --- Model State and Status ---
    version_status: AIModelStatus = Field(..., description="Current lifecycle status of this model version.")
    pulse_status: ObjectOverallStatus = Field(default=ObjectOverallStatus.ACTIVE, description="Whether this model version is actively used: ACTIVE (in use), INACTIVE (not in use), DRAFT (being prepared), RETIRED (permanently discontinued).")
    version_overall_pulse_performance_score: Optional[float] = Field(None, description="Overall performance assessment score for this version. Used for ranking and comparison.")
   
    # --- Lifecycle Timestamps and Governance ---
    deployment_to_production_approved_by: Optional[str] = Field(None, description="Who approved this model version for deployment.")
    approval_notes: Optional[str] = Field(None, description="Notes from the approval process.")
    deployed_to_production_datetime: Optional[datetime] = Field(None, description="When this model version was first used for production inference.")
    version_retired_datetime: Optional[datetime] = Field(None, description="When this model version was retired from active use.")
    drift_detection_enabled: bool = Field(True, description="Whether drift detection is enabled for this model version.")
   
    # --- Model Artifacts ---
    model_artifact_location: Optional[str] = Field(None, description="Primary storage location of the trained model artifact.")
    model_artifact_checksum: Optional[str] = Field(None, description="Checksum/hash of the model artifact for integrity verification.")
    model_artifact_size_mb: Optional[float] = Field(None, description="Size of the model artifact in MB.")
    model_artifact_format: Optional[str] = Field(None, description="Format of the model artifact, e.g., 'pickle', 'onnx', 'tensorflow_savedmodel'.")
    
    # NOTE: Hosting and deployment information has been moved to AIModelDeployment 
    # to support multiple deployments per model version (multi-region, A/B testing, etc.)

    # --- Metadata ---
    model_description: Optional[str] = Field(None, description="Description of what makes this model version unique.")
    release_notes: Optional[str] = Field(None, description="Release notes describing changes and improvements.")
    known_limitations: Optional[str] = Field(None, description="Known limitations or issues with this model version.")
    strengths: Optional[str] = Field(None, description="Strengths of this model version, e.g., 'high accuracy on recent data'.")
    weaknesses: Optional[str] = Field(None, description="Weaknesses of this model version (e.g., 'struggles with outliers').")
    recommended_use_cases: Optional[List[str]] = Field(None, description="Recommended use cases for this model version.")
    notes: Optional[str] = Field(None, description="Additional notes about this model version.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization and filtering.")

    
