FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        default-jdk-headless \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 runner
USER runner

WORKDIR /work
