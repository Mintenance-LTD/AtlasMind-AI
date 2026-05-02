FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .
COPY core ./core
COPY agents ./agents
EXPOSE 8080
CMD ["uvicorn", "agents.country_risk.app:app", "--host", "0.0.0.0", "--port", "8080"]
