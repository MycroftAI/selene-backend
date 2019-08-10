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
- `cd ~/`
- `git clone https://github.com/MycroftAI/selene-backend.git`
- `cd selene-backend`

The Python code utilizes features introduced in Python 3.7, such as data classes.  So ensure you have Python 3.7
installed.  [Pipenv](https://pipenv.readthedocs.io/en/latest/) is used for virtual environment and package management.
If you prefer to use pip and pyenv (or virtualenv), you can find the required libraries in the files named "Pipfile".

There are four APIs defined in this repository, account management, single sign on, skill marketplace and device.
The first three support account.mycroft.ai (aka home.mycroft.ai), sso.mycroft.ai, and market.mycroft.ai, respectively. 
The device API is how devices running Mycroft Core communicate with the server. Also included in this repository is
a package containing batch scripts for maintenance and the definition of the database schema.

Each API is designed to run independently of the others. Code common to each of the APIs, such as the Data Access Layer, 
can be found in the "shared" directory.  The shared code is an independent Python package required by each of the APIs. 
Each API has it's own Pipfile so that it can be run in its own virtual environment. 

# Running the Backend

TODO

# Getting Involved

This is an open source project and we would love your help. We have prepared a [contributing](.github/CONTRIBUTING.md) 
guide to help you get started.

If this is your first PR or you're not sure where to get started,
say hi in [Mycroft Chat](https://chat.mycroft.ai/) and a team member would be happy to mentor you.
Join the [Mycroft Forum](https://community.mycroft.ai/) for questions and answers.
