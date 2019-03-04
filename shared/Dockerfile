# Parent dockerfile for all Selene services and APIs
#
# This Dockerfile contains the steps that are common to building all the
# docker images for the Selene backend to Mycroft

FROM python:3.7
LABEL maintainer="Mycroft AI <devops@mycroft.ai>"

# Install the software required for this image
RUN pip install pipenv

# Use pipenv to install the dependencies for selene-util
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system

# Now that pipenv has installed all the packages required by selene-util
# the Pipfile can be removed from the container.  This makes way for the
# pepenv to use these files to install dependencies for the Selene services
# or applications that will use this Docker config
RUN rm Pipfile
RUN rm Pipfile.lock

# Copy the applicaction code to the image
COPY selene_util /opt/selene/selene_util
WORKDIR /opt/selene/
