"""A set of examples used for demonstrating the physt capabilities / in tests."""

import importlib.util
import io
import pkgutil
import sys
import warnings
from contextlib import suppress

import numpy as np

from physt._facade import h1, h2, h3
from physt.types import Histogram1D, Histogram2D, HistogramND


def normal_h1(size: int = 10000, mean: float = 0, sigma: float = 1) -> Histogram1D:
    """A simple 1D histogram with normal distribution.

    Parameters
    ----------
    size : Number of points
    mean : Mean of the distribution
    sigma : Sigma of the distribution
    """
    data = np.random.normal(mean, sigma, (size,))
    return h1(data, name="normal", axis_name="x", title="1D normal distribution")


def normal_h2(size: int = 10000) -> Histogram2D:
    """A simple 2D histogram with normal distribution.

    Parameters
    ----------
    size : Number of points
    """
    data1 = np.random.normal(0, 1, (size,))
    data2 = np.random.normal(0, 1, (size,))
    return h2(
        data1,
        data2,
        name="normal",
        axis_names=tuple("xy"),
        title="2D normal distribution",
    )


def normal_h3(size: int = 10000) -> HistogramND:
    """A simple 3D histogram with normal distribution.

    Parameters
    ----------
    size : Number of points
    """
    data1 = np.random.normal(0, 1, (size,))
    data2 = np.random.normal(0, 1, (size,))
    data3 = np.random.normal(0, 1, (size,))
    return h3(
        [data1, data2, data3],
        name="normal",
        axis_names=tuple("xyz"),
        title="3D normal distribution",
    )


def fist() -> Histogram1D:
    """A simple histogram in the shape of a fist."""
    widths = [0, 1.2, 0.2, 1, 0.1, 1, 0.1, 0.9, 0.1, 0.8]
    edges = np.cumsum(widths)
    heights = np.asarray([4, 1, 7.5, 6, 7.6, 6, 7.5, 6, 7.2]) + 5
    return Histogram1D(
        edges, heights, axis_name="Is this a fist?", title='Physt "logo"'
    )


ALL_EXAMPLES = [normal_h1, normal_h2, normal_h3, fist]


with suppress(ImportError):
    import pandas as pd

    def load_dataset(name: str) -> pd.DataFrame:
        """Load example dataset.

        If seaborn is present, its datasets can be loaded.
        Physt also includes some datasets in CSV format.
        """
        # Our custom datasets:
        with suppress(FileNotFoundError):
            binary_data = pkgutil.get_data("physt", f"examples/{name}.csv")
            if binary_data:
                return pd.read_csv(io.BytesIO(binary_data))

        # Seaborn datasets?
        import seaborn as sns

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if name in sns.get_dataset_names():
                return sns.load_dataset(name)

        # Fall through
        raise KeyError(f"Dataset '{name}' not available.")

    def munros(edge_length: float = 10) -> Histogram2D:
        """Number of munros in different rectangular areas of Scotland.

        Parameters
        ----------
        edge_length : Size of the rectangular grid in minutes.

        Returns
        -------
        h : physt.histogram_nd.Histogram2D
            Histogram in latitude and longitude.
        """
        data = load_dataset("munros")
        return h2(
            data["lat"],
            data["long"],
            "fixed_width",
            bin_width=edge_length / 60,
            name="munros",
            title="Munros of Scotland",
        )

    ALL_EXAMPLES.append(munros)


def show_examples():
    """Script showing some of the physt examples in the CLI.

    You can run this like:

        python -m physt.examples
    """
    if not importlib.util.find_spec("rich"):
        print("Please, install rich or physt[terminal] to view nice terminal output.")
        sys.exit(-1)

    from rich.console import Console
    from rich.json import JSON
    from rich.panel import Panel

    from physt.examples import normal_h1, normal_h2

    console = Console()

    h1 = normal_h1()
    h2 = normal_h2()

    console.print("[bold]A 1D histogram:[/bold]")
    console.print(h1)

    console.print()
    console.print("[bold]The associated stats:[/bold]")
    console.print(h1.statistics)

    console.print()
    console.print("[bold]And the plot:[/bold]")

    h1.plot(backend="ascii", show_values=True, show_labels=True, color="green")
    console.print()

    console.print("[bold]JSON fully describing the histogram:[/bold]")
    console.print(Panel(JSON(h1.to_json()), width=min(console.width, 60)))

    console.print("[bold]A 2D histogram:[/bold]")
    console.print(h2)

    console.print()
    console.print("[bold]And the plot:[/bold]")
    h2.plot(backend="ascii")
