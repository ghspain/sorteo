# Testing

## Fast Verification

Use the fast verification pass for local changes:

```bash
python -m pytest tests/unit tests/integration -q
```

## End-to-End Verification

Start the app first:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

Then run the browser checks:

```bash
STREAMLIT_HOST=127.0.0.1 STREAMLIT_PORT=8501 python -m pytest tests/e2e/test_csv_upload.py tests/e2e/test_raffle_process.py -q
```

## Documentation Build Check

Validate the GitHub Pages output locally with:

```bash
mkdocs build
```
