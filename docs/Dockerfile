FROM python:3.10-slim

WORKDIR /app

COPY requirements-docs.txt ./
RUN pip install --no-cache-dir -r requirements-docs.txt

COPY mkdocs.yml ./
COPY docs ./docs

EXPOSE 8000

CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"]
