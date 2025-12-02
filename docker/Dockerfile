FROM python:3.14-slim

# Environment variables for Poetry
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV NODE_VERSION=25

# 1. Install system dependencies and build tools
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        curl \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        gnupg \
        ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js and npm from NodeSource (separate layer for better caching)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    # Verify Node.js and npm installation
    node --version && \
    npm --version

# 3. Install Poetry (separate layer)
RUN curl -sSL https://install.python-poetry.org | python3 -

# 4. Install global npm packages if needed (optional, separate layer)
 RUN npm install -g \
     javascript-obfuscator \
     npm cache clean --force

WORKDIR /app

# Copy dependency files first (for better caching)
COPY ./pyproject.toml ./poetry.lock ./

# Install Python dependencies
RUN poetry install --no-interaction --no-root

# Copy the rest of the application
COPY ../ .

# Install the project itself
RUN poetry install --no-interaction

# Verify all installations
RUN python --version && \
    node --version && \
    npm --version