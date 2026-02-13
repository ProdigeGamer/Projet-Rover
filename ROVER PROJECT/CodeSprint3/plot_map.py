import matplotlib.pyplot as plt

# Copie ici le contenu de points.txt
data = [
 (-0.0000, -2.1853),
 (1.6415, -1.1926),
 (1.9292, -0.6268),
 (2.0240, 0.0000),
 (2.6991, 0.8770),
 (2.2720, 1.6507),
 (1.6478, 2.2681),
 (0.8734, 2.6881),
 (-0.0000, 2.1769)
]

# Conversion Mètres -> Centimètres pour le plot
xs = [p[0] * 100 for p in data]
ys = [p[1] * 100 for p in data]

plt.figure(figsize=(10, 10))
plt.scatter(xs, ys, color='blue', label="Obstacles")

# --- GRILLE 1 CARREAU = 1 CM ---
# On définit une zone de vue (ex: de -50cm à +50cm)
plt.xlim(-50, 50)
plt.ylim(-10, 100)

# Pas de 1 pour chaque trait de la grille
plt.xticks(range(-50, 51, 1)) 
plt.yticks(range(-10, 101, 1))

plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True, which='both', linestyle='-', alpha=0.3)
plt.title("Vue en CM (1 carreau = 1 cm)")
plt.show()