FROM python:3.14-slim

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

# Install ffmpeg, ffprobe and build tools
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        curl \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-interaction --no-root

COPY ../ .

RUN poetry install --no-interaction
