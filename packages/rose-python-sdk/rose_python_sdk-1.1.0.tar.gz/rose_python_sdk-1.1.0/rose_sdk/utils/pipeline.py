"""
Pipeline builder utilities for the Rose Python SDK.
"""

from typing import Dict, Any, List, Set

# Datetime import removed


# Supported scenarios from the pipeline deployer
SUPPORTED_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "telasa": {
        "dataset_keys": {"interaction-log", "item-metadata"},
        "description": "Telasa recommendation pipeline with personalized and hybrid recommendations",
    },
    "realtime_leaderboard": {
        "dataset_keys": {"interaction", "metadata"},
        "description": "Realtime leaderboard pipeline for item ranking and user favorites",
    },
}


class PipelineBuilder:
    """Builder for creating pipeline configurations."""

    def __init__(self, account_id: str, pipeline_name: str, scenario: str):
        self.account_id = account_id
        self.pipeline_name = pipeline_name

        if scenario not in SUPPORTED_SCENARIOS:
            raise ValueError(f"Unsupported scenario: {scenario}. Supported scenarios: {list(SUPPORTED_SCENARIOS.keys())}")

        self.scenario = scenario
        self.scenario_config = SUPPORTED_SCENARIOS[scenario]

        # Initialize with minimal required properties
        self.properties: Dict[str, Any] = {"datasets": {}, "scenario": scenario}

    def add_dataset(self, dataset_key: str, dataset_id: str) -> "PipelineBuilder":
        """
        Map a user's dataset to a pipeline dataset key.

        Args:
            dataset_key: The dataset key defined by the pipeline scenario (e.g., "interaction", "metadata")
            dataset_id: The actual dataset ID created by dataset management (e.g., "AHgyJijrQ5GPnHZgKE_Hgg")

        Example:
            # User has datasets: "my_interactions" (ID: abc123) and "my_items" (ID: def456)
            # Pipeline needs: "interaction" and "metadata" keys
            builder.add_dataset("interaction", "abc123")  # Maps user's "my_interactions" to pipeline's "interaction"
            builder.add_dataset("metadata", "def456")     # Maps user's "my_items" to pipeline's "metadata"
        """
        if dataset_key not in self.scenario_config["dataset_keys"]:
            raise ValueError(
                f"Dataset key '{dataset_key}' not supported for scenario '{self.scenario}'. "
                f"Supported dataset keys: {self.scenario_config['dataset_keys']}"
            )

        datasets = self.properties["datasets"]
        if not isinstance(datasets, dict):
            datasets = {}
            self.properties["datasets"] = datasets
        datasets[dataset_key] = dataset_id
        return self

    def set_custom_property(self, key: str, value: Any) -> "PipelineBuilder":
        """Set a custom property (overrides default service properties)."""
        self.properties[key] = value
        return self

    def get_scenario_info(self) -> Dict[str, Any]:
        """Get information about the current scenario."""
        return {
            "scenario": self.scenario,
            "description": self.scenario_config["description"],
            "required_dataset_keys": list(self.scenario_config["dataset_keys"]),
        }

    def get_dataset_mapping(self) -> Dict[str, str]:
        """Get the current dataset mapping (dataset_key -> dataset_id)."""
        datasets = self.properties["datasets"]
        if isinstance(datasets, dict):
            return dict(datasets)
        return {}

    def is_dataset_mapping_complete(self) -> bool:
        """Check if all required dataset keys are mapped to dataset IDs."""
        required_keys: Set[str] = self.scenario_config["dataset_keys"]
        datasets = self.properties["datasets"]
        if isinstance(datasets, dict):
            mapped_keys = set(datasets.keys())
        else:
            mapped_keys = set()
        return required_keys.issubset(mapped_keys)

    def get_missing_dataset_keys(self) -> List[str]:
        """Get list of dataset keys that still need to be mapped."""
        required_keys: Set[str] = self.scenario_config["dataset_keys"]
        datasets = self.properties["datasets"]
        if isinstance(datasets, dict):
            mapped_keys = set(datasets.keys())
        else:
            mapped_keys = set()
        return list(required_keys - mapped_keys)

    def build(self) -> Dict[str, Any]:
        """Build the pipeline configuration."""
        return {"account_id": self.account_id, "pipeline_name": self.pipeline_name, "properties": self.properties}


def create_telasa_pipeline(
    account_id: str, pipeline_name: str, interaction_log_dataset_id: str, item_metadata_dataset_id: str
) -> Dict[str, Any]:
    """
    Create a Telasa pipeline configuration.

    Args:
        account_id: The account ID
        pipeline_name: The pipeline name
        interaction_log_dataset_id: The interaction-log dataset ID
        item_metadata_dataset_id: The item-metadata dataset ID

    Returns:
        Pipeline configuration dictionary
    """
    return (
        PipelineBuilder(account_id, pipeline_name, scenario="telasa")
        .add_dataset("interaction-log", interaction_log_dataset_id)
        .add_dataset("item-metadata", item_metadata_dataset_id)
        .build()
    )


def create_realtime_leaderboard_pipeline(
    account_id: str, pipeline_name: str, interaction_dataset_id: str, metadata_dataset_id: str
) -> Dict[str, Any]:
    """
    Create a realtime leaderboard pipeline configuration.

    Args:
        account_id: The account ID
        pipeline_name: The pipeline name
        interaction_dataset_id: The interaction dataset ID
        metadata_dataset_id: The metadata dataset ID

    Returns:
        Pipeline configuration dictionary
    """
    return (
        PipelineBuilder(account_id, pipeline_name, scenario="realtime_leaderboard")
        .add_dataset("interaction", interaction_dataset_id)
        .add_dataset("metadata", metadata_dataset_id)
        .build()
    )


def create_pipeline(
    account_id: str, pipeline_name: str, scenario: str, dataset_mapping: Dict[str, str], **kwargs
) -> Dict[str, Any]:
    """
    Create a pipeline configuration with minimal configuration.

    Args:
        account_id: The account ID
        pipeline_name: The pipeline name
        scenario: The pipeline scenario (telasa, realtime_leaderboard)
        dataset_mapping: Dictionary mapping dataset keys to dataset names
                        e.g., {"interaction": "user_dataset_123", "metadata": "user_dataset_456"}
        **kwargs: Additional configuration parameters (optional)

    Returns:
        Pipeline configuration dictionary
    """
    builder = PipelineBuilder(account_id, pipeline_name, scenario=scenario)

    # Add datasets
    for dataset_key, dataset_name in dataset_mapping.items():
        builder.add_dataset(dataset_key, dataset_name)

    # Apply custom configurations if provided
    for key, value in kwargs.items():
        if hasattr(builder, key):
            getattr(builder, key)(value)
        else:
            builder.set_custom_property(key, value)

    return builder.build()


def create_custom_pipeline(
    account_id: str, pipeline_name: str, scenario: str, datasets: Dict[str, str], **kwargs
) -> Dict[str, Any]:
    """
    Create a custom pipeline configuration (alias for create_pipeline).

    Args:
        account_id: The account ID
        pipeline_name: The pipeline name
        scenario: The pipeline scenario (telasa, realtime_leaderboard)
        datasets: Dictionary mapping dataset names to dataset IDs
        **kwargs: Additional configuration parameters

    Returns:
        Pipeline configuration dictionary
    """
    return create_pipeline(account_id, pipeline_name, scenario, datasets, **kwargs)


def get_supported_scenarios() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all supported scenarios.

    Returns:
        Dictionary of scenario information
    """
    return SUPPORTED_SCENARIOS.copy()
