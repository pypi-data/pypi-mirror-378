import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

df = pd.read_csv("iris.csv")
X = df.iloc[:, :4].astype('float32').to_numpy()
labels = pd.factorize(df.iloc[:, 4].astype(str))[0]
y = to_categorical(labels, num_classes=3).astype('float32')

X_tmp, X_test, y_tmp, y_test, lbl_tmp, lbl_test = train_test_split(
    X, y, labels, test_size=0.2, stratify=labels, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_tmp, y_tmp, test_size=0.25, stratify=lbl_tmp, random_state=42
)

model = Sequential([
    Input(shape=(4,)),
    Dense(16, activation='relu'),
    Dense(12, activation='relu'),
    Dense(3,  activation='softmax')
])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history = model.fit(X_train, y_train, epochs=30, batch_size=16, validation_data=(X_val, y_val), verbose=0)

plt.figure(figsize=(8,3))
for i,(key,title) in enumerate([('loss','Loss'),('accuracy','Accuracy')]):
    plt.subplot(1,2,i+1)
    plt.plot(history.history[key], label='train')
    plt.plot(history.history['val_'+key], label='val')
    plt.title(title); plt.legend()
plt.tight_layout(); plt.show()

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")
