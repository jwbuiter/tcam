import base64
import json

import numpy as np
from flask import Flask

import tcam


def run(config):
    app = Flask(__name__)

    @app.route("/data")
    def frame_data():
        return str(tcam.get_weighted_percentage())

    app.run("0.0.0.0")
