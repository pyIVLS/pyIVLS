# pyIVLS

**pyIVLS** is a Python-based **Versatile Lab System** designed for modular scientific measurement and control.

But what does “IVLS” really mean?

It depends on what you need:

- **Instrumented Versatile Lab System** – supports modular hardware plugins and precise control of instruments
- **Intelligent Versatile Lab System** – includes AI-driven probe positioning and real-time data fitting
- **Interactive Versatile Lab System** – GUI-driven workflows and user-friendly plugin design
- **IV/Light/Spectra** – originally built for current-voltage and optical measurements, but easily extended

**You decide what pyIVLS means for your lab.**

## Running 
The entry point for the software is pyIVLS.py. Package requirements are provided in pyproject.toml and requirements.txt.

## Basic operation
Add the plugins you need from tools->plugins. If the plugin you need isn't visible in the list, click "upload new plugin" and select the folder containing the plugin code and .ini file with plugin metadata and default settings.
Then load in the necessary plugins and click "Apply". Then, set the settings as you need them and create the measurement sequence (See [docs](./docs/sweep_tutorial.md) for a detailed example.)
