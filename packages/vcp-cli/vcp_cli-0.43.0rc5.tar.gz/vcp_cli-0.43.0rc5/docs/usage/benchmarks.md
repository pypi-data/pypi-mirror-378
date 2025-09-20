# Benchmarks

The VCP CLI provides commands to utilize the capabilities of the [Virtual Cell Platform](https://virtualcellmodels.cziscience.com/)

## Overview

Benchmarking in VCP allows comparison of different models across various tasks and datasets. The benchmarking system consists of three main components:

- **Models**: Pre-trained machine learning models (e.g., scVI, TRANSCRIPTFORMER)
- **Datasets**: Single-cell datasets for evaluation (e.g., Tabula Sapiens datasets)
- **Tasks**: Specific evaluation tasks (e.g., clustering, embedding, label prediction)

The Datasets and Task implementations are provided by the [cz-benchmarks](https://chanzuckerberg.github.io/cz-benchmarks/) package.

## Commands

### vcp benchmarks list

Lists the benchmarks that have been computed by and published on the [Virtual Cell Platform](https://virtualcellmodels.cziscience.com/benchmarks).
This output provides the combinations of datasets, models, and tasks for which benchmarks were computed.
See [`vcp benchmarks get`](#vcp-benchmarks-get) below for how to retrieve the benchmark metric results for specific benchmarks.

#### Basic Usage
```bash
vcp benchmarks list
```

See [Output Fields](#output-fields) for a description of the output fields.

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Filter by specific benchmark key | `-b f47892309c571cdf` |
| `--model-filter` | `-m` | Filter by model key pattern | `-m "scvi*"` |
| `--dataset-filter` | `-d` | Filter by dataset key pattern | `-d "tsv2*blood"` |
| `--task-filter` | `-t` | Filter by task key pattern | `-t "embed*"` |
| `--format` | `-f` | Output format (table or json) | `-f json` |

* A benchmark key is a unique identifier that combines a specific model, dataset, and task. For example, `f47892309c571cdf` represents a specific combination of TRANSCRIPTFORMER model, tsv2_blood dataset, and embedding task. It is returned in results when using the filter options and can be used to identify a specific benchmark when using the `vcp benchmarks get` and `vcp benchmarks list` commands.

The filter options allow use of `*` as a wildcard. Filters use substring matching and are case-insensitive. Filter values match across both the name and key of a given entity type (model, dataset, entity).


#### Examples

**List all available benchmarks:**
```bash
vcp benchmarks list
```

**Filter by dataset, model, and task with table output:**
```bash
vcp benchmarks list -d tsv2_blood -m TRANSCRIPT -t embedding
```

**Find specific benchmark by key:**
```bash
vcp benchmarks list -b f47892309c571cdf
```

**Search for scVI models on any dataset with JSON output:**
```bash
vcp benchmarks list -m "scvi*" -f json
```

### vcp benchmarks run

Executes a benchmark task and generates performance metrics using a specific model and dataset.

#### Basic Usage

To reproduce a benchmark published on the Virtual Cell Platform:
```bash
vcp benchmarks run -m MODEL_KEY -d DATASET_KEY -t TASK_KEY
```

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Use predefined benchmark combination | `-b f47892309c571cdf` |
| `--model-key` | `-m` | Specify model from registry | `-m SCVI-v1-homo_sapiens` |
| `--dataset-key` | `-d` | Specify dataset from registry | `-d tsv2_blood` |
| `--task-key` | `-t` | Specify benchmark task | `-t clustering` |
| `--user-dataset` | `-u` | Use custom dataset file | See user dataset section |
| `--cell-representation` | `-c` | Use precomputed embeddings | `-c embeddings.npy` |
| `--baseline-args` | `-l` | Parameters for baseline computation | `-l '{}'` |
| `--random-seed` | `-r` | Set random seed for reproducibility | `-r 42` |
| `--no-cache` | `-n` | Disable caching, run from scratch | `-n` |

#### Examples

**Run benchmark using a VCP benchmark key:**
```bash
vcp benchmarks run -b 40e2c4837bf36ae1
```

**Run a benchmark using a specific model, dataset, and task:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering -r 42 -n
```

**Run with baseline comparison:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering -baseline-args '{}' -r 42 -n
```
In this example, the Clustering task does not take any explicit arguments for the baseline computation, so an empty JSON object is provided.

**Run embedding task on user-provided dataset:**
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/user_dataset.h5ad"}' \
  -t embedding -r 123 -n
```

**Use precomputed cell representations:**
```bash
vcp benchmarks run -c './user_model_output.npy' \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/user_dataset.h5ad"}' \
  -t label_prediction \
  -l '{"labels": "@obs:cell_type", "n_folds": 5, "min_class_size": 5}' \
  -r 100 -n
```
> Coming soon! Documentation on how to specify task input arguments that are provided by the dataset file.

#### User Dataset Format
When using `--user-dataset`, provide a JSON string with the following keys:
- `dataset_class`: The dataset class to use (typically `czbenchmarks.datasets.SingleCellLabeledDataset`)
- `organism`: The organism type (`HUMAN`, `MOUSE`, etc.)
- `path`: Path to the .h5ad file

Example:
```json
{
  "dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset",
  "organism": "HUMAN",
  "path": "~/mydata.h5ad"
}
```

#### Baseline Arguments
The `--baseline-args` option accepts task-specific parameters:

**For label prediction:**
```json
{
  "labels": "@obs:cell_type",
  "n_folds": 5,
  "min_class_size": 5
}
```

**For clustering (empty for default parameters):**
```json
{}
```

### vcp benchmarks get

Retrieves and displays benchmark results that have been computed by and published by either the the Virtual Cell Platform or computed locally by the user using the `vcp benchmarks run` command.
If filters match benchmarks from both the VCP and a user's locally run benchmarks, all of the matching benchmarks will be output together. This supports comparison of user benchmarks against VCP benchmarks.

#### Basic Usage
```bash
vcp benchmarks get
```

See [Output Fields](#output-fields) for a description of the output fields.

#### Options

| Option | Short | Description | Example |
|--------|--------|-------------|---------|
| `--benchmark-key` | `-b` | Filter by benchmark key pattern | `-b "scvi*v1-tsv2*liver"` |
| `--model-filter` | `-m` | Filter by model key pattern | `-m "scvi*"` |
| `--dataset-filter` | `-d` | Filter by dataset key pattern | `-d "tsv2*liver"` |
| `--task-filter` | `-t` | Filter by task key pattern | `-t "label*pred"` |
| `--format` | `-f` | Output format (table or json) | `-f json` |

The filter options allow use of `*` as a wildcard. Filters use substring matching and are case-insensitive. Filter values match across both the name and key of a given entity type (model, dataset, entity).

#### Examples

**Get all available results:**
```bash
vcp benchmarks get
```

**Filter results by model and dataset:**
```bash
vcp benchmarks get -m test -d tsv2_blood
```

**Get results for specific benchmark:**
```bash
vcp benchmarks get -b f47892309c571cdf
```

**Filter by task and model with JSON output:**
```bash
vcp benchmarks get -m scvi -d tsv2_blood -t clustering -f json
```

## Output Fields

The `vcp benchmarks get` and `vcp benchmarks list` commands output the following attributes:

- **Benchmark Key**: Unique identifier for the benchmark
- **Model Key/Name**: Model identifier and display name
- **Dataset Keys/Names**: Dataset identifier and display name
- **Task Key/Name**: Task identifier and display name
- **Metric**: Metric name (for `get` results only).
- **Value**: Metric value (for `get` results only)

For further details about the supported Tasks and Metrics see the [cz-benchmarks Tasks documentation](https://chanzuckerberg.github.io/cz-benchmarks/assets.html#task-details).

## Advanced Usage Patterns

### Reproducible Experiments
Always use the `--random-seed` option for reproducible results:
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering -r 42
```

### Bypassing Cache
Use `--no-cache` to ensure fresh computation:
```bash
vcp benchmarks run -m SCVI-v1-homo_sapiens -d tsv2_blood -t clustering -n --no-cache
```

### Reproducing VCP Results
Combine `list` and `run` commands for systematic evaluation:
```bash
# First, list available benchmarks
vcp benchmarks list -m "scvi*" -f json > available_benchmarks.json

# Then run specific benchmarks
vcp benchmarks run -b BENCHMARK_KEY_FROM_LIST
```

### User Datasets
Evaluate models on user datasets while comparing to existing benchmarks:
```bash
# Specify a user's local dataset file
vcp benchmarks run -m SCVI-v1-homo_sapiens \
  -u '{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/custom.h5ad"}' \
  -t embedding

# Compare with existing results
vcp benchmarks get -m SCVI-v1-homo_sapiens -t embedding
```

## Best Practices

1. **Use specific filters**: Narrow down results with appropriate filters to find relevant benchmarks quickly
2. **Set random seeds**: Ensure reproducibility by always setting random seeds for experiments
3. **Compare with baselines**: Include baseline arguments when running benchmarks to establish performance context
4. **Cache management**: Use `--no-cache` sparingly, as caching significantly speeds up repeated experiments
5. **Output format selection**: Use JSON format for programmatic processing, table format for human review
6. **Progressive filtering**: Start with broad filters and progressively narrow down to find specific benchmarks

