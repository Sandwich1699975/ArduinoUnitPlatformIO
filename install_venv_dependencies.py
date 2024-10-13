# ---------------------- PIO SCRIPTING ----------------------
# https://docs.platformio.org/en/stable/scripting/examples/extra_python_packages.html
# Do not format the PIO scripting code. It must be before python imports
# noqa: off
Import("env") # type: ignore

# List installed packages
env.Execute("$PYTHONEXE -m pip list") # type: ignore

# Install custom packages from the PyPi registry
env.Execute("$PYTHONEXE -m pip install logic2-automation") # type: ignore

# Install missed package
try:
    from saleae import automation
except ImportError:
    env.Execute("$PYTHONEXE -m pip install logic2-automation") # type: ignore
# noqa: on 
# ---------------------- PIO SCRIPTING ----------------------