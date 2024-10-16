import os

# This file currently does nothing

Import("env")

print("Running python prerequisites")

# Add include folder to python path
env.Execute(
    f'export PYTHONPATH="{os.path.join("$PROJECT_DIR", "test", "embedded","include")}:$PYTHONPATH')

# List installed packages
env.Execute("$PYTHONEXE -m pip list")

# Install custom packages from the PyPi registry
env.Execute("$PYTHONEXE -m pip install logic2-automation")

# Install missed package
try:
    import saleae
except ImportError:
    env.Execute("$PYTHONEXE -m pip install logic2-automation")
