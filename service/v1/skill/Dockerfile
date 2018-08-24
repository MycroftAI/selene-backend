# Docker config for the Selene skill service

# The selene-shared parent image contains all the common Docker configs for
# all Selene apps and services see the "shared" directory in this repository.
FROM selene-shared:latest
LABEL description="Run the Selene skill service"

# Configuration files for the software loaded in this image.
COPY config /opt/selene/config
RUN mkdir -p /var/log/gunicorn/
RUN mkdir -p /var/log/gunicorn/

# Load the skill service application to the image
COPY skill_service /opt/selene/skill_service
WORKDIR /opt/selene/

# Use pipenv to install the package's dependencies in the container
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system

# Now that pipenv has installed all the packages required by selene-util
# the Pipfile can be removed from the container.
RUN rm /opt/selene/Pipfile
RUN rm /opt/selene/Pipfile.lock

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--config=/opt/selene/config/gunicorn_config.py", "skill_service.api.api:skill"]
