import os

# This file currently does nothing

Import("env") # type: ignore

print("Running python prerequisites")

# List installed packages
env.Execute("$PYTHONEXE -m pip list") # type: ignore


# Install custom packages from the PyPi registry
env.Execute("$PYTHONEXE -m pip install logic2-automation") # type: ignore

# Install missed package
try:
    import saleae
except ImportError:
    env.Execute("$PYTHONEXE -m pip install logic2-automation")  # type: ignore
