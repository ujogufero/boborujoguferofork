
# bobor_status
Flask application that monitors [Danube](https://www.shmu.sk/sk/?page=765&station_id=5140) measurements and [Sauna Bobor](https://saunabobor.sk) metrics and provides endpoints for further processing.

Strasne uzasni fork
bolo pouzite ai na poznamky aby ostatny lepsie porozumely inac vsetko robene mnou

```bash
make install # runs `poetry install`
make dev     # starts development server
```

### frontend

```bash
npm install   # installs dependencies
npm run build # builds the frontend
npm run dev   # starts development server
```

### local
```bash
make install # copies configs to ~/.config/bobor and generates systemd service
make start   # starts VictoriaMetrics container and Flask development server
make browse  # opens `vmui` in a web browser 
make nuke    # exactly what it says, so be mindful of that
```
