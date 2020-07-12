[![License](https://img.shields.io/badge/License-GNU_AGPL%203.0-blue.svg)](LICENSE) 
[![CLA](https://img.shields.io/badge/CLA%3F-Required-blue.svg)](https://mycroft.ai/cla) 
[![Team](https://img.shields.io/badge/Team-Mycroft_Backend-violetblue.svg)](https://github.com/MycroftAI/contributors/blob/master/team/Mycroft%20Backend.md) 
![Status](https://img.shields.io/badge/-Production_ready-green.svg)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Join chat](https://img.shields.io/badge/Mattermost-join_chat-brightgreen.svg)](https://chat.mycroft.ai)


Selene -- Mycroft's Server Backend
==========

Selene provides the services used by [Mycroft Core](https://github.com/mycroftai/mycroft-core) to manage devices, skills
and settings.  It consists of two repositories.  This one contains Python and SQL representing the database definition, 
data access layer, APIs and scripts.  The second repository, [Selene UI](https://github.com/mycroftai/selene-ui), 
contains Angular web applications that use the APIs defined in this repository.

There are four APIs defined in this repository, account management, single sign on, skill marketplace and device.
The first three support account.mycroft.ai (aka home.mycroft.ai), sso.mycroft.ai, and market.mycroft.ai, respectively. 
The device API is how devices running Mycroft Core communicate with the server. Also included in this repository is
a package containing batch scripts for maintenance and the definition of the database schema.

Each API is designed to run independently of the others. Code common to each of the APIs, such as the Data Access Layer, 
can be found in the "shared" directory.  The shared code is an independent Python package required by each of the APIs. 
Each API has its own Pipfile so that it can be run in its own virtual environment. 

# Installation
The Python code utilizes features introduced in Python 3.7, such as data classes. 
[Pipenv](https://pipenv.readthedocs.io/en/latest/) is used for virtual environment and package management.
If you prefer to use pip and pyenv (or virtualenv), you can find the required libraries in the files named "Pipfile".
These instructions will use pipenv commands.

If the Selene applications will be servicing a large number of devices (enterprise usage, for example), it is 
recommended that each of the applications run on their own server or virtual machine. This configuration makes it
easier to scale and monitor each application independently.  However, all applications can be run on a single server. 
This configuration could be more practical for a household running a handful of devices. 

These instructions will assume a multi-server setup for several thousand devices. To run on a single server servicing a 
small number of devices, the recommended system requirements are 4 CPU, 8GB RAM and 100GB of disk.  There are a lot of
manual steps in this section that will eventually be replaced with an installation script.

All Selene applications are time zone agnostic.  It is recommended that the time zone on any server running Selene be UTC.

## Postgres DB
* Recommended server configuration: Ubuntu 18.04 LTS, 2 CPU, 4GB RAM, 50GB disk.
* Use the package management system to install Python 3.7, Python 3 pip and PostgreSQL 10  
```
sudo apt-get install postgresql python3.7 python
```
* Set Postgres to start on boot  
```
sudo systemctl enable postgresql
```
* Clone the selene-backend and documentation repositories
```
sudo mkdir -p /opt/selene
sudo chown -R mycroft:users /opt/selene
cd /opt/selene
git clone https://github.com/MycroftAI/selene-backend.git
```
* Create the virtual environment for the database code
```
sudo apt-get install python3-pip
sudo Python3.7 -m pip install pipenv
cd /opt/selene/selene-backend/db
pipenv install
```
* Download files from geonames.org used to populate the geography schema tables
```
mkdir -p /opt/selene/data
cd /opt/selene/data
wget http://download.geonames.org/export/dump/countryInfo.txt
wget http://download.geonames.org/export/dump/timeZones.txt
wget http://download.geonames.org/export/dump/admin1CodesASCII.txt
wget http://download.geonames.org/export/dump/cities500.zip
```
* Generate secure passwords for the postgres user and selene user on the database
```
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '<new password>'"
sudo -u postgres psql -c "CREATE ROLE selene WITH LOGIN ENCRYPTED PASSWORD '<password>'"
```
* Add environment variables containing these passwords for the bootstrap script
```
export DB_PASSWORD=<selene user password>
export POSTGRES_PASSWORD=<postgres user password>
```
* Run the bootstrap script
```
cd /opt/selene/selene-backend/db/scripts
pipenv run python bootstrap_mycroft_db.py
```
* By default, Postgres only listens on localhost.  This will not do for a multi-server setup.  Change the 
`listen_addresses` value in the `posgresql.conf` file to the private IP of the database server.  This file is owned by
the `postgres` user so use the following command to edit it (substituting vi for your favorite editor)
```
sudo -u postgres vi /etc/postgres/10/main/postgresql.conf
```
* By default, Postgres only allows connections from localhost.  This will not do for a multi-server setup either.  Add
an entry to the `pg_hba.conf` file for each server that needs to access this database.  This file is also owned by
the `postgres` user so use the following command to edit it (substituting vi for your favorite editor)
```
sudo -u postgres vi /etc/postgres/10/main/pg_hba.conf
```
* Instructions on how to update the `pg_hba.conf` file can be found in 
[Postgres' documentation](https://www.postgresql.org/docs/10/auth-pg-hba-conf.html).  Below is an example for reference.
```
# IPv4 Selene connections
host    mycroft         selene          <private IP address>/32          md5
```
* Restart Postgres for the `postgres.conf` and `pg_hba.conf` changes to take effect.
```
sudo systemctl restart postgresql
```
## Redis DB
* Recommended server configuration: Ubuntu 18.04 LTS, 1 CPU, 1GB RAM, 5GB disk.
So as to not reinvent the wheel, here are some easy-to-follow instructions for 
[installing Redis on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04).
* By default, Redis only listens for One additional step is to change the "bind" variable in /etc/redis/redis.conf to be the private IP of the Redis host.
## APIs
The majority of the setup for each API is the same.  This section defines the steps common to all APIs. Steps specific
to each API will be defined in their respective sections.
* Add an application user to the VM. Either give this user sudo privileges or execute the sudo commands below as a user
with sudo privileges.  These instructions will assume a user name of "mycroft"
* Use the package management system to install Python 3.7, Python 3 pip and Python 3.7 Developer Tools 
```
sudo apt install python3.7 python3-pip python3.7-dev 
sudo python3.7 -m pip install pipenv
```
* Setup the Backend Application Directory
```
sudo mkdir -p /opt/selene
sudo chown -R mycroft:users /opt/selene
```
* Setup the Log Directory
```
sudo mkdir -p /var/log/mycroft
sudo chown -R mycroft:users /var/log/mycroft
```
* Clone the Selene Backend Repository
```
cd /opt/selene
git clone https://github.com/MycroftAI/selene-backend.git
```
* If running in a test environment, be sure to checkout the "test" branch of the repository
## Single Sign On API
Recommended server configuration: Ubuntu 18.04 LTS, 1 CPU, 1GB RAM, 5GB disk
* Create the virtual environment and install the requirements for the application
```
cd /opt/selene/selene-backend/sso
pipenv install
```
## Account API
* Recommended server configuration: Ubuntu 18.04 LTS, 1 CPU, 1GB RAM, 5GB disk
* Create the virtual environment and install the requirements for the application
```
cd /opt/selene/selene-backend/account
pipenv install
```
## Marketplace API
* Recommended server configuration: Ubuntu 18.04 LTS, 1 CPU, 1GB RAM, 10GB disk
* Create the virtual environment and install the requirements for the application
```
cd /opt/selene/selene-backend/market
pipenv install
```
## Device API
* Recommended server configuration: Ubuntu 18.04 LTS, 2 CPU, 2GB RAM, 50GB disk
* Create the virtual environment and install the requirements for the application
```
cd /opt/selene/selene-backend/public
pipenv install
```
# Running the APIs
Each API is configured to run on port 5000.  This is not a problem if each is running in its own VM but will be an
issue if all APIs are running on the same server, or if port 5000 is already in use.  To address these scenarios, 
change the port numbering in the uwsgi.ini file for each API.
## Single Sign On API
* The SSO application uses three JWTs for authentication. First is an access key, which is required to authenticate a
user for API calls.  Second is a refresh key that automatically refreshes the access key when it expires.  Third is a
reset key, which is used in a password reset scenario.  Generate a secret key for each JWT.
* Any data that can identify a user is encrypted.  Generate a salt that will be used with the encryption algorithm.
* Access to the Github API is required to support logging in with your Github account.  Details can be found
[here](https://developer.github.com/v3/guides/basics-of-authentication/).
* The password reset functionality sends an email to the user with a link to reset their password.  Selene uses 
SendGrid to send these emails so a SendGrid account and API key are required.
* Define a systemd service to run the API.  The service defines environment variables that use the secret and API keys
generated in previous steps.
```
sudo vim /etc/systemd/system/sso_api.service
```
```
[Unit]
Description=Mycroft Single Sign On Api
After=network.target

[Service]
User=mycroft
Group=www-data
Restart=always
Type=simple
WorkingDirectory=/opt/selene/selene-backend/api/sso
ExecStart=/usr/local/bin/pipenv run uwsgi --ini uwsgi.ini
Environment=DB_HOST=<IP address or name of database host>
Environment=DB_NAME=mycroft
Environment=DB_PASSWORD=<selene database user password>
Environment=DB_PORT=5432
Environment=DB_USER=selene
Environment=GITHUB_CLIENT_ID=<github client id>
Environment=GITHUB_CLIENT_SECRET=<github client secret>
Environment=JWT_ACCESS_SECRET=<access secret>
Environment=JWT_REFRESH_SECRET=<refresh secret>
Environment=JWT_RESET_SECRET=<reset secret>
Environment=SALT=<salt value>
Environment=SELENE_ENVIRONMENT=<test/prod>
Environment=SENDGRID_API_KEY=<sendgrid API key>
Environment=SSO_BASE_URL=<base url for single sign on application>

[Install]
WantedBy=multi-user.target
```
* Start the sso_api service and set it to start on boot
```
sudo systemctl start sso_api.service
sudo systemctl enable sso_api.service
```
## Account API
* The account API uses the same authentication mechanism as the single sign on API.  The JWT_ACCESS_SECRET, 
JWT_REFRESH_SECRET and SALT environment variables must be the same values as those on the single sign on API.
* This application uses the Redis database so the service needs to know where it resides.
* Define a systemd service to run the API.  The service defines environment variables that use the secret and API keys
generated in previous steps.
```
sudo vim /etc/systemd/system/account_api.service
```
```
[Unit]
Description=Mycroft Account API
After=network.target

[Service]
User=mycroft
Group=www-data
Restart=always
Type=simple
WorkingDirectory=/opt/selene/selene-backend/api/account
ExecStart=/usr/local/bin/pipenv run uwsgi --ini uwsgi.ini
Environment=DB_HOST=<db host IP address or name>
Environment=DB_NAME=mycroft
Environment=DB_PASSWORD=<selene user database password>
Environment=DB_PORT=5432
Environment=DB_USER=selene
Environment=JWT_ACCESS_SECRET=<same as value for single sign on>
Environment=JWT_REFRESH_SECRET=<same as value for single sign on>
Environment=OAUTH_BASE_URL=<url for oauth service>
Environment=REDIS_HOST=<IP address or name of redis host>
Environment=REDIS_PORT=6379
Environment=SELENE_ENVIRONMENT=<test/prod>
Environment=SALT=<same as value for single sign on>

[Install]
WantedBy=multi-user.target
```
* Start the account_api service and set it to start on boot
```
sudo systemctl start account_api.service
sudo systemctl enable account_api.service
```
## Marketplace API
* The marketplace API uses the same authentication mechanism as the single sign on API.  The JWT_ACCESS_SECRET, 
JWT_REFRESH_SECRET and SALT environment variables must be the same values as those on the single sign on API.
* This application uses the Redis database so the service needs to know where it resides.
* Define a systemd service to run the API.  The service defines environment variables that use the secret and API keys
generated in previous steps.
```
sudo vim /etc/systemd/system/market_api.service
```
```
[Unit]
Description=Mycroft Marketplace API
After=network.target

[Service]
User=mycroft
Group=www-data
Restart=always
Type=simple
WorkingDirectory=/opt/selene/selene-backend/api/market
ExecStart=/usr/local/bin/pipenv run uwsgi --ini uwsgi.ini
Environment=DB_HOST=<db host IP address or name>
Environment=DB_NAME=mycroft
Environment=DB_PASSWORD=<selene user database password>
Environment=DB_PORT=5432
Environment=DB_USER=selene
Environment=JWT_ACCESS_SECRET=<same as value for single sign on>
Environment=JWT_REFRESH_SECRET=<same as value for single sign on>
Environment=OAUTH_BASE_URL=<url for oauth service>
Environment=REDIS_HOST=<IP address or name of redis host>
Environment=REDIS_PORT=6379
Environment=SELENE_ENVIRONMENT=<test/prod>
Environment=SALT=<same as value for single sign on>

[Install]
WantedBy=multi-user.target
```
* Start the market_api service and set it to start on boot
```
sudo systemctl start market_api.service
sudo systemctl enable market_api.service
```
* The marketplace API assumes that the skills it supplies to the web application are in the Postgres database. To get
them there, a script needs to be run to download them from Github.  The script requires the GITHUB_USER, GITHUB_PASSWORD,
DB_HOST, DB_NAME, DB_USER and DB_PASSWORD environment variables to run.  Use the same values as those in the service
definition files.
```
cd /opt/selene/selene-backend/batch
pipenv install
pipenv run python load_skill_display_data.py --core-version <specify core version, e.g. 19.02>
```

## Device API
* The device API uses the same authentication mechanism as the single sign on API.  The JWT_ACCESS_SECRET, 
JWT_REFRESH_SECRET and SALT environment variables must be the same values as those on the single sign on API.
* This application uses the Redis database so the service needs to know where it resides.
* The weather skill requires a key to the Open Weather Map API
* The speech to text engine requires a key to Google's STT API.
* The Wolfram Alpha skill requires an API key to the Wolfram Alpha API
* Define a systemd service to run the API.  The service defines environment variables that use the secret and API keys
generated in previous steps.
```
sudo vim /etc/systemd/system/public_api.service
```
```
[Unit]
Description=Mycroft Public API
After=network.target

[Service]
User=mycroft
Group=www-data
Restart=always
Type=simple
WorkingDirectory=/opt/selene/selene-backend/api/public
ExecStart=/usr/local/bin/pipenv run uwsgi --ini uwsgi.ini
Environment=DB_HOST=<db host IP address or name>
Environment=DB_NAME=mycroft
Environment=DB_PASSWORD=<selene user database password>
Environment=DB_PORT=5432
Environment=DB_USER=selene
Environment=EMAIL_SERVICE_HOST=<email host>
Environment=EMAIL_SERVICE_PORT=<email port>
Environment=EMAIL_SERVICE_USER=<email user>
Environment=EMAIL_SERVICE_PASSWORD=<email password>
Environment=GOOGLE_STT_KEY=<Google STT API key>
Environment=JWT_ACCESS_SECRET=<same as value for single sign on>
Environment=JWT_REFRESH_SECRET=<same as value for single sign on>
Environment=OAUTH_BASE_URL=<url for oauth service>
Environment=OWM_KEY=<Open Weather Map API Key>
Environment=OWM_URL=https://api.openweathermap.org/data/2.5
Environment=REDIS_HOST=<IP address or name of redis host>
Environment=REDIS_PORT=6379
Environment=SELENE_ENVIRONMENT=<test/prod>
Environment=SALT=<same as value for single sign on>
Environment=WOLFRAM_ALPHA_KEY=<Wolfram Alpha API Key
Environment=WOLFRAM_ALPHA_URL=https://api.wolframalpha.com

[Install]
WantedBy=multi-user.target
```
* Start the public_api service and set it to start on boot
```
sudo systemctl start public_api.service
sudo systemctl enable public_api.service
```
## Other Considerations
### DNS
There are multiple ways to setup DNS.  This document will not dictate how to do so for Selene.  However, here is an 
example, based on how DNS is setup at Mycroft AI...

Each application runs on its own sub-domain.  Assuming a top level domain of "mycroft.ai" the subdomains are:
* account.mycroft.ai
* api.mycroft.ai
* market.mycroft.ai
* sso.mycroft.ai

The APIs that support the web applications are directories within the sub-domain (e.g. account.mycroft.ai/api).  Since 
the device API is externally facing, it is versioned.  It's subdirectory must be "v1".

### Reverse Proxy
There are multiple tools available for setting up a reverse proxy that will point your DNS entries to your APIs.
As such, the decision on how to set this up will be left to the user.

### SSL
It is recommended that Selene applications be run using HTTPS.  To do this an SSL certificate is necessary.  
[Let's Encrypt](https://letsencrypt.org) is a great way to easily set up SSL certificates for free.


# What About the GUI???
Once the database and API setup is complete, the next step is to setup the GUI, The README file for the 
[Selene UI](https://github.com/mycroftai/selene-ui) repository contains the instructions for setting up the web 
applications.

# Getting Involved

This is an open source project and we would love your help. We have prepared a [contributing](.github/CONTRIBUTING.md) 
guide to help you get started.

If this is your first PR or you're not sure where to get started,
say hi in [Mycroft Chat](https://chat.mycroft.ai/) and a team member would be happy to mentor you.
Join the [Mycroft Forum](https://community.mycroft.ai/) for questions and answers.
