# Bulletin Builder
Receives http get/post requests with json data and returns (if possible) a pdf.

## Test Locally

#### Start the bulletin builder function
```
docker build -t bulletin_builder .
PORT=8080 && docker run -p 9090:${PORT} -e PORT=${PORT} bulletin_builder
```

#### Run test script
**NOTE** The python environment must have the `requests` library.
```
python3 test/send_http.py
```

## Deploy to Google Cloud Run
```
gcloud run deploy bulletin-builder --source=. --region=us.central1 --no-allow-unauthenticated
```
