FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY hexagon/ hexagon/
COPY driven_adapters/ driven_adapters/
COPY driving_adapters/ driving_adapters/
COPY configuration/ configuration/
COPY hexagon_tests/ hexagon_tests/

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["pytest", "--tb=short"]
