# NITRO30022-Backend
Backend repository for the capstone project for COMP30022
Created by team Nitrogen:
Isaac Parsons
Peh Ni tan
Surya Venkatesh
Pablo Li
Sebastian Tobin-Couzens

# Instructions for Docker
- Need to have docker installed (including docker-compose)
- Run ```docker-compose run web``` in the project directory
- You can then access the server from port 8081

# Instructions for building documentation with Sphinx

Build documentation with:

from root folder:
- ```sphinx-build -b html docs/ docs/_build/```  ; or
- ```python -m sphinx -b html docs/ docs/_build/```

from docs/:
- ```make html```

html source can be found in `docs/_build/`

open `docs/_build/index.html` in browser to view   