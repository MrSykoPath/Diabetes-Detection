#import
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
import pandas as pd
import threading
import os
import time # Added for timestamp in backup file name


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
        tmp = np.clip(tmp, -1.0, 1.0)

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

    def forward(self, Ai):
        # Dropout layer also needs to handle potentially non-NumPy input
        Ai = np.asarray(Ai) # Ensure input is NumPy array
        if self.training:
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
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-7  # Slightly larger to avoid log(0)
        yhat = np.clip(yhat, epsilon, 1 - epsilon)

        pt = y * yhat + (1 - y) * (1 - yhat)
        pt = np.clip(pt, epsilon, 1 - epsilon)  # extra safety

        alpha_t = y * alpha + (1 - y) * (1 - alpha)
        loss = -alpha_t * (1 - pt) ** gamma * np.log(pt + epsilon)

        return np.mean(loss)


    def _diff_focal_loss(self, y, yhat, gamma=2, alpha=0.25):
        # Ensure inputs are NumPy arrays
        y = np.asarray(y)
        yhat = np.asarray(yhat)
        epsilon = 1e-7
        yhat = np.clip(yhat, epsilon, 1 - epsilon)

        pt = y * yhat + (1 - y) * (1 - yhat)
        alpha_t = y * alpha + (1 - y) * (1 - alpha)

        
        dpt = yhat - y 
        grad = alpha_t * gamma * ((1 - pt) ** (gamma - 1)) * (-np.log(pt + epsilon)) * dpt \
             + alpha_t * ((1 - pt) ** gamma) * dpt / (pt + epsilon) 

        # Add clipping to the final gradient as it can still become large
        grad = np.clip(grad, -10.0, 10.0) 

        return grad


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
        # Convert initial input to NumPy array
        a = np.asarray(inp)
        for layer in self.layers:
            # Layers handle their own input conversion now, but this is good practice
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


    def fit(self, x_train,y_train, epochs=5): #data dim is MxN .. M no of examples.. N no of dimension

        M = x_train.shape[0]

        # Convert initial training data to NumPy arrays immediately
        x_train = np.asarray(x_train).T
        y_train = np.asarray(y_train).T


        for i in range(epochs):
            print("Epoche {}/{}".format(i+1,epochs))

            y_hat = self.forward(x_train)
            print(f"y_hat stats - min: {np.min(y_hat)}, max: {np.max(y_hat)}")

            # *** Use Focal Loss instead of Binary Cross-Entropy ***
            loss = self.focal_loss(y_train, y_hat) # Using default gamma=2, alpha=0.25
            print(f"Loss: {loss:.4f}")

            # *** Use the derivative of Focal Loss ***
            dl_dyhat = self._diff_focal_loss(y_train, y_hat)

            if np.any(np.isnan(y_hat)):
                print("NaN detected in y_hat")
            if np.any(np.isnan(dl_dyhat)):
                print("NaN detected in gradient")


            self.backward(dl_dyhat)


            # update using GD
            for layer in self.layers:
                if isinstance(layer, Layer):  # Only update if it's a trainable layer
                     # dW and db were accumulated across the batch in backward
                     # Divide by M here to get the average gradient for the batch update
                    layer.W = layer.W - self.alpha * (layer.dW / M)
                    layer.b = layer.b - self.alpha * (layer.db / M)



            # zeroing deltas for the next epoch
            for layer in self.layers:
                layer.zeroing_delta()

            # Check for NaNs after updates
            for idx, layer in enumerate(self.layers):
                if isinstance(layer, Layer):
                    if np.any(np.isnan(layer.W)) or np.any(np.isnan(layer.b)):
                        print(f"NaN in weights of layer {idx} after update")
                        # *** Added exit here to stop execution immediately upon detecting NaN ***
                        # exit() # Keep this commented out unless you want it to stop hard on NaN


        print("Finished....")


    def update_weights(self, new_data_points):
        global model, df, new_data_file, columns

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
            y_new = new_data_df['Diabetes_binary']
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
CORS(app) # Enable CORS if needed for frontend interaction

columns = []
prediction_count = 0
lock = threading.Lock()
model_lock = threading.Lock()
new_data_file = 'new_data.csv'
new_data = [] # This will store new samples as lists before appending to df


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


# Prepare data for initial training
if 'Diabetes_binary' in df.columns:
    y = df['Diabetes_binary']
    # Ensure X only contains the feature columns based on our 'columns' list
    X = df[expected_feature_columns]
else:
    print("Error: 'Diabetes_binary' column not found in the combined data (Phase 2 data.csv + new_data.csv) for initial training.")
    exit()


# Initialize and train the model
# Using the reduced learning rate and ReLU for hidden layers
model = NN(lr=0.00005)
# Changed hidden layer activations to ReLU
model.add_layer(n_input=X.shape[1], n_output=192, activation='relu')  # Dense(192) - Changed to ReLU
model.add_layer(dropout=0.5)                                             # Dropout
model.add_layer(n_input=192, n_output=64, activation='relu')          # Dense(64) - Changed to ReLU
model.add_layer(dropout=0.5)                                             # Dropout
model.add_layer(n_input=64, n_output=48, activation='relu')           # Dense(48) - Changed to ReLU
model.add_layer(dropout=0.5)                                             # Dropout
model.add_layer(n_input=48, n_output=1, activation='sigmoid')            # Dense(1) - Output layer (Sigmoid)

print("Initial Model Training:")
model.fit(X,y, epochs=10) # Increased epochs for initial training


