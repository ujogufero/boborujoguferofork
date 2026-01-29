from threading import Thread
from loguru import logger

from flask import Flask, jsonify
from flask.wrappers import Response as FlaskResponse

from huey import MemoryHuey, crontab

from parsers.bobor import parse_bobor
from parsers.shmu import parse_shmu

# Global in-memory storage
data_store: dict[str, str | int | float | None] = {}


class Config:
    pass


app = Flask(__name__, static_folder="frontend/dist", static_url_path="/")
app.config.from_object(Config())

huey = MemoryHuey(immediate=False)

@huey.periodic_task(crontab(minute="*/15"))
def scheduled_shmu_task() -> None:
    logger.info("Updating Dunaj values")
    result = parse_shmu()
    if result:
        data_store.update(result)


@huey.periodic_task(crontab(minute="*/5"))
def scheduled_bobor_task() -> None:
    logger.info("Updating Bobor capacity")
    result = parse_bobor()
    if result:
        data_store["bobor_capacity"] = result


def start_huey_consumer() -> None:
    """Starts the Huey consumer in a separate thread."""
    consumer = huey.create_consumer()
    # Disable signal handling since we are not in the main thread
    consumer._set_signal_handlers = lambda: None
    thread = Thread(target=consumer.run, daemon=True)
    thread.start()


# Perform initial data load
logger.info("Performing initial data load")
initial_shmu = parse_shmu()
if initial_shmu:
    data_store.update(initial_shmu)

initial_bobor = parse_bobor()
if initial_bobor:
    data_store["bobor_capacity"] = initial_bobor

# Start the consumer thread
# We start this immediately when the module is loaded, assuming single worker
start_huey_consumer()


@app.route("/api")
def get_sauna_status() -> FlaskResponse | tuple[FlaskResponse, int]:
    return jsonify(data_store)


@app.route("/")
def vue_frontend():
    return app.send_static_file("index.html")
