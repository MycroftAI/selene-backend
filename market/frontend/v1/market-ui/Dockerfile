# Multistage Dockerfile to build the marketplace UI and a web server to run it

# STAGE ONE: build the marketplace angular application
FROM node:latest as build
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# STAGE TWO: build the web server and copy the compiled angular app to it.
FROM nginx:latest
COPY --from=build /usr/src/app/dist/mycroft-marketplace /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
