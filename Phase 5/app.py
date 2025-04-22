#import
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
import pandas as pd
import threading
import os



class Layer:

    ### activations
    def _identity(self,z):
        return z

    def _identity_diff(self,z):
        return np.ones_like(z)

    def _sigmoid(self,z):
        return (1/(1+np.exp(-1*z)))

    def _diff_sigmoid(self,z):
        return self._sigmoid(z)*(1-self._sigmoid(z))

    ###########

    def __init__(self,n_input,n_output, activation="identity",name=None):
        self.n_output= n_output
        self.n_input= n_input
        self.name= name

        if activation == "identity":
            self.activation = self._identity
            self.diff_act= self._identity_diff

        elif activation == "sigmoid":
            self.activation = self._sigmoid
            self.diff_act= self._diff_sigmoid





        self.W= np.random.randn(self.n_output,self.n_input)*np.sqrt(2/self.n_input)
        self.b= np.random.randn(self.n_output,1)*np.sqrt(2/self.n_input)

        self.dW= np.zeros_like(self.W)
        self.db= np.zeros_like(self.b)

        self.Z= None
        self.Ai = None


    def forward(self,Ai):
#         print("FWD")
#         print(Ai.shape)
#         print(self.W.shape)
#         print(self.b.shape)
        z =  np.add((self.W @ Ai),self.b)
#         print(z.shape)
        A = self.activation(z)
#         print(A.shape)


        self.Z = z
        self.Ai = Ai
        return A


    def backward(self,inp):

#         print("input shape: ",end='')
#         print(inp.shape)

        act_diff = self.diff_act(self.Z)
#         print("act_diff shape: ",end='')
#         print(act_diff.shape)

        tmp = inp * act_diff
#         print("tmp shape: ",end='')
#         print(tmp.shape)

        bet = tmp @ self.Ai.T # vector of 1s
#         print("bet shape: ",end='')
#         print(bet.shape)


        e = np.ones((self.Ai.shape[1],1))
        db = tmp @ e
#         print("db shape: ",end='')
#         print(db.shape)

        self.dW = self.dW + bet
        self.db = self.db + db


        return self.W.T @ tmp


    def zeroing_delta(self):
        self.dW= np.zeros_like(self.W)
        self.db= np.zeros_like(self.b)
#########################################################################################################
class NN:

    ########
    ## losses
    def MSE(self,y,yhat):
        a=np.square(yhat-y)
        a=np.sum(a)
        b= 1/(2*y.shape[1])
        return a*b

    ## diff losses
    def _diff_MSE(self,y,yhat):
        return (yhat-y)
    

    def focal_loss(self, y, yhat, gamma=2, alpha=0.25):
        epsilon = 1e-8  # to avoid log(0)
        yhat = np.clip(yhat, epsilon, 1 - epsilon)
        
        pt = y * yhat + (1 - y) * (1 - yhat)
        loss = -alpha * (1 - pt) ** gamma * np.log(pt)
        return np.mean(loss)

    def _diff_focal_loss(self, y, yhat, gamma=2, alpha=0.25):
        epsilon = 1e-8
        yhat = np.clip(yhat, epsilon, 1 - epsilon)

        pt = y * yhat + (1 - y) * (1 - yhat)
        dpt = y * 1 + (1 - y) * (-1)

        grad = -alpha * gamma * (1 - pt) ** (gamma - 1) * np.log(pt) * dpt \
               - alpha * (1 - pt) ** gamma * dpt / pt

        return grad


    #########

    def __init__(self,lr):
        self.layers = []
        self.alpha= lr




    def forward(self,inp):
        a=inp
#         print(a.shape)
        for layer in self.layers:
            a = layer.forward(a)
#             print(a.shape)

        return a

    def backward(self,input):
        gd = input
        for layer in self.layers[::-1]:
            gd = layer.backward(gd)

    def add_layer(self,n_input,n_output, activation="identity",name=None):
        self.layers.append(Layer(n_input,n_output, activation=activation,name=name))

    def fit(self, x_train,y_train, epochs=5): #data dim is MxN .. M no of examples.. N no of dimension

        M = x_train.shape[0]


        x_train = x_train.T
        y_train = y_train.T

#         print(x_train.shape)
#         print(y_train.shape)

        for i in range(epochs):
            print("Epoche {}/{}".format(i+1,epochs))
            
            y_hat = self.forward(x_train)
            loss = self.focal_loss(y_train, y_hat)
            print(f"Loss: {loss:.4f}")

            dl_dyhat = self._diff_focal_loss(y_train, y_hat)


            self.backward(dl_dyhat)

            # update using GD
            for i in range(len(self.layers)):
                # layers[i].dW=layers[i].dW/N
                # layers[i].db=layers[i].db/N
                self.layers[i].W = self.layers[i].W - self.alpha * (self.layers[i].dW/M)
                self.layers[i].b = self.layers[i].b - self.alpha * (self.layers[i].db/M)


            # zeroing deltas
            for layer in self.layers:
                layer.zeroing_delta()

        print("Finished....")





    def predict(self,x_test): #data dim is NxD .. N no of examples.. D no of dimension
#         print(x_test.shape)
        y_hat= self.forward(x_test.T)
        print(y_hat.shape)
        return y_hat.T




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
model = NN()
prediction_count = 0
lock = threading.Lock()
model_lock = threading.Lock()
new_data_file = 'new_data.csv'
new_data = []


@app.route('/predict', methods=['POST'])
def predict():
    global prediction_count, model, new_data
    data = request.get_json()
    data_local = json.loads(data)

    if not check_data(data_local):
        return jsonify({'error': 'Error in Data'}), 400

    x = make_list(data_local)
    prediction = model.predict(x)

    result = "Diabetic or Prediabetic" if prediction == 1.0 else "Not Diabetic"

    # Add new sample for retraining
    with lock:
        new_sample = [1.0 if prediction == "Diabetic or Prediabetic" else 0.0] + x
        new_data.append(new_sample)

        # Save to disk
        pd.DataFrame(new_data, columns=list(X.columns) + ['Diabetes_binary']).to_csv(new_data_file, index=False)

        prediction_count += 1

        if prediction_count >= 10:
            prediction_count = 0
            # Retrain the model using original + new data
            with model_lock:
                df = pd.read_csv('Phase 2 data.csv')
                y = df['Diabetes_binary']
                X = df.drop(['Diabetes_binary'], axis=1)

                # Create DataFrame from new_data
                new_df = pd.DataFrame(new_data, columns=list(X.columns) + ['Diabetes_binary'])

                # Combine original and new data
                combined_df = pd.concat([df, new_df], ignore_index=True)
                y_new = combined_df['Diabetes_binary']
                X_new = combined_df.drop(['Diabetes_binary'], axis=1)

                model = NN().fit(X_new, y_new)

    return jsonify({'prediction': result}), 200





if __name__ == "__main__":
    df = pd.read_csv('Phase 2 data.csv')
    y = df['Diabetes_binary']
    X = df.drop(['Diabetes_binary'],axis=1)
    model.fit(X,y)
    columns = initialize_columns()

    # Load persisted new data
    if os.path.exists(new_data_file):
        new_df = pd.read_csv(new_data_file)
        new_data = new_df.values.tolist()

    app.run(debug=True)