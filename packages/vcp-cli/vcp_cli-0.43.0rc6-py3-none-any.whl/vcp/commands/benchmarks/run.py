import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import click
import numpy as np
from czbenchmarks.cli.resolve_reference import resolve_value_recursively
from czbenchmarks.cli.runner import run_task as czb_run_task
from czbenchmarks.datasets import Dataset, Organism
from czbenchmarks.datasets.utils import load_dataset as czb_load_dataset
from czbenchmarks.datasets.utils import load_local_dataset as czb_load_local_dataset
from czbenchmarks.tasks.task import TASK_REGISTRY
from czbenchmarks.tasks.types import CellRepresentation
from pydantic import BaseModel, field_validator
from rich.console import Console

from .api import fetch_benchmark_models, fetch_benchmarks_by_key
from .utils import (
    CLIError,
    DockerRunner,
    get_cache_dir,
    handle_cli_error,
    handle_unexpected_error,
    load_from_cache,
    mutually_exclusive,
    save_to_cache,
    validate_benchmark_filters,
)

logger = logging.getLogger(__name__)
console = Console()


def load_czbenchmarks_dataset(dataset_key: str) -> Dataset:
    """
    Load a dataset using czbenchmarks and provide user feedback.

    Loads the specified dataset using czbenchmarks, printing progress and summary information to the console.
    Handles common errors gracefully and raises CLIError if loading fails.

    Args:
        dataset_key (str): The dataset key to load.

    Returns:
        Dataset: The loaded dataset object.

    Raises:
        CLIError: If the dataset cannot be loaded or czbenchmarks is unavailable.
    """
    try:
        logger.info(f"Loading dataset '{dataset_key}' with czbenchmarks...")
        dataset = czb_load_dataset(dataset_key)
        logger.info(
            f"  -> Dataset loaded: {dataset.adata.n_obs} cells, {dataset.adata.n_vars} genes"
        )
        return dataset
    except KeyError:
        handle_cli_error(CLIError(f"Dataset key '{dataset_key}' is not valid."))
    except Exception as e:
        handle_unexpected_error(
            e, "vcp benchmarks run: on loading czbenchmarks dataset"
        )


def load_dataset(spec: "BenchmarkRunSpec") -> Dataset:
    """
    Load a dataset based on the BenchmarkRunSpec, supporting both regular and user datasets.

    Loads either a user-provided dataset (from a local file) or a czbenchmarks dataset,
    depending on the fields set in the spec.

    Args:
        spec (BenchmarkRunSpec): The benchmark specification containing dataset information.

    Returns:
        Dataset: The loaded dataset object.

    Raises:
        CLIError: If neither dataset nor user_dataset is specified, or if loading fails.
    """
    if spec.user_dataset:
        try:
            logger.info(f"Loading user dataset from '{spec.user_dataset.path}'...")
            organism = spec.user_dataset.organism

            if isinstance(organism, str):
                if organism.startswith("Organism."):
                    organism = organism.split(".", 1)[1]
                try:
                    organism = Organism[organism]
                except KeyError as e:
                    raise ValueError(f"Invalid organism: {organism}") from e

            dataset = czb_load_local_dataset(
                dataset_class=spec.user_dataset.dataset_class,
                organism=organism,
                path=Path(spec.user_dataset.path),
            )
            logger.info(
                f"  -> User dataset loaded: {dataset.adata.n_obs} cells, {dataset.adata.n_vars} genes"
            )
            return dataset
        except KeyError as e:
            missing_key = str(e).strip("'")
            handle_cli_error(
                CLIError(
                    f"Missing required key '{missing_key}' in user dataset specification. "
                    f"Required keys: dataset_class, organism, path"
                )
            )
        except Exception as e:
            handle_unexpected_error(e, "vcp benchmarks run: on loading user dataset")
    elif spec.czb_dataset_key:
        return load_czbenchmarks_dataset(spec.czb_dataset_key)
    else:
        handle_cli_error(
            CLIError("Either --dataset or --user-dataset must be specified.")
        )


