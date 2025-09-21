import sys
from pathlib import Path
from jupyterlab.labapp import main

def run_notebook():
    main([str(Path(sys.prefix, "share/notebooks", "pytelecomm.ipynb").resolve())])
