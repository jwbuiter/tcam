import base64
import json

from flask import Flask

import tcam


def run(config):
    app = Flask(__name__)

    @app.route("/data")
    def frame_data():
        frame = tcam.update()
        return json.dumps([str(frame.dtype), base64.b64encode(frame).decode('ascii'), frame.shape])

    app.run("0.0.0.0")
