#import
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# References the file
app = Flask(__name__)
columns = []

def initialize_columns():
    with open('columns.txt') as f:
        lines = f.readlines()
    return lines

def machine_learning():
    return "Hello World!"

def make_list(data):
    X = []
    for x in data.values():
        X.append(x)
    return X

def check_data(data):
    valid = True
    if len(data) == len(columns):
        for x in data.values():
            if (x != 1) and (x != 0):
                valid = False
                break
    else:
        valid = False
    return valid

@app.route('/predict', methods = ['POST'])
def predict():
    data = request.get_json()
    data_local = json.loads(data)
    if check_data(data_local):
        X = make_list(data_local)
    else:
        return jsonify({'error': 'Error in Data'}), 400


if __name__ == "__main__":
    columns = initialize_columns()
    app.run(debug=True)