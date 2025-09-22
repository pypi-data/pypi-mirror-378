from typing import TYPE_CHECKING

from .config import DeepFabricConfig
from .config_manager import DEFAULT_MODEL
from .dataset import Dataset
from .exceptions import ConfigurationError
from .generator import DataSetGenerator
from .tui import get_dataset_tui, get_tui

if TYPE_CHECKING:
    from .topic_model import TopicModel


def handle_dataset_events(generator) -> Dataset | None:
    """
    Handle dataset generation with TUI progress.

    Args:
        generator: Generator yielding dataset events

    Returns:
        Dataset object or None if generation failed
    """
    tui = get_dataset_tui()
    progress = None
    task = None

    final_result: Dataset | None = None
    try:
        for event in generator:
            if isinstance(event, dict) and "event" in event:
                if event["event"] == "generation_start":
                    tui.show_generation_header(
                        event["model_name"], event["num_steps"], event["batch_size"]
                    )
                    progress = tui.create_rich_progress()
                    progress.start()
                    task = progress.add_task(
                        "  Generating dataset samples", total=event["total_samples"]
                    )
                elif event["event"] == "step_complete":
                    if progress and task is not None:
                        samples_generated = event.get("samples_generated", 0)
                        if samples_generated > 0:
                            progress.update(task, advance=samples_generated)
                elif event["event"] == "generation_complete":
                    if progress:
                        progress.stop()
                    tui.success(f"Successfully generated {event['total_samples']} samples")
                    if event["failed_samples"] > 0:
                        tui.warning(f"Failed to generate {event['failed_samples']} samples")
            elif isinstance(event, Dataset):
                final_result = event
            else:
                # Handle unexpected non-dict, non-Dataset events
                get_tui().warning(f"Unexpected event type: {type(event)}")
    except Exception as e:
        if progress:
            progress.stop()
        get_tui().error(f"Dataset generation failed: {str(e)}")
        raise

    return final_result


def create_dataset(
    engine: DataSetGenerator,
    topic_model: "TopicModel",
    config: DeepFabricConfig,
    num_steps: int | None = None,
    batch_size: int | None = None,
    sys_msg: bool | None = None,
    provider: str | None = None,  # noqa: ARG001
    model: str | None = None,
    engine_overrides: dict | None = None,
) -> Dataset:
    """
    Create dataset using the data engine and topic model.

    Args:
        engine: DataSetGenerator instance
        topic_model: TopicModel (Tree or Graph) to use for generation
        config: DeepFabricConfig object
        num_steps: Override for number of steps
        batch_size: Override for batch size
        sys_msg: Override for including system message
        provider: Override for LLM provider
        model: Override for model name
        engine_overrides: Additional engine parameter overrides

    Returns:
        Generated Dataset object

    Raises:
        ConfigurationError: If dataset generation fails
    """
    dataset_config = config.get_dataset_config()
    dataset_params = dataset_config["creation"]

    # Get final values
    final_num_steps = num_steps or dataset_params["num_steps"]
    final_batch_size = batch_size or dataset_params["batch_size"]

    # Set model for dataset creation
    engine_params = config.get_engine_params(**(engine_overrides or {}))
    final_model = model or engine_params.get("model_name", DEFAULT_MODEL)

    # Create dataset with overrides - using generator pattern for TUI
    try:
        generator = engine.create_data_with_events(
            num_steps=final_num_steps,
            batch_size=final_batch_size,
            topic_model=topic_model,
            model_name=final_model,
            sys_msg=sys_msg,
            num_example_demonstrations=dataset_params.get("num_example_demonstrations") or 3,
        )
        dataset = handle_dataset_events(generator)
    except Exception as e:
        raise ConfigurationError(f"Error creating dataset: {str(e)}") from e

    # Validate dataset was created
    if dataset is None:
        raise ConfigurationError("Dataset generation failed - no dataset returned")

    return dataset


def save_dataset(dataset: Dataset, save_path: str, config: DeepFabricConfig | None = None) -> None:
    """
    Save dataset to file and apply formatters if configured.

    Args:
        dataset: Dataset object to save
        save_path: Path where to save the dataset
        config: Optional configuration containing formatter settings

    Raises:
        ConfigurationError: If saving fails
    """
    tui = get_tui()
    try:
        # Save the raw dataset
        dataset.save(save_path)
        tui.success(f"Dataset saved to: {save_path}")

        # Apply formatters if configured
        if config:
            formatter_configs = config.get_formatter_configs()
            if formatter_configs:
                tui.info("Applying formatters...")
                try:
                    formatted_datasets = dataset.apply_formatters(formatter_configs)

                    for formatter_name, formatted_dataset in formatted_datasets.items():
                        if hasattr(formatted_dataset, "samples"):
                            sample_count = len(formatted_dataset.samples)
                            tui.success(
                                f"Applied '{formatter_name}' formatter: {sample_count} samples"
                            )
                        else:
                            tui.success(f"Applied '{formatter_name}' formatter")

                except Exception as e:
                    tui.error(f"Error applying formatters: {str(e)}")
                    # Don't raise here - we want to continue even if formatters fail

    except Exception as e:
        raise ConfigurationError(f"Error saving dataset: {str(e)}") from e
