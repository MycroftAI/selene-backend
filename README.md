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


# Getting Started

First, get the code on your system!  The simplest method is via git 
([git installation instructions](https://gist.github.com/derhuerst/1b15ff4652a867391f03)):
```
cd ~/
git clone https://github.com/MycroftAI/selene-backend.git
cd selene-backend
```

There are four APIs defined in this repository, account management, single sign on, skill marketplace and device.
The first three support account.mycroft.ai (aka home.mycroft.ai), sso.mycroft.ai, and market.mycroft.ai, respectively. 
The device API is how devices running Mycroft Core communicate with the server. Also included in this repository is
a package containing batch scripts for maintenance and the definition of the database schema.

Each API is designed to run independently of the others. Code common to each of the APIs, such as the Data Access Layer, 
can be found in the "shared" directory.  The shared code is an independent Python package required by each of the APIs. 
Each API has it's own Pipfile so that it can be run in its own virtual environment. 

# Installation
The Python code utilizes features introduced in Python 3.7, such as data classes. 
[Pipenv](https://pipenv.readthedocs.io/en/latest/) is used for virtual environment and package management.
If you prefer to use pip and pyenv (or virtualenv), you can find the required libraries in the files named "Pipfile".
These instructions will use pipenv commands.

If the Selene applications will be servicing a large number of devices (enterprise usage, for example), it is 
recommended that each of the applications run on their own server or virtual machine. This configuration makes it
easier to scale and monitor each application independently.  However, all applications can be run on a single server. 
This configuration is could be more practical for a household running a handful of devices. 

These instructions will assume a multi-server setup for several thousand devices. To run on a single server servicing a 
small number of devices, the recommended system requirements are 4 CPU, 8GB RAM and 100GB of disk.

## Postgres DB
### Recommended Server Configuration 
Ubuntu 18.04 LTS, 2 CPU, 4GB RAM, 50GB disk.
###Installation Procedure
* Use a package management system to install Python 3.7, Python 3 pip and PostgreSQL 10  
```bash
sudo apt-get install postgresql python3.7 python
```
* Set Postgres to start on boot  
```bash
sudo systemctl enable postgresql
```
* Clone the selene-backend and documentation repositories
```bash
sudo mkdir -p /opt/selene
sudo chown -R mycroft:users /opt/selene
cd /opt/selene
git clone https://github.com/MycroftAI/selene-backend.git
```
* Create the virtual environment for the database code
```bash
sudo Python3.7 -m pip install pipenv
cd /opt/selene/selene-backend/db
pipenv install
```
* Download files from geonames.org used to populate the geography schema tables
```bash
mkdir -p /opt/selene/data
cd /opt/selene/data
wget http://download.geonames.org/export/dump/countryInfo.txt
wget http://download.geonames.org/export/dump/timeZones.txt
wget http://download.geonames.org/export/dump/admin1CodesASCII.txt
wget http://download.geonames.org/export/dump/cities500.zip
```
* Generate secure passwords for the postgres user and selene user on the database
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '<new password>'"
sudo -u postgres psql -c "CREATE ROLE selene WITH LOGIN ENCRYPTED PASSWORD '<password>'"
```
* Add environment variables containing these passwords for the bootstrap script
```bash
export DB_PASSWORD=<selene user password>
export POSTGRES_PASWORD=<postgres user password>
```
* Run the bootstrap script
```bash
cd /opt/selene/selene-backend/db/scripts
pipenv run python bootstrap_mycroft_db.py
```
# Running the Backend

TODO

# Getting Involved

This is an open source project and we would love your help. We have prepared a [contributing](.github/CONTRIBUTING.md) 
guide to help you get started.

If this is your first PR or you're not sure where to get started,
say hi in [Mycroft Chat](https://chat.mycroft.ai/) and a team member would be happy to mentor you.
Join the [Mycroft Forum](https://community.mycroft.ai/) for questions and answers.
