import sys
from pathlib import Path
from jupyterlab.labapp import main
# from . import run_notebook

def run_notebook():
    main([Path(sys.prefix, "share/notebooks", "pytelecomm.ipynb")])

if __name__ == "__main__":
	 run_notebook()
