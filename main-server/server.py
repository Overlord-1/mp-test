from flask import Flask, request, jsonify
import time
import numpy as np
import math

app = Flask(__name__)


@app.route('/light', methods=['POST'])
def work_light():
    data = request.json or {}
    intensity = data.get('intensity', 1)
    start = time.time()
    _ = np.dot(np.random.rand(100 * intensity, 100 * intensity), np.random.rand(100 * intensity, 100 * intensity))
    time_taken = time.time() - start
    return jsonify({"time_taken": time_taken, "message": f"Light work done with intensity {intensity}"})

@app.route('/heavy', methods=['POST'])
def work_heavy():
    data = request.json or {}
    intensity = data.get('intensity', 1)
    start = time.time()
    for _ in range(intensity):
        _ = math.factorial(10000 + intensity * 100)
    time.sleep(intensity * 0.5)
    time_taken = time.time() - start
    return jsonify({"time_taken": time_taken, "message": f"Heavy work done with intensity {intensity}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)