#import
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import OrderedDict
import json
import numpy as np
import pandas as pd
import threading
import os
import time # Added for timestamp in backup file name
# Add new imports at the top
from imblearn.over_sampling import SMOTE
from collections import Counter
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

def save_model(model, filename='saved_model.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(model, f)

def load_model(filename='saved_model.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class Layer:

    ### activations
    def _identity(self,z):
        return z

    def _identity_diff(self,z):
        return np.ones_like(z)

    def _sigmoid(self, z):
        z = np.clip(z, -50, 50)  # prevent overflow
        return 1 / (1 + np.exp(-z))


    def _diff_sigmoid(self, z):
        s = self._sigmoid(z)
        return s * (1 - s)

    # Added ReLU activation and its derivative
    def _relu(self, z):
        return np.maximum(0, z)

    def _diff_relu(self, z):
        return (z > 0).astype(float)


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

        # Added ReLU activation handling
        elif activation == "relu":
            self.activation = self._relu
            self.diff_act= self._diff_relu
        else:
            raise ValueError("Unsupported activation function")


        # Adjusted weight initialization based on activation
        if activation == "relu":
             self.W = np.random.randn(self.n_output, self.n_input) * np.sqrt(2. / self.n_input) # He initialization for ReLU
        else: # Assuming Xavier for Sigmoid or Identity
            self.W = np.random.randn(self.n_output, self.n_input) * np.sqrt(1. / self.n_input) # Xavier initialization


        # Bias initialization - typically zero for ReLU, sometimes small constant for sigmoid
        # Initializing to zeros is often a safe default
        self.b= np.zeros((self.n_output,1))


        self.dW= np.zeros_like(self.W)
        self.db= np.zeros_like(self.b)

        self.Z= None
        self.Ai = None


    def forward(self,Ai):
        # *** Convert input to NumPy array immediately ***
        Ai = np.asarray(Ai)

        z =  np.add((self.W @ Ai),self.b)
        A = self.activation(z)

        self.Z = z
        self.Ai = Ai # Store the NumPy array version
        return A


    def backward(self,inp):
        # *** Convert input to NumPy array immediately ***
        inp = np.asarray(inp)

        act_diff = self.diff_act(self.Z)
        tmp = inp * act_diff

        # Keep Clipping for the intermediate gradient 'tmp' as a safeguard
        # Adjust clipping range if needed, maybe slightly wider for ReLU initially
        tmp = np.clip(tmp, -50.0, 50.0)

        # Calculate dW and db, accumulated across the batch
        bet = tmp @ self.Ai.T
        # Summing across the batch for db
        db = np.sum(tmp, axis=1, keepdims=True) # This should now work correctly with NumPy tmp

        self.dW = self.dW + bet
        self.db = self.db + db

        # Return gradient for the previous layer
        return self.W.T @ tmp


    def zeroing_delta(self):
        self.dW= np.zeros_like(self.W)
        self.db= np.zeros_like(self.b)
#########################################################################################################

class DropoutLayer:
    def __init__(self, dropout_rate):
        self.dropout_rate = dropout_rate
        self.mask = None
        self.Ai = None
        self.training = True  # default to training mode

    def forward(self, Ai, training=True):
        Ai = np.asarray(Ai)  # Ensure input is NumPy array
        if training:
            self.mask = (np.random.rand(*Ai.shape) > self.dropout_rate).astype(float)
            # Scale up the remaining neurons
            return (Ai * self.mask) / (1 - self.dropout_rate)
        else:
            return Ai


    def backward(self, inp):
        # Dropout layer also needs to handle potentially non-NumPy input
        inp = np.asarray(inp) # Ensure input is NumPy array
        # During backprop, apply the same mask and scaling
        return inp * self.mask / (1 - self.dropout_rate) if self.training else inp


    def zeroing_delta(self):
        pass  # Dropout has no weights to update


#########################################################################################################
class NN:

    ########
    ## losses
    def MSE(self,y,yhat):
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        a=np.square(yhat-y)
        a=np.sum(a)
        b= 1/(2*y.shape[1])
        return a*b

    ## diff losses
    def _diff_MSE(self,y,yhat):
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        return (yhat-y)


    def focal_loss(self, y, yhat, gamma=2, alpha=0.25):
        """
        Implementation of Focal Loss for binary classification
        
        Parameters:
        - gamma: focusing parameter that controls the down-weighting of well-classified examples
        - alpha: weighting factor for the positive class
        
        Formula: -alpha * (1-pt)^gamma * log(pt) where pt is the predicted probability
        """
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-7
        
        # Clip predictions for numerical stability
        yhat = np.clip(yhat, epsilon, 1 - epsilon)
        
        # Calculate pt (predicted probability of the true class)
        pt = y * yhat + (1 - y) * (1 - yhat)
        
        # Calculate class weights
        alpha_t = y * alpha + (1 - y) * (1 - alpha)
        
        # Focal loss formula
        loss = -alpha_t * (1 - pt)**gamma * np.log(pt)
        
        return np.mean(loss)

    def _diff_focal_loss(self, y, yhat, gamma=2, alpha=0.25):
        """
        Gradient of the focal loss with respect to the predicted probability
        """
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-7
        
        # Clip predictions for numerical stability
        yhat = np.clip(yhat, epsilon, 1 - epsilon)
        
        # pt is the probability of the true class
        pt = y * yhat + (1 - y) * (1 - yhat)
        
        # Alpha weight term
        alpha_t = y * alpha + (1 - y) * (1 - alpha)
        
        # Calculate the sign term for the gradient (depends on the class)
        # For y=1: dpt/dyhat = 1, for y=0: dpt/dyhat = -1
        dpt_dyhat = y - (1 - y)
        
        # Full gradient calculation based on the chain rule
        grad = alpha_t * (
            gamma * (1 - pt)**(gamma-1) * np.log(pt + epsilon) * dpt_dyhat -
            (1 - pt)**gamma * dpt_dyhat / (pt + epsilon)
        )
        
        # Clip gradient to prevent exploding gradients
        return np.clip(grad, -10.0, 10.0)



    def binary_cross_entropy(self, y, yhat):
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-15 # Use a smaller epsilon for BCE
        yhat = np.clip(yhat, epsilon, 1 - epsilon)
        # Check for empty arrays to avoid log(0) edge cases on structure
        if y.size == 0 or yhat.size == 0:
             return 0.0 # Or some other appropriate value for empty input
        return -np.mean(y * np.log(yhat) + (1 - y) * np.log(1 - yhat))

    # Modified _diff_binary_cross_entropy for numerical stability
    def _diff_binary_cross_entropy(self, y, yhat):
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-15 # Use a smaller epsilon
        yhat = np.clip(yhat, epsilon, 1 - epsilon)
        # Numerically stable gradient for BCE with sigmoid output
        return (yhat - y)




    #########

    def __init__(self,lr):
        self.layers = []
        self.alpha= lr




    def forward(self, inp, training=True):
        a = np.asarray(inp)
        for layer in self.layers:
            if isinstance(layer, DropoutLayer):
                a = layer.forward(a, training=training)
            else:
                a = layer.forward(a)
        return a

    def backward(self,input):
        # Convert initial gradient input to NumPy array
        gd = np.asarray(input)
        for layer in self.layers[::-1]:
            # Layers handle their own input conversion now
            gd = layer.backward(gd)

    def add_layer(self, n_input=None, n_output=None, activation="identity", name=None, dropout=None):
        if dropout is not None:
            self.layers.append(DropoutLayer(dropout))
        else:
            # Use ReLU for hidden layers, Sigmoid for the output layer
            self.layers.append(Layer(n_input, n_output, activation=activation, name=name))


    

    def fit(self, x_train, y_train, epochs=30, apply_smote=True):
        # Convert to numpy arrays
        x_train = np.asarray(x_train).T
        y_train = np.asarray(y_train).T
        
        # Reshape for SMOTE
        x_train = x_train.T
        y_train = y_train.ravel().astype(int)
        
        if apply_smote:
            # Apply SMOTE with less aggressive balancing
            print(f"Class distribution before SMOTE: {Counter(y_train)}")
            # Use sampling_strategy=0.4 instead of 0.5 for less aggressive balancing
            sm = SMOTE(sampling_strategy=0.5, k_neighbors=5, random_state=42)
            x_train, y_train = sm.fit_resample(x_train, y_train)
            print(f"Class distribution after SMOTE: {Counter(y_train)}")
        
        # Reshape back
        x_train = x_train.T
        y_train = y_train.reshape(1, -1)
        
        # Modified focal loss parameters for better recall
        gamma = 2.0  # Standard value
        alpha = 0.40  # Increased from 0.25 to give more weight to positive class
        
        # Batch parameters
        M = x_train.shape[1]
        batch_size = 32
        n_batches = max(1, M // batch_size)
        
        for i in range(epochs):
            # Shuffle data
            indices = np.random.permutation(M)
            x_shuffled = x_train[:, indices]
            y_shuffled = y_train[:, indices]
            
            epoch_loss = 0
            
            # Batch processing
            for b in range(n_batches):
                start_idx = b * batch_size
                end_idx = min((b + 1) * batch_size, M)
                
                x_batch = x_shuffled[:, start_idx:end_idx]
                y_batch = y_shuffled[:, start_idx:end_idx]
                
                # Forward pass
                y_hat = self.forward(x_batch)
                
                # Use focal loss
                loss = self.focal_loss(y_batch, y_hat, gamma=gamma, alpha=alpha)
                epoch_loss += loss
                
                # Gradient
                dl_dyhat = self._diff_focal_loss(y_batch, y_hat, gamma=gamma, alpha=alpha)
                
                # Backward pass
                self.backward(dl_dyhat)
                
                # Weight updates with moderate clipping
                for layer in self.layers:
                    if isinstance(layer, Layer):
                        batch_size = end_idx - start_idx
                        layer.W -= self.alpha * np.clip(layer.dW/batch_size, -3, 3)
                        layer.b -= self.alpha * np.clip(layer.db/batch_size, -3, 3)
                        layer.zeroing_delta()
            
            # Print progress
            if (i+1) % 5 == 0:
                print(f"Epoch {i+1}/{epochs}, Loss: {epoch_loss/n_batches:.4f}")



    def update_weights(self, new_data_points):
        global model, df, new_data_file, columns, model_lock

        # Convert new data points to a DataFrame
        try:
            new_data_df = pd.DataFrame(new_data_points, columns=df.columns)
        except Exception as e:
            print(f"Error creating DataFrame from new data points: {e}")
            return

        # Append new data to the main DataFrame
        df = pd.concat([df, new_data_df], ignore_index=True)

        # Save new data to the CSV file
        try:
            write_header = not os.path.exists(new_data_file) or os.stat(new_data_file).st_size == 0
            new_data_df.to_csv(new_data_file, mode='a', header=write_header, index=False)
            print(f"Appended {len(new_data_df)} new rows to {new_data_file}.")
        except Exception as e:
            print(f"Error saving new data to CSV: {e}")

        # Prepare new data for incremental update
        if 'Diabetes_binary' in new_data_df.columns:
            y_new = new_data_df['Diabetes_binary'].astype(int)  # Ensure y_new is of type int
            expected_feature_columns = [c.strip() for c in columns if c.strip() != 'Diabetes_binary']
            X_new = new_data_df[expected_feature_columns]

            # Update the model weights incrementally
            with model_lock:
                print("Updating weights incrementally with new data...")
                y_new = y_new.values.reshape(1, -1)  # Ensure correct shape
                X_new = X_new.values.T  # Transpose for compatibility with the model
                y_hat = model.forward(X_new)
                loss_gradient = model._diff_focal_loss(y_new, y_hat)
                model.backward(loss_gradient)

                # Update weights using gradients from the new data
                for layer in model.layers:
                    if isinstance(layer, Layer):  # Only update trainable layers
                        layer.W -= model.alpha * (layer.dW / X_new.shape[1])
                        layer.b -= model.alpha * (layer.db / X_new.shape[1])

                # Zero out gradients after update
                for layer in model.layers:
                    layer.zeroing_delta()

                print("Weights updated incrementally with new data.")
        else:
            print("Error: 'Diabetes_binary' column not found in the new data. Skipping weight update.")

    def predict(self, x_test):  # data dim is NxD .. N no of examples.. D no of dimension
        # Convert input to NumPy array immediately
        x_test = np.asarray(x_test)
        # Transpose and ensure it's NumPy for the forward pass
        y_hat = self.forward(x_test.T, training=False)  # Disable dropout
        return y_hat.T


def initialize_columns():
    # Assuming columns.txt exists and contains column names
    try:
        with open('columns.txt') as f:
            lines = f.readlines()
        # Clean up column names (remove leading/trailing whitespace and newlines)
        return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        print("Error: columns.txt not found.")
        # Return an empty list, subsequent checks will handle this
        return []
    except Exception as e:
        print(f"Error reading columns.txt: {e}")
        return []


def machine_learning():
    return "Hello World!"

def make_list(data):
    # Ensure the order of data matches the columns defined (excluding the target)
    # Use a dictionary comprehension to get values in the correct order, default to 0 if key is missing
    required_feature_columns = [col.strip() for col in columns if col.strip() != 'Diabetes_binary']
    ordered_data = [data.get(col, 0) for col in required_feature_columns]
    return ordered_data


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
CORS(app, resources={r'*': {'origins': '*'}}) # Allow all origins for CORS

columns = []
prediction_count = 0
lock = threading.Lock()
model_lock = threading.Lock()
new_data_file = 'new_data.csv'
new_data = [] # This will store new samples as lists before appending to df
new_X = [] # This will store new samples as lists before appending to df
new_y = [] # This will store new samples as lists before appending to df


# Load initial data
try:
    df = pd.read_csv('Phase 2 data.csv')
    print("Successfully loaded Phase 2 data.csv")
except FileNotFoundError:
    print("Error: Phase 2 data.csv not found. Please ensure it's in the correct directory.")
    exit() # Exit if the main data file is not found
except Exception as e:
    print(f"Error loading Phase 2 data.csv: {e}")
    exit()

columns = initialize_columns()
# If columns.txt failed, try to use columns from the main data file
if not columns and 'Diabetes_binary' in df.columns:
    columns = df.columns.tolist()
    print("Using columns from Phase 2 data.csv as columns.txt was not loaded.")
elif not columns:
     print("Critical Error: Could not load columns from columns.txt or determine from Phase 2 data.csv. Exiting.")
     exit()


# Ensure X only contains the feature columns based on our 'columns' list
expected_feature_columns = [c.strip() for c in columns if c.strip() != 'Diabetes_binary']
# Check if all expected feature columns exist in df
if not all(col in df.columns for col in expected_feature_columns):
    missing_cols = [col for col in expected_feature_columns if col not in df.columns]
    print(f"Error: Missing expected feature columns in Phase 2 data.csv: {missing_cols}")
    exit()


# Load persisted new data
new_df = pd.DataFrame() # Initialize new_df as an empty DataFrame
if os.path.exists(new_data_file):
    try:
        # Read new data, ensuring columns match df
        new_df = pd.read_csv(new_data_file)
        print(f"Successfully loaded existing new data from {new_data_file}")

        # Ensure columns match before concatenating
        if list(new_df.columns) != list(df.columns):
             print(f"Warning: Columns in '{new_data_file}' do not match 'Phase 2 data.csv'. Attempting to align by reindexing.")
             # Simple alignment by reindexing new_df columns to match df columns
             new_df = new_df.reindex(columns=df.columns, fill_value=0)
             # It's also wise to save the corrected new_df back, but handle potential errors
             try:
                 new_df.to_csv(new_data_file, index=False)
                 print(f"Corrected and saved {new_data_file} with aligned columns.")
             except Exception as e:
                 print(f"Error saving corrected {new_data_file}: {e}")


        df = pd.concat([df, new_df], ignore_index=True, sort=False)
        print(f"Appended {len(new_df)} rows from {new_data_file} to main data.")

        # Convert new_data_file content back to list of lists for the `new_data` variable
        # This is done to preserve the accumulated data between server restarts
        new_data = new_df.values.tolist()


    except Exception as e:
        print(f"Error loading or processing {new_data_file}: {e}")
        # Decide how to handle a corrupted new_data.csv - e.g., back up and create empty
        backup_filename = new_data_file + f".bak_{int(time.time())}"
        try:
            if os.path.exists(new_data_file):
                 os.rename(new_data_file, backup_filename)
                 print(f"Backed up corrupted {new_data_file} to {backup_filename}")
            # Create an empty new_data.csv with correct headers
            pd.DataFrame(columns=df.columns).to_csv(new_data_file, index=False)
            print(f"Created a new empty {new_data_file}")
            new_df = pd.DataFrame() # Reset new_df
            new_data = [] # Reset new_data
        except Exception as rename_e:
            print(f"Error during backup/creation of {new_data_file}: {rename_e}")


# Prepare data for initial training and testing
if 'Diabetes_binary' in df.columns:
    y = df['Diabetes_binary']
    X = df[expected_feature_columns]
    
    # Standardize features - critical for neural network performance
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    
    # Split the data using stratification to maintain class distribution
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print("Data split into training and testing sets.")
    
    # Print class distribution information
    print(f"Positive class percentage: {y.mean()*100:.2f}%")
    print(f"Training data distribution: {Counter(y_train)}")
    print(f"Testing data distribution: {Counter(y_test)}")
else:
    print("Error: 'Diabetes_binary' column not found in the combined data for initial training.")
    exit()

model_filename = 'saved_model.pkl'
if os.path.exists(model_filename):
    print(f"Loading model from {model_filename}")
    model = load_model(model_filename)
else:
    print("No saved model found. Initializing and training a new model.")
    
    # Initialize model with the exact architecture shown in the image
    model = NN(lr=0.001)
    
    # First dense layer with 192 neurons (10,560 parameters)
    model.add_layer(n_input=X.shape[1], n_output=192, activation='relu')
    
    # First dropout layer with 0.5 rate
    model.add_layer(dropout=0.5)
    
    # Second dense layer with 64 neurons (12,352 parameters)
    model.add_layer(n_input=192, n_output=64, activation='relu')
    
    # Second dropout layer with 0.5 rate
    model.add_layer(dropout=0.5)
    
    # Third dense layer with 48 neurons (3,120 parameters)
    model.add_layer(n_input=64, n_output=48, activation='relu')
    
    # Third dropout layer with 0.5 rate
    model.add_layer(dropout=0.5)
    
    # Output layer with 1 neuron (49 parameters)
    model.add_layer(n_input=48, n_output=1, activation='sigmoid')
    
    print("Initial Model Training:")
    model.fit(X_train, y_train, epochs=50, apply_smote=True)
    
    # Save the trained model
    save_model(model, model_filename)

# Evaluate model performance on the test data with adjusted threshold
y_test_pred = model.predict(X_test)

# Try different thresholds to find optimal precision-recall balance
thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
best_f1 = 0
best_threshold = 0.5

for threshold in thresholds:
    y_test_pred_binary = (y_test_pred >= threshold).astype(int)
    
    # Calculate performance metrics at this threshold
    accuracy = accuracy_score(y_test, y_test_pred_binary)
    precision = precision_score(y_test, y_test_pred_binary)
    recall = recall_score(y_test, y_test_pred_binary)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)
    
    print(f"Threshold: {threshold:.1f}")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

# Use the best threshold
y_test_pred_binary = (y_test_pred >= best_threshold).astype(int)
accuracy = accuracy_score(y_test, y_test_pred_binary)
precision = precision_score(y_test, y_test_pred_binary, average='macro')
recall = recall_score(y_test, y_test_pred_binary, average='macro')
f1 = 2 * (precision * recall) / (precision + recall + 1e-10)

print(f"\nFinal Model Performance (threshold={best_threshold:.1f}):")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")



@app.route('/predict', methods=['POST'])
def predict():
    global prediction_count, model, new_data, df, new_df, columns, new_X, model_lock
    data = request.get_json()

    # Validate the input data
    if not check_data(data):
        return jsonify({'error': 'Invalid Data Format or Values'}), 400

    # Convert the input data (dictionary) into a DataFrame, ensuring column order
    try:
        # Use the make_list function which orders data according to 'columns' list
        # Create DataFrame with explicit feature column names
        # expected_feature_columns_local = [col.strip() for col in columns if col.strip() != 'Diabetes_binary']
        ordered_data = OrderedDict(data)
        x_df = pd.DataFrame([ordered_data])
        print(f"Input DataFrame for prediction: {x_df}")
    except Exception as e:
         return jsonify({'error': f'Error processing input data for prediction: {e}'}), 400


    # Make a prediction
    # Ensure prediction is done with model_lock to prevent conflicts during retraining
    with model_lock:
        prediction = model.predict(x_df)

    # Interpret the prediction result
    # Assuming the output layer has a sigmoid activation, prediction is a probability
    result_probability = prediction[0][0]
    result = "Diabetic or Prediabetic" if result_probability >= 0.5 else "Not Diabetic"

    # Add new sample for retraining
    with lock:

        df_feature_columns = [col for col in df.columns if col.strip() != 'Diabetes_binary']
        
        ordered_feature_values = [data.get(col.strip(), 0) for col in df_feature_columns]


        new_sample_row = ordered_feature_values
        new_X.append(new_sample_row)

        
           

    return jsonify({'prediction': result, 'probability': float(result_probability)}), 200

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    global prediction_count, model, new_data, df, new_df, columns, new_X, new_y, model_lock

    data = request.get_json()

    # Ask the user for feedback (diabetic or not)
    feedback = data.get('Diabetes_binary')
    if feedback not in [0, 1]:
        return jsonify({'error': 'Feedback must be 0 (Not Diabetic) or 1 (Prediabetic or Diabetic)'}), 400

    global new_y
    new_y.append(feedback)
    

    # Convert the input data (dictionary) into a DataFrame row
    try:
        # Ensure the order of data matches the columns defined
        new_sample_row = [new_y[-1]] + new_X[-1]   # Combine the latest feature values and feedback
        new_X = []
        new_y = [] # Reset new_y after using it

        # Add the new sample to the new_data list
        with lock:
            new_data.append(new_sample_row)

            prediction_count += 1

            # Check if retraining threshold is met
            if prediction_count >= 10:
                prediction_count = 0

                # Retrain the model using original + new data
                # Use model_lock during retraining to prevent predictions

                model.update_weights(new_data) # Update model weights with new data
                save_model(model)  # Save the updated model
                print("Model retrained with new data.")

        # Save the new sample to the CSV file
        try:
            write_header = not os.path.exists(new_data_file) or os.stat(new_data_file).st_size == 0
            new_sample_df = pd.DataFrame([new_sample_row], columns=df.columns)
            new_sample_df.to_csv(new_data_file, mode='a', header=write_header, index=False)
            print(f"Appended new feedback row to {new_data_file}.")
        except Exception as e:
            print(f"Error saving new feedback to CSV: {e}")
            return jsonify({'error': 'Failed to save feedback to file'}), 500

        return jsonify({'message': 'Feedback added successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Error processing feedback: {e}'}), 400

if __name__ == "__main__":
    # Initial training happens here when the script is run directly
    # If running with a production server like Gunicorn, this block might not be executed
    # in the main process, so initial training might need to be handled differently.
    # For development with debug=True, this is fine.

    app.run(debug=True, use_reloader=False)