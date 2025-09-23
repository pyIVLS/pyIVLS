import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from typing import List, Tuple, Optional, Dict, Any


class IVDataset:
    """Represents a single I-V dataset with associated metadata."""

    def __init__(self, filepath: str, label: Optional[str] = None):
        """
        Initialize an I-V dataset.

        Args:
            filepath: Path to the data file
            label: Optional label for the dataset (defaults to filename)
        """
        self.filepath = filepath
        self.label = label or os.path.basename(filepath)
        self.current: Optional[np.ndarray] = None
        self.voltage: Optional[np.ndarray] = None
        self._loaded = False

    def load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load I-V data from the file.
        Returns current and voltage arrays.
        """
        if self._loaded and self.current is not None and self.voltage is not None:
            return self.current, self.voltage

        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Data file not found: {self.filepath}")

        current = []
        voltage = []

        with open(self.filepath, "r") as file:
            for line in file:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Skip header lines that don't contain numeric data
                if line.startswith("IS_4pr") or line.startswith("VS_4pr"):
                    continue

                # Try to parse the line as two comma-separated numbers
                try:
                    parts = line.split(",")
                    if len(parts) == 2:
                        curr = float(parts[0])
                        volt = float(parts[1])
                        current.append(curr)
                        voltage.append(volt)
                except ValueError:
                    # Skip lines that can't be parsed as numbers
                    continue

        self.current = np.array(current)
        self.voltage = np.array(voltage)
        self._loaded = True

        return self.current, self.voltage

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the dataset."""
        if not self._loaded:
            self.load_data()

        if self.current is None or self.voltage is None or len(self.current) == 0:
            return {}

        stats = {
            "num_points": len(self.current),
            "voltage_min": self.voltage.min(),
            "voltage_max": self.voltage.max(),
            "current_min": self.current.min(),
            "current_max": self.current.max(),
            "current_magnitude_max": abs(self.current).max(),
        }

        # Calculate resistance near zero voltage if meaningful
        if len(self.current) > 0 and not np.allclose(self.current, 0):
            zero_v_idx = np.argmin(np.abs(self.voltage))
            if abs(self.voltage[zero_v_idx]) < 0.1 and abs(self.current[zero_v_idx]) > 1e-9:
                stats["resistance_at_zero"] = self.voltage[zero_v_idx] / self.current[zero_v_idx]

        return stats


