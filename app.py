from loguru import logger

from typing import cast

from flask import Flask, jsonify
from flask.wrappers import Response as FlaskResponse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from prometheus_client import generate_latest

from prom.metrics import (
    metric_water_temp,
    metric_water_level,
    metric_bobor_capacity,
    metric_sauna_temp,
    metric_sauna_door,
    metric_shmu_last_updated,
    metric_bobor_last_updated,
    metric_sauna_last_updated,
)

from parsers.bobor import parse_bobor
from parsers.shmu import parse_shmu
from sauna.status import get_sauna_status
from utils.scheduler import Scheduler

# Global in-memory storage
data_store: dict[str, str | int | float | None] = {}


class Config:
    pass


app = Flask(__name__, static_folder="frontend/dist", static_url_path="/")
app.config.from_object(Config())

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",
)


def update_shmu_status() -> None:
    result = parse_shmu()
    if result:
        data_store.update(result)

        if result.get("water_temp_c") is not None:
            metric_water_temp.set(float(cast(float, result["water_temp_c"])))
        if result.get("water_level_cm") is not None:
            metric_water_level.set(float(cast(float, result["water_level_cm"])))
        metric_shmu_last_updated.set_to_current_time()


def update_bobor_status() -> None:
    result = parse_bobor()
    if result:
        data_store["bobor_capacity"] = result

        if result == "closed":
            metric_bobor_capacity.set(0)
        else:
            try:
                current_people = int(result.split(" z ")[0])
                metric_bobor_capacity.set(current_people)
            except (ValueError, IndexError):
                logger.warning(f"Could not parse bobor capacity from string: {result}")

        metric_bobor_last_updated.set_to_current_time()


def update_sauna_status():
    result = get_sauna_status()
    if result:
        data_store["sauna_temperature"] = result.temperature
        data_store["sauna_door_closed"] = result.door_closed

        metric_sauna_temp.set(result.temperature)
        metric_sauna_door.set(1 if result.door_closed else 0)
        metric_sauna_last_updated.set_to_current_time()


# Initialize and start scheduler
scheduler = Scheduler()
scheduler.add_task(600, update_shmu_status)
scheduler.add_task(300, update_bobor_status)
scheduler.add_task(300, update_sauna_status)
scheduler.start()


# Perform initial data load
initial_shmu = parse_shmu()
if initial_shmu:
    data_store.update(initial_shmu)
    if initial_shmu.get("water_temp_c") is not None:
        metric_water_temp.set(float(cast(float, initial_shmu["water_temp_c"])))
    if initial_shmu.get("water_level_cm") is not None:
        metric_water_level.set(float(cast(float, initial_shmu["water_level_cm"])))
    metric_shmu_last_updated.set_to_current_time()

initial_bobor = parse_bobor()
if initial_bobor:
    data_store["bobor_capacity"] = initial_bobor
    if initial_bobor == "closed":
        metric_bobor_capacity.set(0)
    else:
        try:
            current_people = int(initial_bobor.split(" z ")[0])
            metric_bobor_capacity.set(current_people)
        except (ValueError, IndexError):
            logger.warning(
                f"Could not parse bobor capacity from string: {initial_bobor}"
            )
    metric_bobor_last_updated.set_to_current_time()

initial_sauna = get_sauna_status()
if initial_sauna:
    data_store["sauna_temperature"] = initial_sauna.temperature
    data_store["sauna_door_closed"] = initial_sauna.door_closed
    metric_sauna_temp.set(initial_sauna.temperature)
    metric_sauna_door.set(1 if initial_sauna.door_closed else 0)
    metric_sauna_last_updated.set_to_current_time()


@app.route("/api")
@limiter.limit("100 per minute")
def get_bobor_status() -> FlaskResponse | tuple[FlaskResponse, int]:
    return jsonify(data_store)


@app.route("/metrics")
@limiter.limit("100 per minute")
def metric_export():
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/")
def frontend():
    return app.send_static_file("index.html")
