FROM gcr.io/buildpacks/builder
USER root
RUN apt-get update && apt-get install -y -q --no-install-recommends npm \
build-essential curl cargo
RUN npm install -g sass
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
USER cnb
