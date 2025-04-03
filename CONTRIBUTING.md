# Contributing

## Adding a graph from Network Repository to the dataset

> [!IMPORTANT]
> The following instructions assume that you are using [uv](https://github.com/astral-sh/uv) to run the scripts, which is **recommended**. If you are not using `uv`, substitute `uv run` with `python3` in the commands below, and make sure to create and activate a Python virtual environment and install the required dependencies (as listed in [`pyproject.toml`](pyproject.toml)) in that virtual environment beforehand.

> [!TIP]
> Many of the scripts can take additional arguments to customize their behavior. Run a script with the `--help` argument to see the available options.

1.  Download the ZIP file for a graph from the Network Repository website.

    The [`download.py`](download.py) script in this repository can be used to download the ZIP file. For example, to download the `ca-CSphd` graph, run:

    ```bash
    uv run download.py https://nrvis.com/download/data/ca/ca-CSphd.zip
    ```

    This will download the ZIP file to a temporary directory and print the path to the downloaded file. For example, the output might look like this:

    ```
    /var/folders/dk/pswnzxss0mb_77zx6cc1xkbh0000gn/T/tmp_gsupspy/ca-CSphd.zip
    ```

2.  Unzip the downloaded file into a folder with the same name as the graph and place the folder in the [`data`](data) directory.

    If using the [`extract.py`](extract.py) script, run it with the path to the ZIP file as the argument. For example, to extract the `ca-CSphd` graph we downloaded in step 1, run:

    ```bash
    uv run extract.py /var/folders/dk/pswnzxss0mb_77zx6cc1xkbh0000gn/T/tmp_gsupspy/ca-CSphd.zip
    ```

    This will create a folder called `ca-CSphd` in the [`data`](data) directory with the contents of the ZIP file, and print the path to the extracted folder. For our example, the output might look like this:

    ```
    /Users/ta7mid/repos/vc-research-experiments/data/ca-CSphd
    ```

3.  Run the [`preprocess_graph.py`](preprocess_graph.py) script on the extracted folder:

    ```bash
    uv run preprocess_graph.py /Users/ta7mid/repos/vc-research-experiments/data/ca-CSphd
    ```

    This will delete the existing files in the folder and generate the following two files:

    - `graph.edges`: An edge-list representation of the graph, with one edge per line in the format `source target`. The graph will be undirected, unweighted, and without self-loops.

    - `properties.yaml`: A YAML file with some metadata and statistical properties of the graph, namely: order (node count), size (edge count), maximum and average degrees, density, and connectedness.

> [!TIP]
> Notice that each script (except `download.py`) takes the output of the previous script in the data-preparation toolchain as the first and only positional argument, which is always a path on the filesystem. To help with chaining the scripts on the command line, the scripts are designed so that if you run a script omitting this positional argument, it will default to taking that argument from the standard input. This means that in Unix shells and in PowerShell, you can chain the scripts together using the pipe operator `|` into a single command line:
>
> ```bash
> uv run download.py URL | uv run extract.py | uv run preprocess_graph.py
> ```
>
> (Substitute the URL with the actual URL of the graph data you want to download.)
>
> To help things further, we have provided a script called `prepare_graph.py` that you can use to run the entire data-preparation toolchain in a single command:
>
> ```bash
> uv run prepare_graph.py URL
> ```
