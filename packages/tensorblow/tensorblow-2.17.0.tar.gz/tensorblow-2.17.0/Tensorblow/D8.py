import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split as tts
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense

df = pd.read_csv("mnist_train.csv")
X = df.drop('label', axis=1).values / 255.0
X_noisy = np.clip(X + np.random.normal(0, 0.4, X.shape), 0., 1.)

X_train, X_test, Xn_train, Xn_test = tts(X, X_noisy, test_size=0.2, random_state=42)

model = Sequential([
    Input((784,)),
    Dense(128, activation='relu'),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(64, activation='relu'),
    Dense(128, activation='relu'),
    Dense(784, activation='sigmoid')
])
model.compile('adam', 'binary_crossentropy')
hist = model.fit(Xn_train, X_train, validation_data=(Xn_test, X_test), epochs=10, verbose=0)

plt.plot(hist.history['loss'], label='Train Loss')
plt.plot(hist.history['val_loss'], label='Val Loss')
plt.title("Denoising AutoENncoder Loss"); plt.xlabel("Epoch"); plt.ylabel("Loss"); plt.legend()
plt.grid(True); plt.show()

decoded = model.predict(Xn_test[:5])
fig, axs = plt.subplots(3,5,figsize=(12,6))
for i in range(5):
    axs[0,i].imshow(Xn_test[i].reshape(28,28), cmap='gray'); axs[0,i].axis('off')
    axs[1,i].imshow(decoded[i].reshape(28,28), cmap='gray'); axs[1,i].axis('off')
    axs[2,i].imshow(X_test[i].reshape(28,28), cmap='gray'); axs[2,i].axis('off')
axs[0,0].set_title("Noisy"); axs[1,0].set_title("Denoised"); axs[2,0].set_title("Original")
plt.suptitle("Denosing Autoencoder Results")
plt.tight_layout(); plt.show()
