# Docker config for the Selene skill service

# The selene-shared parent image contains all the common Docker configs for
# all Selene apps and services see the "shared" directory in this repository.
FROM docker.mycroft.ai/selene-shared:2018.4
LABEL description="Run the API for the Mycroft login screen"

# Use pipenv to install the package's dependencies in the container
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system

# Now that pipenv has installed all the packages required by selene-util
# the Pipfile can be removed from the container.
RUN rm Pipfile
RUN rm Pipfile.lock

# Load the skill service application to the image
COPY sso_api /opt/selene/sso_api
WORKDIR /opt/selene/

EXPOSE 7102

# Use uwsgi to serve the API
COPY uwsgi.ini uwsgi.ini
ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]