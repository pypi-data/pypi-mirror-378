"""Common base model for all time series predictions (LLM and Quant)."""
from typing import ClassVar, Dict, Any, Optional, Union, List
from datetime import datetime
from pydantic import Field, BaseModel
from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge.enums import (SectorCategory, SectorRecordsCategory,
                                              ModelOutputPurpose, ProgressStatus,TimeFrame)


class PredictionValuePointBase(BaseModel):
    """
    Base prediction point with financial analysis.
    """
    prediction_timestamp_utc: Union[datetime, str] = Field(..., description="Timestamp of the prediction in datetime utc format or YYYY-MM-DD format")
    prediction_value: float = Field()
    prediction_value_upper_bound: float = Field(..., description="Upper bound of the prediction confidence interval")
    prediction_value_lower_bound: float = Field(..., description="Lower bound of the prediction confidence interval")
    prediction_confidence_score: float = Field(..., description="Confidence score of the prediction")
    


class TimeSeriesPredictionBase(BaseDataModel):
    """
    Common base class for all time series predictions.
    Contains fields that apply to ANY time series prediction, regardless of method (LLM or Quant).
    Version 1.0: Unified base architecture for extensible prediction types.
    """
    VERSION: ClassVar[float] = 1.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "tspredbase"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # --- Core Identity ---
    prediction_id: str = Field(..., description="Unique identifier for this prediction")
    prediction_purpose : ModelOutputPurpose = Field(..., description="Training , Validation, Serving..")
    # --- Target Context ---
    target_subject_id: str = Field(..., description="ID of the subject being predicted")
    target_subject_name: str = Field(..., description="Name of the subject being predicted")
    target_subject_domain: Optional[str] = Field(None, description="Domain of the predicted subject")
    target_subject_sector_records_category: Optional[Union[str, SectorRecordsCategory]] = Field(None, description="Subject sector, like MARKET, INDICATOR, FUNDAMENTAL, etc.")
    target_subject_sector_category: Optional[Union[str, SectorCategory]] = Field(None, description="Category: 'EQUITY', 'FIXED_INCOME', 'Commodity', etc.")

    # --- AI Model Context ---
    model_specification_id: str = Field(..., description="ID of the AI model")
    model_name: str = Field(..., description="Readable Name of the AI model")
    model_version_id: str = Field(..., description="Version of the AI model. For internal model this comes from AIModelVersion")
    model_version_name: Optional[str] = Field(None, description="Human-readable version name, e.g., 'Summer_2024_Production'.")

    # --- Model Deployment Context (Optional - for MLOps tracking) ---
    model_serving_instance_id: Optional[str] = Field(None, description="ID of the specific serving instance used for this prediction")
    model_serving_instance_name: Optional[str] = Field(None, description="Name of the serving instance used for this prediction")

    # --- Input Data Context (Multi-dimensional sources) ---
    input_data_sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="Input data sources used for this prediction with their characteristics.")
    # Example structure:
    # {
    #   "schema_id": "market_eod_data_realtime",
    #   "schema_name": "Market EOD Real-time Feed", 
    #   "rows_count": 252,  # trading days used
    #   "index_or_date_column_name": "trade_date",  # primary temporal/index column
    #   "feature_columns_used": ["open_normalized", "volume_log", "sentiment_score"],
    #   "temporal_range_start": "2024-01-15",
    #   "temporal_range_end": "2024-12-31",
    #   "data_freshness_minutes": 15,  # how old the latest data is
    #   "preprocessing_applied": {"outlier_removal": True, "normalization": "z_score"},
    #   "dataset_filter_used": {"asset_id_in": ["AAPL", "GOOGL"], "asset_category_pulse":"equity",  "trading_status": "traded_on_exchange"},
    #   "dataset_scope": "training_universe"
    # }
    
    # --- Prediction Context and Cost---
    prediction_status: ProgressStatus = Field(..., description="Status of the prediction generation process.")
    prediction_requested_datetime_utc: datetime = Field(..., description="When prediction was requested")
    prediction_received_datetime_utc: datetime = Field(..., description="When response was received")
    prediction_latency_ms: Optional[float] = Field(None, description="Time taken to generate prediction in milliseconds")
    prediction_cost_usd: Optional[float] = Field(None, description="Cost of prediction in USD")

    # --- Value Context ---
    prediction_values_start_timestamp_utc: Optional[Union[datetime, str]] = Field(None, description="Start of prediction horizon,Timestamp in datetime or YYYY-MM-DD format ")
    prediction_values_end_timestamp_utc: Optional[Union[datetime, str]] = Field(None, description="End of prediction horizon,Timestamp in datetime or YYYY-MM-DD format ")
    prediction_steps_count: int = Field(..., description="Number of time steps predicted.")
    prediction_step_timeframe: TimeFrame = Field(..., description="Time frequency of predictions.")
    prediction_value_type: Optional[str] = Field(None, description="Type of value being predicted")
    prediction_value_unit: Optional[str] = Field(None, description="Unit/dimension of predicted values")
    prediction_values: List[PredictionValuePointBase] = Field(default_factory=list, 
        description="List of prediction points with timestamps and values")
    

    # --- Status & Error Handling (Generic) ---
    prediction_error: Optional[str] = Field(None, description="Error message if prediction failed")
    
    # --- Metadata ---
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Tags for categorization and filtering")
    prediction_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        extra = "forbid"  # Prevent unexpected fields
