import flask
from flask import request, jsonify
from flask_cors import CORS
import heapq
import queue
import simsearch
from status_codes import StatusCodes as status_codes

app = CORS(flask.Flask(__name__))

Payload = collections.namedtuple("Payload", ['stamp', 'payload'])

inputq = queue.Queue()
outputq = queue.Queue()

simobj = simsearch.SimSearch(
    "databases/vectordb",
    "databases/clusterdb",
    "en_core_web_sm")

second_thread = threading.Thread(target=launch_workers)
second_thread.start()

@ray.remote
def worker(payload):
  url = simobj.query(payload.payload)
  return Payload(payload.stamp, url)

def launch_workers():
  while True:
    task = inputq.get()
    outputq.put(worker.remote(task))

@app.route("/egress", methods=['POST']
def get_result():
  try:
    payload = ray.get(output.get(timeout=2))
    return jsonify({"idx": payload.stamp, "urls": payload.payload})
  except queue.Full:
    return jsonify({"status": status_codes.NO_ITEM_IN_QUEUE})
  except ray.exceptions.GetTimeoutError:
    return jsonify({"status": status_codes.PROCESSING_NOT_COMPLETED})
  except Exception as e:
    return jsonify({"status": status_codes.OTHER, "message": str(e)})


@app.route("/ingress", methods=['POST'])
def ingress():
  try:
    stamp = request.args.get("ts")
    text = request.args.get("text")
    inputq.put(Payload(stamp, text))
  except Exception as e:
    return jsonify({"status": status_codes.OTHER, "message": str(e)})
  return jsonify({"status": status_codes.QUEUED})
