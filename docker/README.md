# Container Support
Here's everything needed to run FIFA Tracker in containers.  
  
It uses `docker` for the conatiners and `docker-compose` to coorindate the database and web containers. 

- [Container Support](#container-support)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
  - [Install Docker](#install-docker)
  - [Prepare Containers](#prepare-containers)
  - [Load Data](#load-data)
  - [Cleanup and Finish](#cleanup-and-finish)
- [Technical Details](#technical-details)
  - [docker-compose.yml](#docker-composeyml)
  - [Dockerfile-webapp](#dockerfile-webapp)
  - [install_extension.sql](#install_extensionsql)
  - [post-run bash scripts](#post-run-bash-scripts)
  - [.env](#env)

# Configuration
* Ensure you set the database username and passwords and SECRET_KEY located in `.env` and `docker-compose.yml`. 
* Also configure your ALLOWED_HOSTS in the `.env` file to contain the external facing IP of your server. 

# Getting Started

## Install Docker
* Prepare a container host to run the docker containers. For this testing a `Debian 9` host was used. 
* Install preqs (via: https://docs.docker.com/engine/install/debian/)
    ```
    sudo apt update
    sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common
    ```
* Install Docker's GPG Key
  ```
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
  ```
* Add Docker repo
  ```
  sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
  ```
* Install Docker Engine
  ```
  sudo apt update
  sudo apt install docker-ce docker-ce-cli containerd.io
  ```
* Install docker-compose (https://docs.docker.com/compose/install/)
  ```
  sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

  sudo chmod +x /usr/local/bin/docker-compose
  ```
  
## Prepare Containers
* Grab this repo into your working directory via `git clone`
* Configure the database usernames, passwords and the web server ALLOWED_HOSTS and SECRET_KEY in the `.env` and `docker-compose.yml` files. See [Configuration](#configuration)
* Navigate into root directory of repo. You should see `docker-compose.yml` in your working directory

* Build docker containers via docker-compose
  ```
  docker-compose build
  ```
* Start the docker conatiners via docker-compose
  ```
  docker-compose up
  ```
## Load Data
In another terminal run the following to initialise the data. Only need to do this once.
> Notice the name of the docker container called. e.g. `fifa-tracker_web_1` or `fifa-tracker_db_1`. Take a look at `docker ps` for the name of your containers
* Load database schemas and kickoff migrations
  ```
  docker exec fifa-tracker_web_1 sh manage_migrations.sh
  ```
* Fix datausersplayers
  ```
  docker exec fifa-tracker_web_1 sh manage_datausersplayers.sh
  ```
* Load database data
  ```
  docker exec fifa-tracker_db_1 sh /load_csvs.sh
  ```
  > There will be the following errors. Not sure how to handle them. If you're not using FIFA 17 or 18 it probably doesn't matter.   
  > `ERROR:  relation "dataplayernames18" does not exist`  
  > `ERROR:  relation "datanations18" does not exist`  
  > `ERROR:  duplicate key value violates unique constraint "dataplayernames17_pkey"`

## Cleanup and Finish
* Restart docker container to ensure changes took effect
  ```
  docker-compose stop
  docker-compose up
  ```
* All done! Access web url via `http://<your-ip>:8000`

# Technical Details
Here's a description of all the files and their usage. If you just want to run the app, feel free to ignore this section.

## docker-compose.yml
This file coordinates the database and web container. It's what's used to fire up the two docker containers. They include what to run when the container starts, how to ensure they're running healthy, and any environment, network, or disk volumes required.   

The two containers talk to eachother on back channels that docker compose configures.   

The database stores all of it's data on the `db-data` volume that persists across restarts. 

It needs to be at the root of the repo so it can reference files at the root. 

## Dockerfile-webapp
This file sets up the environment for the web container. They need to be at the root of the repo so they can reference files at the root. 
No Dockerfile is needed for the database since there are no environment changes needed to the image (besides adding a few files that docker-compose volumes handles.)

## install_extension.sql
When the postgres container starts for the first time it will look in `docker-entrypoint-initdb.d/` for any sql files to execute. The `install_extension.sql` will then get executed to add the `unaccent` extension. 

## post-run bash scripts
A few bash scripts are need to run after the first start of containers to initialize data. These will need to be manually run. The order is as follows. 

1. `manage_migrations.sh`: This will initialize the django webapp and add some tables the database. Run this inside the web container. 
2. `manage_datausersplayers.sh`: This initializes a few more fields in django and the database. Run this inside the web container. 
3. `load_csvs.sh`: This loads in default data into the database. 

## .env
Stores configuration information about the webapp. Ideally we should be using `secret_settings.py` but that was not being referenced, so we fall back to using `.env`. 