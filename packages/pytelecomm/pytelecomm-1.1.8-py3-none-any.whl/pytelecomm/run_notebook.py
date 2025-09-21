#!/usr/bin/env python

import sys
from pathlib import Path
from jupyterlab.labapp import main

if __name__ == "__main__":
	 main(Path(sys.prefix, "share/notebooks", "pytelecomm.ipynb"))
