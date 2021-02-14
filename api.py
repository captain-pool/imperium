import flask
from flask import request, jsonify
from flask_cors import CORS
import collections
import queue
import simsearch
from status_codes import StatusCodes as status_codes
import threading
import ray
import addict
import database


ray.init()

app = flask.Flask(__name__)
CORS(app)

Payload = collections.namedtuple('Payload', ['stamp', 'payload'])

inputq = queue.Queue()
outputq = queue.Queue()

previous = None
vectorizer = database.Vectorize("en_core_web_sm")
simobj = simsearch.SimSearch(
    "databases/vectordb",
    "databases/clusterdb",
    vectorizer)

@ray.remote
def worker(timestamp, payload):
  url = simobj.query(payload)
  return timestamp, url

def launch_workers():
  while True:
    task = inputq.get()
    objid = worker.remote(task.stamp, task.payload)
    outputq.put(objid)


second_thread = threading.Thread(target=launch_workers)
second_thread.start()

@app.route("/egress", methods=['GET'])
def get_result():
  try:
    payload = Payload(*ray.get(outputq.get(timeout=2)))
    return jsonify({"idx": payload.stamp, "urls": payload.payload})
  except queue.Empty:
    return jsonify({"status": status_codes.NO_ITEM_IN_QUEUE})
  except ray.exceptions.GetTimeoutError:
    return jsonify({"status": status_codes.PROCESSING_NOT_COMPLETED})
  except Exception as e:
    return jsonify({"status": status_codes.OTHER, "message": str(e)})


@app.route("/ingress", methods=['POST'])
def ingress():
  global previous
  try:
    stamp = request.json["ts"]
    text = request.json["text"]
    if text != previous:
      inputq.put(Payload(stamp, text))
      previous = text
  except Exception as e:
    return jsonify({"status": status_codes.OTHER, "message": str(e)})
  return jsonify({"status": status_codes.QUEUED})


app.run("0.0.0.0", 5000)
