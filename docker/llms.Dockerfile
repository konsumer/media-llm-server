# this is an extension of llms.py docker that installs the deps needed to actually run it's extensions and stuff

FROM ghcr.io/servicestack/llms:latest

# Switch to root to install packages
USER root

# Install git and other system dependencies
RUN apt-get update && \
  apt-get install -y git curl npm && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install Python dependencies for extensions
RUN pip install --no-cache-dir ddgs fastmcp google-genai

RUN npm install n -g && n latest && chown -R llms /home/llms/.npm

# setup aitorrent
ADD https://github.com/konsumer/aitorrent/archive/refs/heads/main.tar.gz /tmp/aitorrent.tgz
RUN cd /opt && tar xvzf /tmp/aitorrent.tgz && mv aitorrent-main aitorrent && cd aitorrent && pip install --no-cache-dir -r requirements.txt && rm -rf /tmp/aitorrent.tgz

USER llms
