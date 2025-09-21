# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, Any, ClassVar, Literal
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import (
    AILearningParadigm,
    AIArchitectureFamily,
    RegressionAlgorithm,
    ClassificationAlgorithm,
    TimeSeriesAlgorithm,
    DataModality,
    DataStructureLevel,
    ModalityContentDynamics,
    ObjectOverallStatus,
)


class AIModelSpecification(BaseDataModel):
    """
    🏗️ AI MODEL SPECIFICATION - The Blueprint
    
    CORE CONCEPT:
    This represents the fundamental architecture and capabilities of an AI model - what it CAN do,
    not what it HAS done. Think of it as the "specification sheet" for a model type.
    
    KEY RELATIONSHIPS:
    • ONE model specification → MULTIPLE training configurations
    • ONE model specification → MULTIPLE model versions
    • Each training configuration defines HOW to train this model type
    • Each model version is the result of actually training this model type
    
    PREDICTION SCOPE STRATEGY:
    • single_target: Model predicts one specific object (e.g., AAPL stock price)
    • multi_target: Model predicts multiple specific objects (e.g., S&P 500 stocks)  
    • universal: Model can predict any object matching criteria (e.g., any equity with market cap > $1B)
    
    MULTIMODAL CAPABILITIES:
    Modern foundation models support multiple input/output modalities using structured enums:
    • Input Modalities: DataModality enum (text, image, audio, video, tabular, json_text, etc.)
    • Output Modalities: DataModality enum (text, structured_json, image, audio, etc.)
    • Structure Levels: DataStructureLevel enum (structured, semi_structured, unstructured)
    • Content Dynamics: ModalityContentDynamics enum (static, sequence, timeseries, etc.)
    
    EXTERNAL MODEL EXAMPLES:
    • GPT-4: input=[TEXT, IMAGE], output=[TEXT, JSON_TEXT], structure=[STRUCTURED, SEMI_STRUCTURED]
    • Gemini Pro: input=[TEXT, IMAGE, VIDEO], output=[TEXT, JSON_TEXT], dynamics=[STATIC, SEQUENCE]
    • Claude-3: input=[TEXT, IMAGE], output=[TEXT, JSON_TEXT], structure=[STRUCTURED, SEMI_STRUCTURED]
    
    SUPPORTED TARGET CRITERIA:
    Flexible criteria system for defining what this model can predict:
    {
        "domain": ["fincore_market_assets"],
        "asset_class": ["equity", "crypto"], 
        "market_cap_min": 1000000000,
        "specific_object_ids": ["AAPL", "GOOGL"]
    }
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aimodel"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    model_spec_id: str = Field(..., description="The unique identifier for this AI model.")
    model_spec_name: str = Field(..., description="The name of the AI model, e.g., 'Universal_Asset_Predictor_v2'.")
    pulse_status: ObjectOverallStatus = Field(default=ObjectOverallStatus.ACTIVE, description="Status of this model specification: ACTIVE (in use), INACTIVE (not in use), DRAFT (being developed), RETIRED (permanently discontinued).")
    
    # --- Prediction Capabilities ---
    prediction_scope_type: Literal["single_target", "multi_target", "universal"] = Field(..., description="Type of prediction scope this model supports.")
    supported_target_subjects_criteria: Dict[str, Any] = Field(..., description="Flexible criteria defining what this model can predict. Keys: domain, category, asset_class, market_cap_min/max, specific_object_ids, etc.")
    supported_prediction_variables: List[str] = Field(..., description="List of variables this model can predict, e.g., ['close_price', 'volatility', 'sentiment_score'].")
    
    # --- Model Source ---
    model_source: Literal["internal", "external_foundational", "external_service"] = Field(..., description="Source and training approach: 'internal' (built from scratch), 'foundational' (API-based LLM), 'open_source_finetuned' (open-source base + our training), 'cloud_service' (cloud provider's ML service).")
    model_author: str = Field(..., description="The author or team responsible for the model.")
    model_provider_organization: List[str] = Field(..., description="The provider of the model, e.g., 'OpenAI', 'Google'.")
    model_license: Optional[str] = Field(None, description="The license under which the model is released, e.g., 'MIT', 'Apache 2.0'.")
    model_rights_description: Optional[str] = Field(None, description="A description of the rights associated with the model, e.g., 'Open for research use only'.")
    
    # --- Multimodal Capabilities (Using structured enums) ---
    supported_input_modalities: Optional[List[DataModality]] = Field(None, description="Input data modalities supported by the model.")
    supported_output_modalities: Optional[List[DataModality]] = Field(None, description="Output data modalities the model can produce.")
    supported_input_structure_levels: Optional[List[DataStructureLevel]] = Field(None, description="Input data structure levels supported, e.g., structured, semi_structured, unstructured.")
    supported_output_structure_levels: Optional[List[DataStructureLevel]] = Field(None, description="Output data structure levels the model can produce.")
    supported_content_dynamics: Optional[List[ModalityContentDynamics]] = Field(None, description="Content dynamics supported, e.g., static, sequence, timeseries.")
    max_input_tokens: Optional[int] = Field(None, description="Maximum input context length in tokens.")
    max_output_tokens: Optional[int] = Field(None, description="Maximum output length in tokens.")
    supports_function_calling: Optional[bool] = Field(None, description="Whether model supports function/tool calling.")
    
    # --- External Service Fields (Only for cloud_service) ---

    # --- Training & Features ---
    learning_paradigm: AILearningParadigm = Field(default=AILearningParadigm.SUPERVISED, description="Always supervised for this application.")
    ai_architecture_family: AIArchitectureFamily = Field(..., description="The supervised learning family: Regression, Classification, Time Series, or Foundation Model.")
    algorithm: Optional[
        RegressionAlgorithm |
        ClassificationAlgorithm |
        TimeSeriesAlgorithm
    ] = Field(None, description="The underlying algorithm used. For foundational models, this represents their core architecture (e.g., TRANSFORMER for GPT).")

    foundation_model_type: Optional[str] = Field(None, description="Model family, e.g., 'gpt-4', 'gemini-pro', 'claude-3'.")
    external_managed_model_service_name: Optional[str] = Field(None, description="Specific service, e.g., 'bigquery_ml', 'bigquery_ai', 'vertex_ai', 'sagemaker', 'databricks_ml'.")
    model_development_framework: Optional[Dict[str, Any]] = Field(None, description="Information about the model framework, e.g., {'framework': 'TensorFlow', 'version': '2.14', 'gpu_support': True}.")
    model_description: Optional[str] = Field(None, description="A detailed description of the model, its purpose, and its architecture.")
    model_overall_pulse_performance_score: Optional[float] = Field(None, description="A single overall performance score for the model.")

    # ---- Model Details ----
    parameters_count: Optional[int] = Field(..., description="The number of parameters in the model, used for complexity assessment.")
    hyperparameters_schema: Optional[Dict[str, Any]] = Field(None, description="The hyperparameters used to train the model, e.g., {'learning_rate': 0.001, 'batch_size': 32, 'epochs': 100}.")
    model_complexity_score: Optional[float] = Field(None, description="Complexity score for model comparison and resource planning.")
    feature_input_schema: Optional[Dict[str, Any]] = Field(None, description="The input schema for the model, e.g., {'type': 'object', 'properties': {'feature1': {'type': 'number'}, ...}}.")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="The output schema of the model, e.g., {'type': 'object', 'properties': {'prediction': {'type': 'number'}}}.")
    
    # --- USE CASES--- # Below is COMMENTED OUT , BECAUSE THERE ARE POTENTIALLY MANY VERSIONS FOR A SINGLE MODEL
    
    notes: Optional[str] = Field(None, description="Any additional notes about this model specification.")
    strengths: Optional[str] = Field(None, description="A description of the strengths of the model specification, e.g., 'High accuracy on recent data'.")
    weaknesses: Optional[str] = Field(None, description="A description of the weaknesses of the model specification, e.g., 'Struggles with outliers'.")
    recommended_use_cases: Optional[List[str]] = Field(None, description="Recommended use cases for this model specification.")
    recommended_consumer: Optional[str] = Field(None, description="Who/what requested this prediction, e.g., 'trading_system', 'user_dashboard'.")
    model_conceived_on: Optional[datetime] = Field(..., description="The timestamp when the model was created.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization, e.g., {'environment': 'production', 'team': 'ml-ops'}.")
