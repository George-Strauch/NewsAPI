#!/usr/bin/env bash
# Usage:
#   ./build_and_start.bash
#
# Assumptions:
# - /opt/news/News is a valid git repo with working credentials on the host
# - ./env (in the current dir) exists and should become /opt/news/.env on the host
# - Dockerfile is in the current directory
# - Container does not already exist with the same name

set -euo pipefail

IMAGE_NAME="news-api-image"
CONTAINER_NAME="news-api"
BUILD_CONTEXT="."
HOST_OPT_NEWS="/opt/news"
CONTAINER_OPT_NEWS="/opt/news"

# Set to "true" for background mode (default), "false" to attach and view logs.
DETACHED=false


HOST_PORT=""
CONTAINER_PORT=""

# remove all previous artifacts
if [ -d "News" ]; then
  rm -rf "News"
fi
# remove all previous artifacts
if [ -d "NewsFE" ]; then
  rm -rf "News"
fi

if [ -f ".env" ]; then
    rm ".env"
fi

if [ -f "requirements.txt" ]; then
    rm "requirements.txt"
fi

find "." -type d -name "__pycache__" -exec rm -rf {} +
find "." -type f -name "*.log*" -delete

# NEW: remove old container and image if present
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
docker rmi -f "${IMAGE_NAME}" 2>/dev/null || true

# Update host News repo
echo "pulling most recent news collector"
git pull --rebase --autostash

echo "pulling most recent news collector"
git -C "${HOST_OPT_NEWS}/News" pull --rebase --autostash

echo "pulling most recent news front end"
git -C "${HOST_OPT_NEWS}/NewsFE" pull --rebase --autostash

# 2) copy stuff
cp "${HOST_OPT_NEWS}/.env" .
cp -r "${HOST_OPT_NEWS}/News" .
cp -r "${HOST_OPT_NEWS}/NewsFE" .

cp "News/requirements.txt" .

# Build image
DOCKER_BUILDKIT=1 docker build -t "${IMAGE_NAME}" "${BUILD_CONTEXT}"

# Run container
# Determine run mode
if [ "${DETACHED}" = true ]; then
    echo "Running container in detached mode..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -v /opt/news:/opt/news \
        "${IMAGE_NAME}"
else
    echo "Running container in attached mode..."
    echo "(Ctrl+C will stop the container)"
    docker run \
        --name "${CONTAINER_NAME}" \
        -v /opt/news:/opt/news \
        "${IMAGE_NAME}"
fi