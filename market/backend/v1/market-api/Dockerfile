# Docker config for the Selene skill service

# The selene-shared parent image contains all the common Docker configs for
# all Selene apps and services see the "shared" directory in this repository.
FROM selene-shared:latest
LABEL description="Run the API for the Mycroft marketplace"

# Load the skill service application to the image
COPY market_api /opt/selene/market_api
WORKDIR /opt/selene/

# Use pipenv to install the package's dependencies in the container
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system

# Now that pipenv has installed all the packages required by selene-util
# the Pipfile can be removed from the container.
RUN rm /opt/selene/Pipfile
RUN rm /opt/selene/Pipfile.lock

EXPOSE 5002

# Use gunicorn to serve the API
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5002", "market_api.api:marketplace"]
