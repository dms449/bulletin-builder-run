# Bulletin Builder
Receives http get/post requests with json data and returns (if possible) a pdf.

## Run Locally

```
docker build -t bulletin_builder .                                                                            develop [!]
PORT=8080 && docker run -p 9090:${PORT} -e PORT=${PORT} bulletin_builder
```

## Deploy to Google Cloud Run
```
gcloud run deploy bulletin-builder --source=. --region=us.central1 --no-allow-unauthenticated
```
