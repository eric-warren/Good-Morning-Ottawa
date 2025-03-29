# Use Ubuntu 18.04 as base image
FROM ubuntu:18.04

# Set non-interactive mode to avoid tzdata issues
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && apt install -y \
    software-properties-common build-essential curl \
    libffi-dev libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev \
    liblzma-dev git python3-venv && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src

# Download and compile Python 3.10
RUN wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && \
    tar -xvf Python-3.10.13.tgz && \
    cd Python-3.10.13 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf Python-3.10.13.tgz Python-3.10.13

# Explicitly link Python binaries
RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/local/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3 && \
    ln -sf /usr/local/bin/pip3.10 /usr/bin/pip

# Verify installation
RUN python3 --version && python --version

# Install dependencies
RUN pip install --no-cache-dir pymongo atproto flask python-dotenv

# Set environment variables (use ARG for build-time secrets, ENV for runtime)
ARG BLSKY_USERNAME
ARG BLSKY_PASSWORD
ARG MONGO_URI

ENV BLSKY_USERNAME=${BLSKY_USERNAME}
ENV BLSKY_PASSWORD=${BLSKY_PASSWORD}
ENV MONGO_URI=${MONGO_URI}

# Copy application files
WORKDIR /root
COPY . .

# Expose port 80
EXPOSE 80

# Start the application
CMD ["python3", "app.py"]