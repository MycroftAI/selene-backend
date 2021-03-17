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
FROM python:3.7-slim as base-build
RUN apt-get update && apt-get -y install gcc git
RUN python3 -m pip install pipenv
RUN mkdir -p /root/allure /opt/selene/selene-backend /root/code-quality /var/log/mycroft
WORKDIR /opt/selene/selene-backend
ENV DB_HOST selene-db
ENV DB_NAME mycroft
ENV DB_PASSWORD adam
ENV DB_USER selene
ENV JWT_ACCESS_SECRET access-secret
ENV JWT_REFRESH_SECRET refresh-secret
ENV REDIS_HOST selene-cache
ENV REDIS_PORT 6379
ENV SALT testsalt
ENV SELENE_ENVIRONMENT dev

# Put the copy of the shared library code in its own section to avoid reinstalling base software every time
FROM base-build as selene-base
COPY shared shared

# Code quality scripts and user agreements are stored in the MycroftAI/devops repository.  This repository is private.
# builds for publicly available images should not use this build stage.
#
# The GitHub API key is sensitive information and can change depending on who is running the application.
# It is used here to clone the private MycroftAI/devops repository.
FROM selene-base as devops-build
ARG github_api_key
ENV GITHUB_API_KEY=$github_api_key
RUN mkdir -p /opt/mycroft
WORKDIR /opt/mycroft
RUN git clone https://$github_api_key@github.com/MycroftAI/devops.git
WORKDIR /opt/mycroft/devops/jenkins
RUN pipenv install

# Run a linter and code formatter against the API specified in the build argument
FROM devops-build as api-code-check
ARG api_name
WORKDIR /opt/selene/selene-backend
COPY api/${api_name} api/${api_name}
WORKDIR /opt/selene/selene-backend/api/${api_name}
RUN pipenv install --dev
ENV PYTHONPATH=$PYTHONPATH:/opt/selene/selene-backend/api/${api_name}
WORKDIR /opt/mycroft/devops/jenkins
ENTRYPOINT ["pipenv", "run", "python", "-m", "pipeline.code_check", "--repository", "selene-backend", "--base-dir", "/opt/selene"]

# Bootstrap the Selene database as it will be needed to run any Selene applications.
FROM devops-build as db-bootstrap
ENV POSTGRES_PASSWORD selene
WORKDIR /opt/selene/selene-backend
COPY db db
WORKDIR /opt/selene/selene-backend/db
RUN pipenv install
ENTRYPOINT ["pipenv", "run", "python", "scripts/bootstrap_mycroft_db.py"]

# Run the tests defined in the Account API
FROM selene-base as account-api-test
ARG stripe_api_key
ENV PANTACOR_API_TOKEN pantacor-token
ENV PANTACOR_API_BASE_URL pantacor.test.url
ENV PYTHONPATH=$PYTHONPATH:/opt/selene/selene-backend/api/account
ENV STRIPE_PRIVATE_KEY $stripe_api_key
COPY api/account api/account
WORKDIR /opt/selene/selene-backend/api/account
RUN pipenv install --dev
WORKDIR /opt/selene/selene-backend/api/account/tests
ENTRYPOINT ["pipenv", "run", "behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", "/root/allure/allure-result"]

# Run the tests defined in the Single Sign On API
FROM selene-base as sso-api-test
ARG github_client_id
ARG github_client_secret
ENV PYTHONPATH=$PYTHONPATH:/opt/selene/selene-backend/api/sso
ENV JWT_RESET_SECRET reset-secret
# The GitHub client ID and secret are sensitive information and can change depending on who is running the application.
# They are used here to facilitate user authentication using a GitHub account.
ENV GITHUB_CLIENT_ID $github_client_id
ENV GITHUB_CLIENT_SECRET $github_client_secret
COPY api/sso api/sso
WORKDIR /opt/selene/selene-backend/api/sso
RUN pipenv install --dev
WORKDIR /opt/selene/selene-backend/api/sso/tests
ENTRYPOINT ["pipenv", "run", "behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", "/root/allure/allure-result"]

# Run the tests defined in the Public Device API
FROM selene-base as public-api-test
RUN mkdir -p /opt/selene/data
ARG google_stt_key
ARG wolfram_alpha_key
ENV PANTACOR_API_TOKEN pantacor-token
ENV PANTACOR_API_BASE_URL pantacor.test.url
ENV PYTHONPATH=$PYTHONPATH:/opt/selene/selene-backend/api/public
ENV GOOGLE_STT_KEY $google_stt_key
ENV SENDGRID_API_KEY test_sendgrid_key
ENV WOLFRAM_ALPHA_KEY $wolfram_alpha_key
ENV WOLFRAM_ALPHA_URL https://api.wolframalpha.com
COPY api/public api/public
WORKDIR /opt/selene/selene-backend/api/public
RUN pipenv install --dev
WORKDIR /opt/selene/selene-backend/api/public/tests
ENTRYPOINT ["pipenv", "run", "behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", "/root/allure/allure-result"]