@app.route('/predict', methods=['POST'])
def predict():
    global prediction_count, model, new_data, df, new_df, columns
    data = request.get_json()

    # Validate the input data
    if not check_data(data):
        return jsonify({'error': 'Invalid Data Format or Values'}), 400

    # Convert the input data (dictionary) into a DataFrame, ensuring column order
    try:
        # Use the make_list function which orders data according to 'columns' list
        x = make_list(data)
        # Create DataFrame with explicit feature column names
        expected_feature_columns_local = [col.strip() for col in columns if col.strip() != 'Diabetes_binary']
        x_df = pd.DataFrame([x], columns=expected_feature_columns_local)
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

        df_feature_columns = [col for col in df.columns]
        
        ordered_feature_values = [data.get(col.strip(), 0) for col in df_feature_columns]


        new_sample_row = ordered_feature_values
        new_data.append(new_sample_row)

        prediction_count += 1

        # Check if retraining threshold is met
        if prediction_count >= 10:
            prediction_count = 0

            # Retrain the model using original + new data
            # Use model_lock during retraining to prevent predictions

            model.update_weights(new_data) # Update model weights with new data
            # with model_lock:
            #     print("Retraining model...")
            #     # Create a DataFrame from accumulated new_data, using the columns from the main df
            #     try:
            #         # Ensure the columns match the format expected by the CSV (including Diabetes_binary)
            #         df_additional = pd.DataFrame(new_data, columns=df.columns)
            #     except Exception as e:
            #         print(f"Error creating DataFrame from new_data during retraining: {e}")
            #         # Clear new_data and return to prevent further issues with potentially malformed data
            #         new_data = []
            #         # Log the error and potentially alert, but allow prediction to continue with old model
            #         return jsonify({'prediction': result, 'probability': float(result_probability), 'warning': 'Error processing new data for retraining.'}), 200


            #     # Save new data to disk - append mode
            #     try:
            #         # Check if file exists to write header only once
            #         write_header = not os.path.exists(new_data_file) # Write header if file doesn't exist
            #         # If file exists but is empty, also write header
            #         if os.path.exists(new_data_file) and os.stat(new_data_file).st_size == 0:
            #              write_header = True

            #         # Append the additional data. Ensure columns match df for consistent saving.
            #         df_additional[df.columns].to_csv(new_data_file, mode='a', header=write_header, index=False)
            #         print(f"Appended {len(df_additional)} new rows to {new_data_file}.")

            #     except Exception as e:
            #         print(f"Error saving new data to csv during retraining: {e}")
            #         # Log the error. Retraining will proceed with data loaded from files below.


            #     try:
            #         # Reload ALL data from scratch for retraining to ensure consistency
            #         temp_df = pd.read_csv('Phase 2 data.csv')
            #         if os.path.exists(new_data_file):
            #              temp_new_df = pd.read_csv(new_data_file)
            #              # Check if columns match before concatenating reloaded data
            #              if list(temp_new_df.columns) == list(temp_df.columns):
            #                  temp_df = pd.concat([temp_df, temp_new_df], ignore_index=True, sort=False)
            #                  print(f"Retraining data includes {len(temp_new_df)} rows from {new_data_file}.")
            #              else:
            #                  print("Warning: Columns in reloaded new_data.csv mismatch main data. Skipping append for retraining.")


            #         # Prepare data for retraining from the reloaded temp_df
            #         if 'Diabetes_binary' in temp_df.columns:
            #             y_retrain = temp_df['Diabetes_binary']
            #             # Ensure X_retrain uses the correct feature columns
            #             expected_feature_columns_local = [c.strip() for c in columns if c.strip() != 'Diabetes_binary']
            #             # Verify all expected columns are present in temp_df before selecting
            #             if all(col in temp_df.columns for col in expected_feature_columns_local):
            #                  X_retrain = temp_df[expected_feature_columns_local]
            #                  df = temp_df # Update the global df reference

            #                  # Clear new data after successful saving/reloading for retraining
            #                  new_data = []


            #                  # Reinitialize and train the model
            #                  # Using the adjusted learning rate
            #                  model = NN(lr=0.00005)
            #                  # Changed hidden layer activations to ReLU for retraining as well
            #                  model.add_layer(n_input=X_retrain.shape[1], n_output=192, activation='relu')
            #                  model.add_layer(dropout=0.5)
            #                  model.add_layer(n_input=192, n_output=64, activation='relu')
            #                  model.add_layer(dropout=0.5)
            #                  model.add_layer(n_input=64, n_output=48, activation='relu')
            #                  model.add_layer(dropout=0.5)
            #                  model.add_layer(n_input=48, n_output=1, activation='sigmoid') # Output layer remains sigmoid
            #                  # *** Use Focal Loss for retraining as well ***
            #                  model.fit(X_retrain, y_retrain, epochs=5) # Reduced epochs for retraining
            #                  print("Retraining complete.")
            #             else:
            #                  missing_retrain_cols = [col for col in expected_feature_columns_local if col not in temp_df.columns]
            #                  print(f"Error: Missing expected feature columns for retraining: {missing_retrain_cols}. Skipping retraining.")


            #         else:
            #              print("Error: 'Diabetes_binary' column not found after reloading data for retraining. Skipping retraining.")


            #     except Exception as e:
            #         print(f"Critical Error during retraining data load or model fit: {e}")
            #         # If retraining fails critically, the model remains the old one.
            #         # A production system would need a more robust strategy (e.g., alerting, fallback model).


    return jsonify({'prediction': result, 'probability': float(result_probability)}), 200


if __name__ == "__main__":
    # Initial training happens here when the script is run directly
    # If running with a production server like Gunicorn, this block might not be executed
    # in the main process, so initial training might need to be handled differently.
    # For development with debug=True, this is fine.

    app.run(debug=True, use_reloader=False)