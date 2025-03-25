import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

# Loading in preprocessed data
df = pd.read_csv("preprocessed_data.csv")


# Mapping delay classes to standardised delay values from preprocessed data
# 0      -> class 0
# 0.0625 -> class 1
# 0.125  -> class 2
# 0.25   -> class 3
# 0.5    -> class 4
# 1      -> class 5
delay_mapping = {0.0: 0, 0.0625: 1, 0.125: 2, 0.25: 3, 0.5: 4, 1.0: 5}
df["Delay_Class"] = df["Departure Delay"].apply(lambda x: delay_mapping.get(round(x, 4), 0))

# Check the distribution of the classes (showing inbalance of delay data)
print("Delay Class Distribution:")
print(df["Delay_Class"].value_counts())


# Columns that will be used from the preprocessed data
predictor_cols = [
    "Origin Airport", "Destination Airport", "Carrier ID",
    "Month", "Day", "Hour", "Temperature", "Average Wind Speed", "Humidity", "Precipitation"
]
X = df[predictor_cols].values

# Target data
y = df["Delay_Class"].values

# Convert target to categorical (one-hot encoding) with 6 classes 
y_cat = to_categorical(y, num_classes=6)

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Convert one-hot encoded labels back to integer labels to calculate class weights
# Using class weights because data is unbalanced (most delays are 0)
y_train_int = np.argmax(y_train, axis=1)
class_weights = class_weight.compute_class_weight("balanced",
                                                  classes=np.unique(y_train_int),
                                                  y=y_train_int)
class_weights_dict = dict(enumerate(class_weights))
print("Class Weights:", class_weights_dict)

# Building the model
model = Sequential([
    Dense(8, activation="relu", input_dim=X_train.shape[1]),
    #Dropout(0.3),
    #Dense(6, activation="relu"),
    Dense(6, activation="softmax")  # 6 output classes
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.summary()

# Training the model
history = model.fit(X_train, y_train, 
                    validation_data=(X_test, y_test),
                    epochs=10, 
                    batch_size=128,
                    class_weight=class_weights_dict)

# Testing the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}")

# Generating and saving the test values used
y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)
y_true = np.argmax(y_test, axis=1)

# Creating a dataframe with the predictor values, true labels, and predicted labels
df_test = pd.DataFrame(X_test, columns=predictor_cols)
df_test["True_Delay_Class"] = y_true
df_test["Predicted_Delay_Class"] = y_pred

# Saving the test predictions to a .csv file
df_test.to_csv("test_predictions.csv", index=False)
print("Test predictions saved to 'test_predictions.csv'.")

# Saving the model to be used in the server
model.save("model_files/model.keras")
