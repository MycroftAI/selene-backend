# Multistage Dockerfile to build the marketplace UI and a web server to run it

# STAGE ONE: build the marketplace angular application
FROM node:latest as build
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
ARG selene_env
ARG application_name
RUN npm run build -- --project=globalnav
RUN npm run build-${selene_env} -- --project=${application_name}

# STAGE TWO: build the web server and copy the compiled angular app to it.
FROM nginx:latest
COPY --from=build /usr/src/app/dist/${application_name} /usr/share/nginx/html