class UserDatasetSpec(BaseModel):
    """
    Pydantic model for user-provided dataset configuration.

    Validates and manages user dataset specifications including the dataset
    class, organism type, and file path. Automatically expands user paths
    and validates file existence.

    Attributes:
        dataset_class (str): Fully qualified class name for the dataset.
        organism (str): Organism type (e.g., "HUMAN", "MOUSE").
        path (Path): Resolved path to the dataset file.
    """

    dataset_class: str
    organism: str
    path: Path

    @field_validator("path", mode="before")
    @classmethod
    def validate_path_exists_and_expand(cls, v):
        p = Path(v).expanduser()
        if not p.exists():
            handle_cli_error(CLIError(f"User dataset file not found: {p}"))
        return p

    model_config = {"extra": "forbid", "protected_namespaces": ()}


class BenchmarkRunSpec(BaseModel):
    """
    Complete specification for running a benchmark evaluation.

    Defines all parameters needed to execute a benchmark including model
    selection, dataset configuration, task specification, and baseline
    options. Supports both VCP models and precomputed cell representations,
    as well as both czbenchmarks datasets and user-provided datasets.

    Attributes:
        model_key (Optional[str]): VCP model identifier.
        czb_dataset_key (Optional[str]): czbenchmarks dataset identifier.
        user_dataset (Optional[UserDatasetSpec]): User-provided dataset config.
        task_key (Optional[str]): Benchmark task identifier.
        cell_representation (Optional[Path]): Path to precomputed embeddings.
        run_baseline (bool): Whether to compute baseline metrics.
        baseline_args (Optional[Dict[str, Any]]): Baseline computation parameters.
    """

    model_key: Optional[str] = None
    czb_dataset_key: Optional[str] = None
    user_dataset: Optional[UserDatasetSpec] = None
    task_key: Optional[str] = None
    cell_representation: Optional[Path] = None
    run_baseline: bool = False
    baseline_args: Optional[Dict[str, Any]] = None
    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "protected_namespaces": (),
    }

    @classmethod
    def from_cli_args(cls, args: Dict) -> "BenchmarkRunSpec":
        """
        Create a BenchmarkRunSpec from CLI arguments.

        Parses and validates CLI arguments to create a complete benchmark
        specification. Handles JSON parsing for user datasets and baseline
        arguments, and resolves benchmark keys to individual components.

        Args:
            args (Dict): Dictionary of CLI arguments from click.

        Returns:
            BenchmarkRunSpec: Validated benchmark specification.

        Raises:
            CLIError: If required arguments are missing, JSON parsing fails,
                    or benchmark key resolution fails.
        """

        model_key = args.get("model_key")
        cell_representation = args.get("cell_representation")
        czb_dataset_key = args.get("dataset_key")
        user_dataset = args.get("user_dataset")
        task_key = args.get("task_key")

        spec_data = {
            "model_key": model_key,
            "czb_dataset_key": czb_dataset_key,
            "task_key": task_key,
            "cell_representation": cell_representation,
            "run_baseline": args.get("run_baseline", False),
        }

        if user_dataset:
            try:
                user_dataset_config = json.loads(user_dataset)
                validated_config = UserDatasetSpec(**user_dataset_config)
                spec_data["user_dataset"] = validated_config
            except Exception as e:
                handle_cli_error(CLIError(f"Invalid user dataset: {e}"))

        if args.get("baseline_args"):
            try:
                baseline_config = json.loads(args["baseline_args"])
                spec_data["baseline_args"] = baseline_config
                spec_data["run_baseline"] = True
            except Exception as e:
                handle_cli_error(CLIError(f"Invalid baseline args: {e}"))

        spec = cls(**spec_data)
        spec._handle_benchmark_key(args)

        if not (
            (spec.model_key or spec.cell_representation)
            and (spec.czb_dataset_key or spec.user_dataset)
            and spec.task_key
        ):
            handle_cli_error(
                CLIError(
                    "Missing required arguments: model/cell_representation, dataset/user-dataset, or task. Use --help for details."
                )
            )

        logger.info(
            f"Selected benchmark run - "
            f"Model: {spec.model_key}, "
            f"Dataset: {spec.dataset_key}, "
            f"Task: {spec.task_key}"
        )

        return spec

    # TODO: convert to a model_post_init() on the pydantic model
    def _handle_benchmark_key(self, args: Dict) -> None:
        """
        Resolve benchmark key into individual model, dataset, and task components.

        Fetches the benchmark record from the API and populates the model_key,
        czb_dataset_key, and task_key fields based on the benchmark configuration.

        Args:
            args (Dict): CLI arguments containing potential benchmark_key.

        Raises:
            CLIError: If benchmark key is invalid or resolution fails.
        """

        benchmark_key = args.get("benchmark_key")
        if not benchmark_key:
            return

        try:
            benchmark_record = fetch_benchmarks_by_key(benchmark_key)
            self.model_key = benchmark_record.model_key
            self.czb_dataset_key = (
                benchmark_record.dataset_keys[0]
                if benchmark_record.dataset_keys
                else None
            )
            self.task_key = benchmark_record.task_key

            if not self.czb_dataset_key:
                handle_cli_error(
                    CLIError(f"No dataset found for benchmark key '{benchmark_key}'")
                )

        except Exception as e:
            handle_cli_error(
                CLIError(f"Failed to resolve benchmark key '{benchmark_key}': {e}")
            )

    @property
    def key(self) -> str:
        """
        Generate a unique key for this benchmark run.

        Creates a composite key from model, dataset, and task for caching
        and identification purposes.

        Returns:
            str: Formatted key as "model-dataset-task".
        """

        return f"{self.model_key}-{self.dataset_key}-{self.task_key}"

    @property
    def dataset_key(self) -> str:
        """
        Get the dataset key for this benchmark run.

        Returns either the czbenchmarks dataset key or a generated key
        for user datasets based on the filename.

        Returns:
            str: Dataset key for caching and identification.

        Note:
            For user datasets, generates a sanitized key from the filename.
            This may cause cache collisions for files with identical names.
        """

        assert self.user_dataset or self.czb_dataset_key
        if self.user_dataset:
            # FIXME: Ideally, should be create using a hash of the file contents to avoid cache collisions on files with the same name. Less ideally, it could hash the full path
            filename = Path(self.user_dataset.path).stem
            sanitized_name = "".join(c if c.isalnum() else "_" for c in filename)
            return f"user_dataset_{sanitized_name}"
        return self.czb_dataset_key


