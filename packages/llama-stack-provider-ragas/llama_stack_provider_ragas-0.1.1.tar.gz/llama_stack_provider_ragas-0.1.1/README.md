# `trustyai-ragas` <br> Ragas as an Out-of-Tree Llama Stack Provider

## About
This repository implements [Ragas](https://github.com/explodinggradients/ragas) as an out-of-tree [Llama Stack](https://github.com/meta-llama/llama-stack) evaluation provider.

## Features
The goal is to provide all of Ragas' evaluation functionality over Llama Stack's eval API, while leveraging the Llama Stack's built-in APIs for inference (llms and embeddings), datasets, and benchmarks.

There are two versions of the provider:
- `inline`: runs the Ragas evaluation in the same process as the Llama Stack server.
- `remote`: runs the Ragas evaluation in a remote process, using Kubeflow Pipelines.

## Prerequisites
- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- The remote provider requires a running [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines) server.

## Setup
- Clone this repository
    ```bash
    git clone <repository-url>
    cd llama-stack-provider-ragas
    ```

- Create and activate a virtual environment
    ```bash
    uv venv
    source .venv/bin/activate
    ```

- Install (optionally as an editable package). There's `distro`, `remote` and `dev` optional dependencies to run the sample LS distribution and the KFP-enabled remote provider. Installing the `dev` dependencies will also install the `distro` and `remote` dependencies.
    ```bash
    uv pip install -e ".[dev]"
    ```
- Run the Llama Stack server with the distribution configs. The distribution is a simple LS distribution that uses Ollama for inference and embeddings, and includes both the inline and remote Ragas providers. Counting the number of `run`s in this command is left as an exercise for the reader:
    ```bash
    dotenv run uv run llama stack run distribution/run.yaml
    ```

### Inline provider (within the Llama Stack process)
- Create a `.env` file with the following:
    - `EMBEDDING_MODEL`
        - This is the embedding model that Ragas will use to embed the questions and contexts. This depends on the metrics you are using.

### Remote provider (on Kubernetes via Kubeflow Pipelines)
- In addition to the env variables above, your `.env` file should also contain the following Kubeflow Pipelines related variables:
    - `KUBEFLOW_LLAMA_STACK_URL`
        - This is the url of the llama stack server that the Kubeflow Pipeline will use to run the evaluation (LLM generations and embeddings, etc.). If you are running Llama Stack locally, you can use [ngrok](https://ngrok.com/) to expose it.
    - `KUBEFLOW_PIPELINES_ENDPOINT`
        - You can get this via `kubectl get routes -A | grep -i pipeline` on your Kubernetes cluster.
    - `KUBEFLOW_NAMESPACE`
        - This is the name of the data science project where the Kubeflow Pipelines server is running.

## Usage
See the demos in the `demos` directory.
