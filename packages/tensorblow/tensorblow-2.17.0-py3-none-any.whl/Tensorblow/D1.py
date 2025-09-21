import numpy as np
import matplotlib.pyplot as plt

layers = [4, 8, 3]
W1, W2 = np.random.randn(4, 8), np.random.randn(8, 3)
weights = [W1, W2]

fig, ax = plt.subplots()
ax.axis('off')
x_coords = [0, 1, 2]
y_positions = {i: np.linspace(0, 1, num=layers[i]) for i in range(len(layers))}

for l, size in enumerate(layers):
    for n in range(size):
        circle = plt.Circle((x_coords[l], y_positions[l][n]), 0.03, color='skyblue', ec='black')
        ax.add_patch(circle)

for idx, W in enumerate(weights):
    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            ax.plot([x_coords[idx], x_coords[idx+1]], [y_positions[idx][i], y_positions[idx+1][j]], linewidth=0.5)

ax.set_title('4-8-3 Neural Network Architecture')
plt.show()
