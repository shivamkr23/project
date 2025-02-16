FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y
RUN apt install -y curl wget git build-essential python3 python3-pip python3-venv nodejs npm jq

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN npm install -g prettier@3.4.2 -y

WORKDIR /app

COPY . .

EXPOSE 8000

RUN uv sync --frozen

CMD ["uv", "run", "hello.py"]
