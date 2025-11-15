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

# Set to "true" for background mode (default), "false" to attach and view logs.
DETACHED=false

git pull --rebase --autostash


# remove all previous artifacts
if [ -d "News" ]; then
  rm -rf "News"
fi

if [ -d "NewsFE" ]; then
  rm -rf "NewsFE"
fi

if [ -f ".env" ]; then
    rm ".env"
fi

if [ -f "requirements.txt" ]; then
    rm "requirements.txt"
fi

find "." -type d -name "__pycache__" -exec rm -rf {} +
find "." -type f -name "*.log*" -delete

# remove old container and image if present
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
docker rmi -f "${IMAGE_NAME}" 2>/dev/null || true

cp "${HOST_OPT_NEWS}/.env" .

git clone git@github.com:George-Strauch/NewsFE.git
git clone git@github.com:George-Strauch/News.git

cp "News/requirements.txt" .

echo "building the front end"
cd NewsFE
npm install
npm run build
cd ..

# Build image
DOCKER_BUILDKIT=1 docker build -t "${IMAGE_NAME}" "${BUILD_CONTEXT}"

# Run container
# Determine run mode
if [ "${DETACHED}" = true ]; then
    echo "Running container in detached mode..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -v /opt/news_api:/opt/news_api \
        "${IMAGE_NAME}"
else
    echo "Running container in attached mode..."
    echo "(Ctrl+C will stop the container)"
    docker run \
        --name "${CONTAINER_NAME}" \
        -v /opt/news_api:/opt/news_api \
        "${IMAGE_NAME}"
fi