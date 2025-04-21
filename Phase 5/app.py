#import
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
import pandas as pd

class NB:

    def __init__(self):
        self.Px_y= dict()
        self.Py= dict()
        self.cols= None


    def fit(self,X,y):

        # first calculate the probability of y equal each value
        # get the y categoried
        labels,counts = np.unique(y,return_counts=True)

        m = len(y)
        for i in range(len(labels)):
            self.Py[labels[i]]= counts[i]/m

        # calculate the probability of each feature value
        self.cols = X.columns
        for col in X.columns: # loop each column
            self.Px_y[col] = dict()

            feature = X[col]
            values = np.unique(feature)
            for value in values:
                self.Px_y[col][value]=dict()
                for j in range(len(labels)):
                    self.Px_y[col][value][labels[j]] = len(X[ X[col] == value][y == labels[j]])/counts[j]



        return self



    def predict(self,x_test):

        # get P(Y | X_test)
        out = []
        for label,prob in self.Py.items(): # loop over each category proba
            p=prob
            for i in range(len(x_test)): # loop over each feature in x_test
                col = self.cols[i]
                p=p * self.Px_y[col][x_test[i]][label]
            out.append((p,label))

        # sort probas
        sor = sorted(out , key= lambda x: x[0], reverse= True)


        return sor[0][1]

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

# References the file
app = Flask(__name__)
columns = []
model = NB()

@app.route('/predict', methods = ['POST'])
def predict():
    data = request.get_json()
    data_local = json.loads(data)
    if check_data(data_local):
        x = make_list(data_local)
        prediction = "Not Diabetic"
        if model.predict(x) == 1.0:
            prediction = "Diabetic or Prediabetic"

        return jsonify({'prediction': prediction}),200
    else:
        return jsonify({'error': 'Error in Data'}), 400




if __name__ == "__main__":
    df = pd.read_csv('Phase 2 data.csv')
    y = df['Diabetes_binary']
    X = df.drop(['Diabetes_binary'],axis=1)
    model.fit(X,y)
    columns = initialize_columns()
    app.run(debug=True)