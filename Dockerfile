FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install uv
RUN uv pip install --system -e .

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]