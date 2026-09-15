# Compile all .ui files in the components/ui_files dir to py files.
import argparse
import fnmatch
import subprocess
from pathlib import Path

# Try to import optional Typer dep
try:
    import typer
except ImportError:
    typer = None

UI_DIR = Path("components/ui_files")
OUT_DIR = Path("components/compiled_ui")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_main_files() -> None:
    for ui_file in UI_DIR.glob("*.ui"):
        out_file = OUT_DIR / f"{ui_file.stem.lower()}.py"
        print(f"Compiling {ui_file} to {out_file}...")
        subprocess.run(["pyside6-uic", str(ui_file), "-o", str(out_file)], check=True)

        print("Cleaning up generated UI files with Ruff...")
        subprocess.run(["uvx", "ruff", "check", "--fix", "--ignore", "N999", str(OUT_DIR)], check=True)

        subprocess.run(["uvx", "ruff", "format", str(OUT_DIR)], check=True)


def build_single_plugin(plugin_dir: Path) -> None:
    ui_files = list(plugin_dir.rglob("*.ui"))
    if not ui_files:
        print(f"No .ui files found in {plugin_dir}. Skipping.")
        return

    for ui_file in ui_files:
        out_file = plugin_dir / f"{ui_file.stem.lower()}.py"
        print(f"Compiling {ui_file} to {out_file}...")
        subprocess.run(["pyside6-uic", str(ui_file), "-o", str(out_file)], check=True)

        print("Cleaning up generated UI files with Ruff...")
        subprocess.run(["uvx", "ruff", "check", "--fix", "--ignore", "N999", str(out_file)], check=True)  # clean up just the generated file, mainly to remove unused imports.

        subprocess.run(["uvx", "ruff", "format", str(out_file)], check=True)


def main(build_plugins: bool = False, plugins_dir_input: str = "plugins", plugin_filter: str = "") -> None:
    build_main_files()
    plugins_dir = Path(plugins_dir_input)  # throws on bad path?
    if build_plugins or plugin_filter:
        pattern = f"*{plugin_filter.lower()}*" if plugin_filter else "*"
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir() and fnmatch.fnmatch(plugin_dir.name.lower(), pattern):
                print(f"Matched plugin directory: {plugin_dir.name}")
                build_single_plugin(plugin_dir)


if __name__ == "__main__":
    if typer is not None:
        typer.run(main)
    else:
        print("Typer is not installed. Falling back to argparse.")
        parser = argparse.ArgumentParser()
        parser.add_argument("--build-plugins", action="store_true", help="Build plugin UI files")
        parser.add_argument("--plugins-dir", type=Path, default=Path("plugins"), help="Directory containing the plugins")
        parser.add_argument("--plugin-filter", type=str, default="", help="Filter for plugin directories")
        args = parser.parse_args()
        main(build_plugins=args.build_plugins, plugins_dir_input=args.plugins_dir, plugin_filter=args.plugin_filter)