class ModelRegistry:
    """
    Registry for managing model configurations and validation.

    Provides functionality to fetch model configurations from the API,
    validate benchmark specifications against model capabilities, and
    ensure compatibility between models, datasets, and tasks.
    """

    def __init__(self):
        """Initialize the ModelRegistry."""
        pass

    def get_model_config(self, model_key: str) -> Dict[str, Any]:
        """
        Fetch and return model configuration from the API.

        Retrieves the complete model configuration including adapter image,
        model image, supported datasets, and supported tasks.

        Args:
            model_key (str): The unique identifier for the model.

        Returns:
            Dict[str, Any]: Model configuration containing:
                - adapter_image: Docker image for preprocessing/postprocessing
                - model_image: Docker image for model inference
                - supported_datasets: List of compatible dataset keys
                - supported_tasks: List of compatible task keys

        Raises:
            CLIError: If the model key is invalid or API request fails.
        """
        try:
            model_response = fetch_benchmark_models(model_key)
            model_details = model_response.model.model_dump()

            config = {
                "adapter_image": model_details["adapter_image"],
                "model_image": model_details["model_image"],
                "supported_datasets": model_details["supported_datasets"],
                "supported_tasks": model_details["supported_tasks"],
            }

            return config
        except Exception as e:
            handle_cli_error(
                CLIError(f"Failed to fetch model '{model_key}' from API: {e}")
            )

    def validate(self, spec: BenchmarkRunSpec) -> bool:
        """
        Validate that a benchmark specification is compatible with the model configuration.

        Args:
            spec: The benchmark run specification to validate

        Returns:
            True if the specification is valid

        Raises:
            CLIError: If validation fails for any reason
        """
        try:
            model_config = self.get_model_config(spec.model_key)
        except CLIError:
            handle_cli_error(CLIError(f"Invalid model key: {spec.model_key}"))
            return False

        if not model_config:
            handle_cli_error(CLIError(f"Invalid model key: {spec.model_key}"))
            return False

        supported_datasets = model_config.get("supported_datasets", [])
        supported_tasks = model_config.get("supported_tasks", [])

        if not (
            spec.dataset_key in supported_datasets
            or spec.dataset_key.startswith("user_dataset_")
        ):
            console.print(
                f"[yellow]Warning: Dataset {spec.dataset_key!r} is not listed as supported for model {spec.model_key!r} and may fail. "
                f"Supported datasets: {supported_datasets!r}[/yellow]"
            )

        if spec.task_key not in supported_tasks:
            console.print(
                f"[yellow]Warning: Task {spec.task_key!r} is not listed as supported for model {spec.model_key!r} and may fail. "
                f"Supported tasks: {supported_tasks!r}[/yellow]"
            )

        return True


