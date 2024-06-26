# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.10.9
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ENV DAPR_API_TOKEN=diagrid://v1/a657cb15-9aa6-4bfd-b3c6-61e76a173cfb/139416/kv-project-fbe8f200-4/user-service/c4f7e75e-b149-4ffd-852b-7ee716924d3e
ENV DAPR_APP_ID=user-service
ENV DAPR_CLIENT_TIMEOUT_SECONDS=10
ENV DAPR_USER_DB=usersdb
ENV DAPR_PUB_SUB=awssqs
ENV DAPR_DELIVER_AGENT_ACCOUNT_CREATED_TOPIC_NAME=delivery-agent-account-created
ENV DAPR_GRPC_ENDPOINT=https://grpc-prj139416.api.cloud.diagrid.io:443
ENV DAPR_HTTP_ENDPOINT=https://http-prj139416.api.cloud.diagrid.io

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 5001

# Run the application.
CMD uvicorn 'main:app' --host=0.0.0.0 --port=5001
