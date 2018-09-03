# Docker config for the Selene skill service

# The selene-shared parent image contains all the common Docker configs for
# all Selene apps and services see the "shared" directory in this repository.
FROM docker.mycroft.ai/selene-shared:latest
LABEL description="Selene Skill Service API"

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

# Use gunicorn to serve the API
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5000", "skill_service.api.api:skill"]
