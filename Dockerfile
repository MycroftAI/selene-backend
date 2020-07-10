# Multi-stage Dockerfile for running Selene APIs or their test suites.
#
# ASSUMPTION:
#   This Dockerfile assumes its resulting containers will run on a Docker network.  A Postgres container named
#   "selene-db" and a Redis container named "selene-cache" also need to be running on this network.  To create the
#   network and the Postgres/Redis containers, use the following commands:
#       docker network create --driver bridge <network name>
#       docker run -d --net <network name> --name selene-cache redis:6
#       docker run -d -e POSTGRES_PASSWORD=selene --net <network name> --name selene-db postgres:10
#   The DB_HOST environment variable is set to the name of the Postgres container and the REDIS_HOST environment
#   variable is set to the name of he Redis container.  When running images created from this Dockerfile, include the
#   "--net <network name>" argument.

# Build steps that apply to all of the selene applications.
FROM python:3.7-slim as selene-base
RUN apt-get update && apt-get -y install gcc git
RUN python3 -m pip install pipenv
RUN mkdir -p /root/allure /opt/selene/selene-backend /root/code-quality /var/log/mycroft
WORKDIR /opt/selene
ENV DB_HOST selene-db
ENV DB_PASSWORD adam
ENV SELENE_ENVIRONMENT dev
ENV DB_NAME mycroft
ENV DB_USER selene
ENV JWT_ACCESS_SECRET access-secret
ENV JWT_REFRESH_SECRET refresh-secret
ENV SALT testsalt
ENV REDIS_HOST selene-cache
ENV REDIS_PORT 6379

# Code quality scripts and user agreements are stored in the MycroftAI/devops repository.  This repository is private.
# builds for publicly available images should not use this build stage.
FROM selene-base as devops-build
ARG github_api_key
ENV GITHUB_API_KEY=$github_api_key
RUN mkdir -p /opt/mycroft
WORKDIR /opt/mycroft
RUN git clone https://$github_api_key@github.com/MycroftAI/devops.git

# Bootstrap the Selene database as it will be needed to run any Selene applications.
FROM devops-build as db-bootstrap
ENV POSTGRES_PASSWORD selene
# TODO: remove when the feature/agreements branch is merged.
WORKDIR /opt/mycroft/devops
RUN git checkout feature/agreements
WORKDIR /opt/selene/selene-backend
COPY db db
WORKDIR /opt/selene/selene-backend/db
RUN pipenv install
ENTRYPOINT ["pipenv", "run", "python", "scripts/bootstrap_mycroft_db.py"]

# Run the tests defined in the Account API
FROM selene-base as account-api-test
ENV PYTHONPATH=$PYTHONPATH:/opt/selene/selene-backend/api/account
ENV STRIPE_PRIVATE_KEY totally_fake_api_key
WORKDIR /opt/selene/selene-backend
COPY shared shared
COPY api/account api/account
WORKDIR /opt/selene/selene-backend/api/account
RUN pipenv install --dev
WORKDIR /opt/selene/selene-backend/api/account/tests
ENTRYPOINT ["pipenv", "run", "behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", "/root/allure/allure-result"]
