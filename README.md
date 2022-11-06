# NITRO30022-Backend
Backend repository for the capstone project for COMP30022
Created by team Nitrogen:
Isaac Parsons
Peh Ni tan
Surya Venkatesh
Pablo Li
Sebastian Tobin-Couzens

# Installing Dependencies

- Install python 3.7 or newer version
- To install module dependencies, run:

```pip install -r requirements.txt```

# Instructions for Docker
- Need to have docker installed (including docker-compose)
- Run `docker-compose run web` in the project directory
- You can then access the server from port 8081

# Required fields in the .env file
- For the server to successfully run, you need to have a .env file in the root directory with the following fields:
  - MONGODB_USERNAME: The MongoDB username you used for your database
  - MONGO_DB_PASSWORD: The password you set for the database
  - MONGO_DB_HOST: The host of the MongoDB server.
  
- If you are planning to run it together with Docker, then also include these fields:
  - AWS_ACCESS_KEY_ID 
  - AWS_SECRET_ACCESS_KEY
  - AWS_STORAGE_BUCKET_NAME
  - AWS_S3_SIGNATURE_VERSION 
  - AWS_S3_REGION_NAME

# Required Repo Keys & Secrets
- Deploy Keys:
  - SHA:256 key for giving AWS access to this repo, may have any titled, currently "AWS Key"
- Secrets (Actions):
  - RSA private key for accessing AWS via github actions, titled "AWS_PRIVATE_KEY"
  - hostname of deployed site, titled "HOSTNAME"
  - OS profile used on AWS, titled "USER_NAME"
  
# Instructions for Running the Backend Server
- From the home directory run:

``` python manage.py runserver <optional port number>```
- You can either specify a port number for the server to run on
- If left blank, port defaults to 3000
- Make sure you have all modules in the requirement.txt file installed
- Make sure you have python 3 installed (Preferably above version 3.7)

# Instructions for Running Tests
- From the home directory run:

``` python manage.py test <optional specific module>```
- You can either specify an app to test
- Or leave it blank which runs the test files located in each test folder in each app

# Instructions for Building Code Documentation with Sphinx

- Create documentation .rst source files in /docs/pages/
- Set page hierarchy in /docs/index.rst
- Build documentation with:
  - from root folder:
    
    ```sphinx-build -b html docs/ docs/_build/```  ; or
    
    ```python -m sphinx -b html docs/ docs/_build/```
  - from `/docs/`:
    
    ```make html```
- html source can be found in `docs/_build/`
- open `docs/_build/index.html` in browser to view   
- Can be easily scaled up with the project & customized via sphinx extensions, or hosted
