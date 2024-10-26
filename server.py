from flask import Flask, jsonify
from data_analysis import getDatInsights
import json
import numpy as np

app = Flask(__name__)

# Custom JSON encoder for handling NumPy data types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Define a GET route
@app.route('/get-data', methods=['GET'])
def get_data():
    # Assuming getDatInsights() returns data with NumPy data types
    data = getDatInsights()

    # Convert to JSON string using NumpyEncoder
    json_data = json.dumps(data, cls=NumpyEncoder)

    return json_data

if __name__ == '__main__':
    app.run(debug=True, port=7100)  # Specify the port here
