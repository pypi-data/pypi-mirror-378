import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input
from tensorflow.keras.utils import to_categorical

df = pd.read_csv('mnist_train.csv')
y = df.iloc[:,0].values
X = df.iloc[:,1:].values.reshape(-1,28,28,1).astype('float32')/255.0
y = to_categorical(y, num_classes=10)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=np.argmax(y,1), random_state=42)

model = Sequential([
    Input(shape=(28,28,1)),
    Conv2D(32,3,activation='relu'),
    MaxPooling2D(),
    Flatten(),
    Dense(64,activation='relu'),
    Dense(10,activation='softmax')
])
model.compile('adam','categorical_crossentropy',metrics=['accuracy'])
hist = model.fit(X_train,y_train,epochs=5,batch_size=128,validation_split=0.2,verbose=0)

pd.DataFrame(hist.history)[['loss','val_loss','accuracy','val_accuracy']]\
    .plot(figsize=(10,4), grid=True, title="CNN Training vs Validation Curves")
plt.show()

loss, acc = model.evaluate(X_test,y_test,verbose=0)
print(f"Final Test Loss: {loss:.4f}\nFinal Test Accuracy: {acc:.4f}")
