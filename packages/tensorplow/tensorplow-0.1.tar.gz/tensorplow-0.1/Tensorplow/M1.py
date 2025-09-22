import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf

df = pd.read_csv('housing.csv').dropna()
X = df[['median_income', 'housing_median_age', 'total_rooms', 'population']].values
y = df['median_house_value'].values

X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = tf.keras.Sequential([
    tf.keras.Input(shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse')
callback = tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=0, validation_split=0.2, callbacks=[callback])

y_pred = model.predict(X_test).flatten()

mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'MSE: {mse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}')

plt.figure(figsize=(8, 5))
plt.scatter(y_test, y_pred, alpha=0.5, color='green')
plt.xlabel('Actual Pric')
plt.ylabel('Predicted Price')
plt.title('Predicted vs Actual House Price')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red')
plt.grid()
plt.show()
