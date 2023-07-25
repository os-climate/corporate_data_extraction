import logging
from flask import Flask, request
import numpy as np

INPUT_ARRAY = [[5.1, 3.5, 1.4, 0.2]]
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route('/')
def hello_world():
    preds = np.exp(INPUT_ARRAY)
    app.logger.info(" Inputs: "+ str(INPUT_ARRAY))
    app.logger.info(" Prediction: "+ str(preds))
    return str(preds)


@app.route('/predict', methods=['GET'])
def predict():
    """Return A Prediction."""
    app.logger.info(str(request.args))
    data = request.args["data"]
    app.logger.info("Record To predict: {}".format(data))
    app.logger.info(type(data))
    input_data = [float(data)]
    app.logger.info(input_data)
    prediction = np.exp(input_data)
    app.logger.info(prediction)
    response_data = prediction
    return {"prediction": str(response_data)}
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666, debug=True)

