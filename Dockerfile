# Use an official Node.js image as the base image
FROM node:bookworm

RUN apt-get update && \
    apt-get install -y \
    curl \
    ca-certificates \
    build-essential \
    git 

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY . .

RUN uv sync
RUN cd src/anagrams/ui; npm install; npm run build

EXPOSE 8000

# Run the app using just
CMD ["uv", "run", "anagrams"]
