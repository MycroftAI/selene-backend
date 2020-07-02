# Multi-stage Dockerfile for running Selene APIs or their test suites.

# Build an environment that can run any of the selene applications.
FROM python:3.7-slim as selene-base
RUN apt-get update && apt-get -y install gcc git
RUN python3 -m pip install pipenv
RUN mkdir -p /root/allure /opt/selene/selene-backend /root/code-quality /var/log/mycroft
WORKDIR /opt/selene
# The DB_HOST environment variable assumes there is a Postgres Docker container named "selene-db"
# running on the same Docker network as any container originating from an image defined in this Dockerfile.
ENV DB_HOST selene-db
ENV DB_PASSWORD adam

FROM selene-base as devops-build
ARG github_api_key
ENV GITHUB_API_KEY=$github_api_key
RUN mkdir -p /opt/mycroft
WORKDIR /opt/mycroft
RUN git clone https://$github_api_key@github.com/MycroftAI/devops.git

# Bootstrap the Selene database as it will be needed to run any Selene applications
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