class IVPlotter:
    """Class for plotting I-V characteristics with support for multiple datasets."""

    def __init__(self, figsize: Tuple[float, float] = (12, 8)):
        """
        Initialize the plotter.

        Args:
            figsize: Figure size as (width, height) in inches
        """
        self.figsize = figsize
        self.datasets = []
        self.colors = ["b", "r", "g", "orange", "purple", "brown", "pink", "gray", "olive", "cyan"]
        self.markers = ["o", "s", "^", "v", "D", "p", "h", "*", "+", "x"]

    def add_dataset(self, dataset: IVDataset) -> None:
        """Add a dataset to be plotted."""
        self.datasets.append(dataset)

    def add_dataset_from_file(self, filepath: str, label: Optional[str] = None) -> IVDataset:
        """
        Create and add a dataset from a file path.

        Args:
            filepath: Path to the data file
            label: Optional label for the dataset

        Returns:
            The created IVDataset object
        """
        dataset = IVDataset(filepath, label)
        self.add_dataset(dataset)
        return dataset

    def clear_datasets(self) -> None:
        """Clear all datasets."""
        self.datasets = []

    def plot_single(self, dataset: IVDataset, show_stats: bool = True) -> None:
        """
        Plot a single I-V dataset.

        Args:
            dataset: The dataset to plot
            show_stats: Whether to print statistics
        """
        current, voltage = dataset.load_data()

        plt.figure(figsize=self.figsize)
        plt.plot(voltage, current, "b-o", markersize=2, linewidth=1.5, label=dataset.label)
        plt.xlabel("Voltage (V)", fontsize=12)
        plt.ylabel("Current (A)", fontsize=12)
        plt.title(f"Current-Voltage (I-V) Characteristic\nData source: {dataset.label}", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.tight_layout()

        if show_stats:
            self._print_statistics(dataset)

    def plot_multiple(self, show_stats: bool = True) -> None:
        """
        Plot multiple I-V datasets on the same plot.

        Args:
            show_stats: Whether to print statistics for each dataset
        """
        if not self.datasets:
            raise ValueError("No datasets to plot. Add datasets first using add_dataset().")

        plt.figure(figsize=self.figsize)

        for i, dataset in enumerate(self.datasets):
            current, voltage = dataset.load_data()

            # Cycle through colors and markers
            color = self.colors[i % len(self.colors)]
            marker = self.markers[i % len(self.markers)]

            plt.plot(voltage, current, color=color, marker=marker, markersize=2, linewidth=1.5, label=dataset.label)

            if show_stats:
                self._print_statistics(dataset)

        plt.xlabel("Voltage (V)", fontsize=12)
        plt.ylabel("Current (A)", fontsize=12)
        plt.title("Current-Voltage (I-V) Characteristics Comparison", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.tight_layout()

    def show(self) -> None:
        """Display the plot."""
        plt.show()

    def save_plot(self, filename: str, dpi: int = 300) -> None:
        """
        Save the current plot to a file.

        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
        """
        plt.savefig(filename, dpi=dpi, bbox_inches="tight")

    def _print_statistics(self, dataset: IVDataset) -> None:
        """Print statistics for a dataset."""
        stats = dataset.get_statistics()

        print(f"\nData Summary for '{dataset.label}':")
        print(f"Number of data points: {stats.get('num_points', 0)}")

        if stats:
            print(f"Voltage range: {stats['voltage_min']:.3f} V to {stats['voltage_max']:.3f} V")
            print(f"Current range: {stats['current_min']:.6f} A to {stats['current_max']:.6f} A")
            print(f"Maximum current magnitude: {stats['current_magnitude_max']:.6f} A")

            if "resistance_at_zero" in stats:
                print(f"Approximate resistance near V=0: {stats['resistance_at_zero']:.2f} Ω")


class MultiIVPlotter:
    """Wrapper class for convenient multi-dataset plotting."""

    def __init__(self, figsize: Tuple[float, float] = (12, 8)):
        """
        Initialize the multi-plotter.

        Args:
            figsize: Figure size as (width, height) in inches
        """
        self.plotter = IVPlotter(figsize)

    def plot_files(self, filepaths: List[str], labels: Optional[List[str]] = None, show_stats: bool = True) -> None:
        """
        Plot multiple I-V files on the same plot.

        Args:
            filepaths: List of file paths to plot
            labels: Optional list of labels (defaults to filenames)
            show_stats: Whether to print statistics for each dataset
        """
        if labels and len(labels) != len(filepaths):
            raise ValueError("Number of labels must match number of filepaths")

        self.plotter.clear_datasets()

        for i, filepath in enumerate(filepaths):
            label = labels[i] if labels else None
            self.plotter.add_dataset_from_file(filepath, label)

        if len(filepaths) == 1:
            self.plotter.plot_single(self.plotter.datasets[0], show_stats)
        else:
            self.plotter.plot_multiple(show_stats)

        self.plotter.show()

    def compare_datasets(self, dataset_configs: List[Dict[str, str]], show_stats: bool = True) -> None:
        """
        Compare multiple datasets with custom configurations.

        Args:
            dataset_configs: List of dictionaries with 'filepath' and optional 'label' keys
            show_stats: Whether to print statistics for each dataset
        """
        self.plotter.clear_datasets()

        for config in dataset_configs:
            filepath = config["filepath"]
            label = config.get("label")
            self.plotter.add_dataset_from_file(filepath, label)

        if len(dataset_configs) == 1:
            self.plotter.plot_single(self.plotter.datasets[0], show_stats)
        else:
            self.plotter.plot_multiple(show_stats)

        self.plotter.show()


# Legacy function for backward compatibility
def read_iv_data_from_file(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Read I-V data from a .dat file.
    Returns current and voltage arrays.

    This is a legacy function for backward compatibility.
    Consider using IVDataset class for new code.
    """
    dataset = IVDataset(filepath)
    return dataset.load_data()


# Main execution when run as script
if __name__ == "__main__":
    # Default data file path
    default_datapath = "plugins/sweep-1.0.0/406-flat-p-ctlm_iter1_b.dat"

    if len(sys.argv) > 1:
        # Multiple files can be provided as arguments
        filepaths = sys.argv[1:]
        print(f"Plotting {len(filepaths)} file(s): {filepaths}")

        # Use the multi-plotter wrapper
        multi_plotter = MultiIVPlotter()
        multi_plotter.plot_files(filepaths)

    else:
        # Single file mode for backward compatibility
        print(f"Using default data file: {default_datapath}")

        try:
            # Create a single dataset and plot it
            dataset = IVDataset(default_datapath)
            plotter = IVPlotter()
            plotter.add_dataset(dataset)
            plotter.plot_single(dataset)
            plotter.show()

        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
