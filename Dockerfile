FROM python:3.11-slim

LABEL maintainer="Ahmed Hassan <developer@a2zsoc.com>"
LABEL description="Project ChronoArbitrage: Autonomous Narrative Intelligence & Liquidity Arbitrage Swarm"

WORKDIR /app

COPY pyproject.toml README.md ./
COPY chrono_arbitrage ./chrono_arbitrage
RUN pip install --no-cache-dir .

EXPOSE 8080

ENTRYPOINT ["chrono-arbitrage"]
CMD ["all"]
