# Deployment

## GitHub Pages

The repository publishes its documentation from the `docs/` folder through MkDocs.

The deployment workflow is defined in `.github/workflows/deploy-docs.yml` and runs on pushes to `main`.

Build steps:

1. Install documentation dependencies from `requirements-docs.txt`.
2. Run `mkdocs build`.
3. Upload the generated `site/` directory.
4. Deploy the artifact with the official GitHub Pages actions.

The expected published URL is:

- `https://ghspain.github.io/sorteo/`

## Local Documentation Preview

Use either of these commands:

```bash
mkdocs serve
```

or:

```bash
docker-compose --profile docs up docs
```

## Application Runtime

The raffle application itself remains a Streamlit app and is independent from the documentation site.

For local app execution:

```bash
streamlit run app.py
```
