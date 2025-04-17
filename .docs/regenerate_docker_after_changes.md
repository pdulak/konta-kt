
# Rebuilding Docker Container After Updating requirements.txt

When you've made changes to your `requirements.txt` file, you need to rebuild your Docker container to install the new dependencies. Here's how to do it:

## Option 1: Rebuild and restart with docker-compose

```bash
# Stop the current container
docker compose down

# Rebuild the image with the updated requirements.txt
docker compose build

# Start the container again
docker compose up
```

Or you can combine the build and up steps:

```bash
docker compose down
docker compose up --build
```

## Option 2: Force rebuild without cache

If you're having issues with the dependencies not updating correctly, you can force a rebuild without using the cache:

```bash
docker compose build --no-cache
docker compose up
```

## Why this works

Looking at your Dockerfile:
```dockerfile
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
```

The `requirements.txt` file is copied into the container and dependencies are installed during the build process. Simply restarting the container won't install new dependencies - you need to rebuild the image to trigger the `RUN pip install -r requirements.txt` instruction.

Your docker-compose.yml mounts the current directory as a volume, but this happens after the build process, so changes to requirements.txt won't automatically be reflected without rebuilding.