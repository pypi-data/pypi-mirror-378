import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import Dense

df = pd.read_csv("titanic.csv", usecols=['Pclass','Gender','Age','Fare','Survived']).dropna()
df['Gender'] = df['Gender'].map({'male':0,'female':1})

X = df[['Pclass','Gender','Age','Fare']].astype('float32').to_numpy()
y = df['Survived'].astype('float32').to_numpy().reshape(-1,1)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
scaler = StandardScaler().fit(X_tr)
X_tr, X_te = scaler.transform(X_tr).astype('float32'), scaler.transform(X_te).astype('float32')

model = Sequential([Input(shape=(4,)), Dense(1, activation='sigmoid')])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
h = model.fit(X_tr, y_tr, epochs=30, batch_size=16, validation_split=0.2, verbose=0)

plt.figure(figsize=(8,3))
for i,(key,title) in enumerate([('loss','Loss'),('accuracy','Accuracy')]):
    plt.subplot(1,2,i+1)
    plt.plot(h.history[key], label='train')
    plt.plot(h.history['val_'+key], label='val')
    plt.title(title); plt.legend()
plt.tight_layout(); plt.show()

loss, acc = model.evaluate(X_te, y_te, verbose=0)
print(f"Test Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")