def run_benchmarking_task(
    task_key: str,
    dataset: Dataset,
    cell_representation: CellRepresentation,
    run_baseline: bool,
    baseline_params: Optional[Dict[str, Any]] = None,
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a benchmarking task using provided embeddings and dataset.

    Executes the specified benchmarking task using the provided cell embeddings and dataset.
    Optionally runs a baseline computation if requested. Returns a dictionary containing
    model metrics and, if requested, baseline metrics.

    Args:
        task_key (str): The key identifying the task to run.
        dataset (Dataset): The dataset object.
        cell_representation (CellRepresentation): The cell embeddings to use for the task.
        run_baseline (bool): Whether to run the baseline computation.
        baseline_params (Optional[Dict[str, Any]]): Parameters for the baseline computation.
        random_seed (Optional[int]): Random seed for reproducibility.

    Returns:
        Dict[str, Any]: Dictionary with "model_metrics" and, if run_baseline is True, "baseline_metrics".

    Raises:
        CLIError: If the task is not found or fails to execute.
    """

    try:
        task_info = TASK_REGISTRY.get_task_info(task_key)
    except KeyError:
        available_tasks = ", ".join(TASK_REGISTRY.list_tasks())
        handle_cli_error(
            CLIError(f"Task '{task_key}' not found. Available tasks: {available_tasks}")
        )
    except Exception as e:
        handle_unexpected_error(
            e, "vcp benchmarks run: on getting czbenchmarks task info"
        )

    adata = dataset.adata

    task_params: Dict[str, Any] = {}
    if hasattr(dataset, "labels"):
        if "input_labels" in task_info.task_params:
            task_params["input_labels"] = dataset.labels
        if "labels" in task_info.task_params:
            task_params["labels"] = dataset.labels
    if (
        hasattr(dataset, "adata")
        and hasattr(dataset.adata, "obs")
        and "obs" in task_info.task_params
    ):
        task_params["obs"] = dataset.adata.obs

    if baseline_params:
        baseline_params = {**baseline_params}
    else:
        baseline_params = {}

    resolved_task_params = resolve_value_recursively(task_params, adata)
    resolved_baseline_params = resolve_value_recursively(baseline_params, adata)

    logger.info(f"Running {task_key} task on provided embeddings...")
    results: Dict[str, Any] = {
        "model_metrics": czb_run_task(
            task_name=task_key,
            adata=adata,
            cell_representation=cell_representation,
            run_baseline=False,
            task_params=resolved_task_params,
            baseline_params=resolved_baseline_params,
            random_seed=random_seed,
        )
    }

    if run_baseline:
        logger.info(f"Running {task_key} task on baselines...")
        results["baseline_metrics"] = czb_run_task(
            task_name=task_key,
            adata=adata,
            cell_representation=dataset.adata.X,
            run_baseline=True,
            task_params=resolved_task_params,
            baseline_params=resolved_baseline_params,
            random_seed=random_seed,
        )

    return results


class CellRepresentationPipeline:
    """
    Pipeline for running benchmarks using precomputed cell representations.

    Loads precomputed cell representations, runs the specified benchmarking task, and optionally includes baseline metrics.
    Results are saved to cache unless caching is disabled.
    """

    def run(
        self, spec: BenchmarkRunSpec, use_cache: bool, random_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the benchmarking pipeline using precomputed cell representations.

        Loads the dataset and cell embeddings, runs the benchmarking task, and saves results
        to cache if caching is enabled.

        Args:
            spec (BenchmarkRunSpec): The benchmark specification.
            use_cache (bool): If True, uses cached of results.
            random_seed (Optional[int]): Random seed for reproducibility.

        Returns:
            Dict[str, Any]: The benchmarking results.
        """

        logger.info(
            f"Starting Cell Representation Run: {spec.dataset_key}/{spec.task_key}"
        )
        dataset_obj = load_dataset(spec)
        embeddings = np.load(spec.cell_representation)
        results = run_benchmarking_task(
            spec.task_key,
            dataset_obj,
            embeddings,
            spec.run_baseline,
            spec.baseline_args,
            random_seed,
        )

        if use_cache:
            if spec.model_key:
                model_key = spec.model_key
            else:
                model_key = Path(spec.cell_representation).stem
            save_to_cache(
                model_key, spec.dataset_key, spec.task_key, results, "results"
            )

        return results


class FullBenchmarkPipeline:
    """
    Pipeline for running a full benchmark, including model inference and evaluation.

    Handles the complete process: loading the dataset, running the model pipeline
    (preprocessing, inference, postprocessing), generating embeddings, and running the benchmarking
    task. Results and embeddings are cached unless caching is disabled.
    """

    def __init__(self, registry, docker: DockerRunner):
        """
        Initialize the FullBenchmarkPipeline.

        Args:
            registry (ModelRegistry): The model registry for configuration and validation.
            docker (DockerRunner): The Docker runner for executing containerized steps.
        """
        self.registry = registry
        self.docker = docker

    def run(
        self, spec: BenchmarkRunSpec, use_cache: bool, random_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the full benchmarking pipeline from scratch.

        Loads the dataset, runs the model pipeline to generate embeddings, and executes the
        benchmarking task. Utilizes cached results and embeddings if available and caching is enabled.

        Args:
            spec (BenchmarkRunSpec): The benchmark specification.
            use_cache (bool): If True, uses cached results and embeddings.
            random_seed (Optional[int]): Random seed for reproducibility.

        Returns:
            Dict[str, Any]: The benchmarking results.

        Raises:
            CLIError: If required files are missing or pipeline steps fail.
        """

        logger.info(f"Starting Full Benchmark: {spec.key}")

        if use_cache:
            try:
                results = load_from_cache(
                    spec.model_key, spec.dataset_key, spec.task_key, "results"
                )
                logger.info("Reusing cached task results.")
                return results
            except FileNotFoundError:
                pass

        dataset_obj = load_dataset(spec)

        embeddings = None
        if use_cache:
            try:
                embeddings = load_from_cache(
                    spec.model_key, spec.dataset_key, None, "embeddings"
                )
                logger.info("Reusing cached embeddings.")
            except FileNotFoundError:
                pass

        if embeddings is None:
            self._run_model_pipeline(spec)

            embeddings_path = (
                get_cache_dir(spec.model_key, spec.dataset_key, None)
                / "task_input"
                / "embeddings.npy"
            )
            if embeddings_path.exists():
                embeddings = np.load(embeddings_path)
                if use_cache:
                    save_to_cache(
                        spec.model_key, spec.dataset_key, None, embeddings, "embeddings"
                    )
            else:
                raise CLIError(
                    f"Embeddings file not found at {embeddings_path}. Pipeline may have failed."
                )

        results = run_benchmarking_task(
            spec.task_key,
            dataset_obj,
            embeddings,
            spec.run_baseline,
            spec.baseline_args,
            random_seed,
        )

        save_to_cache(
            spec.model_key, spec.dataset_key, spec.task_key, results, "results"
        )
        return results

    def _run_model_pipeline(self, spec: BenchmarkRunSpec) -> None:
        """
        Run the model pipeline to generate cell embeddings.

        Executes the preprocessing, inference, and postprocessing steps using Docker containers
        as specified in the model registry. Ensures that the final embeddings file is created.

        Args:
            spec (BenchmarkRunSpec): The benchmark specification.

        Raises:
            CLIError: If any pipeline step fails or required files are missing.
        """

        config = self.registry.get_model_config(spec.model_key)

        run_cache_dir = get_cache_dir(spec.model_key, spec.dataset_key, None)
        model_input_json_path = run_cache_dir / "model_input" / "input.json"
        final_embeddings_path = run_cache_dir / "task_input" / "embeddings.npy"

        self._run_preprocess(spec, config, run_cache_dir)
        self._run_inference(config, run_cache_dir, model_input_json_path)
        self._run_postprocess(config, run_cache_dir)

        if not final_embeddings_path.exists():
            raise CLIError(
                f"Postprocessing failed: Expected embeddings file {final_embeddings_path} was not created. "
                f"Check adapter configuration and Docker logs."
            )

    def _run_preprocess(
        self, spec: BenchmarkRunSpec, config: Dict, run_cache_dir: Path
    ):
        """
        Run the preprocessing step of the model pipeline.

        Executes the model adapter's preprocessing Docker container, preparing input data
        for model inference.

        Args:
            spec (BenchmarkRunSpec): The benchmark specification.
            config (Dict): Model configuration from the registry.
            run_cache_dir (Path): Directory for caching pipeline files.

        Raises:
            CLIError: If preprocessing fails.
        """
        logger.info("1. Running Preprocessing Step...")

        model_input_dir = run_cache_dir / "model_input"
        model_input_dir.mkdir(exist_ok=True)

        if spec.user_dataset:
            dataset_file_path = spec.user_dataset.path.expanduser().resolve()
            # copy the user dataset file into the model_input directory
            shutil.copy(dataset_file_path, model_input_dir)

            container_dataset_path = f"/model_input/{dataset_file_path.name}"
            user_dataset_spec = spec.user_dataset.model_copy(deep=True)
            user_dataset_spec.path = container_dataset_path
            user_dataset_spec_json = user_dataset_spec.model_dump_json()

            logger.info(
                f"Running preprocessing with user dataset: {user_dataset_spec_json}"
            )
            logger.debug(
                f"Executing Docker command: adapter_image={config['adapter_image']}, "
                f"mounts=[{str(model_input_dir)}, '/model_input', 'rw'], "
                f"cmd_args=['preprocess', '--dataset-spec', {user_dataset_spec_json}], "
                "description='Preprocessing'"
            )
            try:
                self.docker.run(
                    image=config["adapter_image"],
                    mounts=[(str(model_input_dir), "/model_input", "rw")],
                    cmd_args=[
                        "preprocess",
                        "--dataset-spec",
                        str(user_dataset_spec_json),
                    ],
                    description="Preprocessing",
                )
            except Exception as e:
                handle_cli_error(
                    CLIError(
                        f"Docker execution failed during preprocessing with user dataset: {e}"
                    )
                )
        else:
            dataset_name = spec.dataset_key
            logger.info(f"Running preprocessing with dataset: {dataset_name}")
            logger.debug(
                f"Executing Docker command: adapter_image={config['adapter_image']}, "
                f"mounts=[{str(model_input_dir)}, '/model_input', 'rw'], "
                f"cmd_args=['preprocess', '--dataset-name', {dataset_name}], "
                f"description='Preprocessing'"
            )
            try:
                self.docker.run(
                    image=config["adapter_image"],
                    mounts=[(str(model_input_dir), "/model_input", "rw")],
                    cmd_args=["preprocess", "--dataset-name", dataset_name],
                    description="Preprocessing",
                )
            except Exception as e:
                handle_cli_error(
                    CLIError(
                        f"Docker execution failed during preprocessing with dataset '{dataset_name}': {e}"
                    )
                )

    def _run_inference(
        self, config: Dict, run_cache_dir: Path, model_input_json_path: Path
    ):
        """
        Run the model inference step of the pipeline.

        Executes the model's inference Docker container, generating output from preprocessed input.

        Args:
            config (Dict): Model configuration from the registry.
            run_cache_dir (Path): Directory for caching pipeline files.
            model_input_json_path (Path): Path to the model input JSON file.

        Raises:
            CLIError: If inference fails or output file is missing.
        """
        logger.info("2. Running Model Inference Step...")

        model_input_dir = run_cache_dir / "model_input"
        model_output_dir = run_cache_dir / "model_output"
        model_output_dir.mkdir(exist_ok=True)

        input_json_path = model_input_dir / "input.json"
        if input_json_path.exists():
            logger.info("Using input.json created by preprocessing step.")
        else:
            raise CLIError(
                f"input.json not found in {model_input_dir}. Preprocessing may have failed."
            )

        self.docker.run(
            image=config["model_image"],
            mounts=[
                (str(model_input_dir), "/model_input", "ro"),
                (str(model_output_dir), "/model_output", "rw"),
            ],
            env_vars=config.get("inference_env_vars"),
            cmd_args=[],
            description="Inference",
        )

        output_json_path = model_output_dir / "output.json"
        if not output_json_path.exists():
            raise CLIError(
                f"Model inference failed: Expected output file {output_json_path} was not created. "
                f"Check model configuration and Docker logs."
            )

    def _run_postprocess(self, config: Dict, run_cache_dir: Path):
        """
        Run the postprocessing step of the model pipeline.

        Executes the model adapter's postprocessing Docker container, converting model output
        into final cell embeddings.

        Args:
            config (Dict): Model configuration from the registry.
            run_cache_dir (Path): Directory for caching pipeline files.

        Raises:
            CLIError: If postprocessing fails or embeddings file is missing.
        """
        logger.info("3. Running Postprocessing Step...")

        model_output_dir = run_cache_dir / "model_output"
        task_input_dir = run_cache_dir / "task_input"
        task_input_dir.mkdir(exist_ok=True)

        output_json_path = model_output_dir / "output.json"
        if output_json_path.exists():
            logger.info("Using output.json created by inference step.")
        else:
            raise CLIError(
                f"output.json not found in {model_output_dir}. Model inference may have failed."
            )

        self.docker.run(
            image=config["adapter_image"],
            mounts=[
                (str(model_output_dir), "/model_output", "ro"),
                (str(task_input_dir), "/task_input", "rw"),
            ],
            cmd_args=["postprocess"],
            description="Postprocessing",
        )


@click.command(
    name="run",
    context_settings={"help_option_names": ["-h", "--help"]},
    help="""
Run a benchmark task on a model and dataset.

Supports use of a VCP model inference (--model-key) or use of a pre-computed cell representation (--cell-representation). Supports use of a VCP dataset (--dataset-key) or a user dataset (--user-dataset).
""",
)
@click.option(
    "-b",
    "--benchmark-key",
    callback=mutually_exclusive(
        "model-key", "cell_representation", "user_dataset", "dataset_key"
    ),
    help="Shortcut for specifying model, dataset, and task together. Format: MODEL-DATASET-TASK (e.g., scvi_homo_sapiens-tsv2_blood-cell_type_annotation).",
)
@click.option(
    "-m",
    "--model-key",
    callback=mutually_exclusive("benchmark", "cell_representation"),
    # TODO: Could list the valid model keys here (there are a limited number currently)
    help="Model key from the registry (e.g., scvi_homo_sapiens).",
)
@click.option(
    "-d",
    "--dataset-key",
    callback=mutually_exclusive("user_dataset"),
    help="Dataset key from czbenchmarks datasets(e.g., tsv2_blood).",
)
@click.option(
    "-u",
    "--user-dataset",
    callback=mutually_exclusive("dataset"),
    help='Path to a user-provided .h5ad file. Provide as a JSON string with keys: \'dataset_class\', \'organism\', and \'path\'. Example: \'{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/mydata.h5ad"}\'.',
)
@click.option(
    "-t",
    "--task-key",
    type=click.Choice(TASK_REGISTRY.list_tasks(), case_sensitive=False),
    help="Benchmark task to run (choose from available tasks).",
)
@click.option(
    "-c",
    "--cell-representation",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    callback=mutually_exclusive("benchmark", "model"),
    help="Path to precomputed cell embeddings (.npy file).",
)
@click.option(
    "-l",
    "--baseline-args",
    help="JSON string with parameters for the baseline computation.",
)
@click.option(
    "-r", "--random-seed", type=int, help="Set a random seed for reproducibility."
)
@click.option(
    "-n",
    "--no-cache",
    is_flag=True,
    help="Disable caching. Forces all steps to run from scratch.",
)
# TODO: Consider --debug if this is just showing debug log output (https://czi.atlassian.net/browse/VC-4024)
@click.pass_context
def run_command(ctx: click.Context, **kwargs) -> None:
    """
    Run a benchmark task on a model and dataset.

    You can run a full benchmark (model + dataset + task) or evaluate precomputed cell embeddings.
    Specify either a model and dataset, a benchmark key, or a user dataset file.
    """

    try:
        spec = BenchmarkRunSpec.from_cli_args(kwargs)
        validate_benchmark_filters(spec.model_key, spec.dataset_key, spec.task_key)

        if spec.cell_representation:
            pipeline = CellRepresentationPipeline()
            results = pipeline.run(
                spec,
                use_cache=not kwargs.get("no_cache", False),
                random_seed=kwargs.get("random_seed"),
            )
        else:
            registry = ModelRegistry()

            if not registry.validate(spec):
                return

            docker = DockerRunner(
                use_gpu=True  # benchmarks absolutely need a GPU for inference
            )
            pipeline = FullBenchmarkPipeline(registry, docker)
            results = pipeline.run(
                spec,
                use_cache=not kwargs.get("no_cache", False),
                random_seed=kwargs.get("random_seed"),
            )
        console.print("\n[green]Benchmark completed successfully![/green]")
        console.print("\n[bold]Results:[/bold]")
        console.print(json.dumps(results, indent=2, default=str))
    except click.UsageError:
        raise
    except CLIError as e:
        handle_cli_error(e)
    except Exception as e:
        handle_unexpected_error(e, "vcp benchmarks run")
