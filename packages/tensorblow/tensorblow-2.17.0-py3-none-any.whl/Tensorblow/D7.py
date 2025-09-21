import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import Dense

df = pd.read_csv("banknote.csv")
X = df.iloc[:,:-1].astype('float32').to_numpy()
y = df.iloc[:,-1].astype('float32').to_numpy().reshape(-1,1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
scaler = StandardScaler().fit(X_train)
X_train, X_test = scaler.transform(X_train), scaler.transform(X_test)

model = Sequential([Input(shape=(X_train.shape[1],)), Dense(10, activation='relu'), Dense(1, activation='sigmoid')])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
history = model.fit(X_train, y_train, epochs=30, batch_size=16, validation_split=0.2, verbose=0)

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,4))
ax1.plot(history.history['loss'], label='train'); ax1.plot(history.history['val_loss'], label='val'); ax1.set_title('Loss'); ax1.legend()
ax2.plot(history.history['accuracy'], label='train'); ax2.plot(history.history['val_accuracy'], label='val'); ax2.set_title('Accuracy'); ax2.legend()
plt.tight_layout(); plt.show()

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")
