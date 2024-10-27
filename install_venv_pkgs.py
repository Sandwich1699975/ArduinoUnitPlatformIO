import os

# This file currently does nothing

Import("env")

print("Running python prerequisites")

# List installed packages
env.Execute("$PYTHONEXE -m pip list")

# Install custom packages from the PyPi registry
env.Execute("$PYTHONEXE -m pip install logic2-automation")

# Install missed package
try:
    import saleae
except ImportError:
    env.Execute("$PYTHONEXE -m pip install logic2-automation")
