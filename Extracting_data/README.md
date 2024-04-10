# Introduction


- This is the introduction to the Extract part of this project. 
- We will going through setting up the Docker Container with Postgresql DBMS and PGAdmin for monitoring
- Writing Python script to connect to Postgresql, create table inside it, read csv file and insert it in the database




# Setting up Docker and Postgresql



## Setting .env file: 


- First, you can git clone this repo into your working repository by copy this line to your terminal (or Powershell) :

  ```cmd 
  git clone https://github.com/CyTusSi1ver1197/london_bike_map.git 
  ```

- Then move into the `Extracting_data` directory:

    ```cmd
    cd .\Extracting_data
    ``` 

- In there, create a `.env` file like this:
  
  ```py
    POSTGRES_HOST="localhost"
    POSTGRES_USER="postgres"
    POSTGRES_PASS="12345678"
    POSTGRES_DB="postgres"
    POSTGRES_DB_SCHEMA="public"
    POSTGRES_TABLE="journey_bike_trip"
    POSTGRES_PORT=5433
    DOCKER_POSTGRES_PORT="5433:5432"
    DOCKER_PGADMIN_PORT="8080:80"
  ```
- With:
  
    **POSTGRES_HOST**:

    - This variable specifies the hostname or IP address of the PostgreSQL database server.

    **POSTGRES_USER**:

    - This variable specifies the username used to authenticate with the PostgreSQL database server.

    **POSTGRES_PASS**:

    - This variable specifies the password used to authenticate with the PostgreSQL database server.

    **POSTGRES_DB**:

    - This variable specifies the name of the PostgreSQL database.

    **POSTGRES_DB_SCHEMA**:

    - This variable specifies the schema within the PostgreSQL database where tables and other database objects are located.

    **POSTGRES_TABLE**:

    - This variable specifies the name of the table within the PostgreSQL database.

    **POSTGRES_PORT**:

    - This variable specifies the port number on which the PostgreSQL database server is running.

    **DOCKER_POSTGRES_PORT**:

    - This variable specifies the port number on which the PostgreSQL Docker container is configured to listen.

    **DOCKER_PGADMIN_PORT**:

    - This variable specifies the port number on which the pgAdmin Docker container is configured to listen.

- After configuring the `.env` file has been completed, we can start on creating a Docker container for Postgresql and PGAdmin

    ## Setting Postgresql:

- Opening the `docker-postgres.yml` file to configure more as you like but if you just need a working database, just run:

    ```
    docker compose -f .\Extracting_data\docker-postgres.yml up -d
    ```
- Opening any browser, go to `http://localhost:8080/` to login to the pgAdmin, if succeeded, the browser would look like this:

    ![pgAdmin image](/Images/pgAdmin.png)

- Inputing `email` and `password` the value of `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` in `docker-postgres.yml` respectively to complete the login process, the GUI should look like this:

    ![pgAdmin user image](/Images/pgAdmin_GUI.png)

- Choose the `Add New Server` icon, it will show an icon like this:

    ![pgAdmin server connection](/Images/pgAdmin_server_01.png)

- Choose the `Name` part any name you like then move on to the `Connection` setion:

    ![pgAdmin server connection](/Images/pgAdmin_server_02.png)

- Then, to completely connect to the database, fill in these sections:
  - `Host name/address`: `POSTGRES_HOST`
  - `Port`: 5432
  - `Username`: `POSTGRES_USER`
  - `Password`: `POSTGRES_PASS`

- The rest could be left as blank, then choose `SAVE` and you have completed connecting to Postgresql on Docker!

    ![pgAdmin server connection](/Images/pgAdmin_completed.png)

## Setting up Python script

- Go back to `.env` file and add this line to the end off file:

    ```py
    URL="s3://cycling.data.tfl.gov.uk/usage-stats/"
    ```
- This is where we will retrieve the csv files to put on the database
