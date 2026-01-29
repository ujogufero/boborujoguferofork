# Sauna Bobor Status

A simple web application to monitor [Danube river measurements](https://www.shmu.sk/sk/?page=765&station_id=5140) and [Sauna Bobor](https://saunabobor.sk) capacity.

- **Backend**: Python (Flask) with scheduled tasks using [Huey](https://github.com/coleifer/huey) to scrape external sources.
- **Frontend**: Vue.js (Vite).

## Development

### Python

```bash
poetry install
poetry run flask --app app run
```

### Node

```bash
cd frontend
npm install
npm run dev
npm run build
```

## Deployment

I am using [fly.io](https://fly.io) as its simplicity fits the purpose of this application.

> [!NOTE]
Make sure only one replica is running since the data is stored in-memory.
