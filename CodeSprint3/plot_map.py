import matplotlib
matplotlib.use('Agg')  # Mode non-interactif pour matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Copie ici le contenu de points.txt
data =[
 (-0.0000, -3.7981),
 (0.4259, -0.6950),
 (2.3105, -0.9570),
 (2.5262, -0.4001),
 (2.5411, -0.2000),
 (2.5660, 0.0000),
 (2.4910, 0.1960),
 (2.5127, 0.3980),
 (2.4338, 0.5843),
 (2.3799, 0.7733),
 (1.1249, 0.4659),
 (1.0960, 0.5585),
 (1.0483, 0.6424),
 (1.0153, 0.7376),
 (0.9345, 0.7981),
 (0.8687, 0.8687),
 (0.7865, 0.9209),
 (0.7168, 0.9865),
 (0.6301, 1.0283),
 (0.5572, 1.0936),
 (0.4614, 1.1139),
 (0.3725, 1.1465),
 (0.2793, 1.1636),
 (0.1871, 1.1812),
 (0.0952, 1.2101),
 (-0.0000, 1.2004),
 (-0.0000, 24.0371),
 (0.1136, 23.5564),
 (0.6616, 24.0894),
 (0.7122, 24.2878),
 (0.8113, 24.4106),
 (0.9265, 24.6162),
 (1.3685, 24.5554),
 (1.5041, 24.6389),
 (1.4150, 24.7759),
 (1.4067, 24.8893),
 (1.0020, 25.0000),
 (1.4165, 25.1115),
 (1.4944, 25.2367),
 (1.3659, 25.3279),
 (1.3190, 25.4286),
 (1.3267, 25.5495),
 (1.2327, 25.6281),
 (1.1715, 25.7179),
 (1.1289, 25.8202),
 (1.0613, 25.9064),
 (0.9808, 25.9808),
 (0.7051, 25.8255),
 (0.8206, 26.1294),
 (0.5320, 25.8681),
 (0.4505, 25.8841),
 (0.3616, 25.8731),
 (0.3012, 25.9271),
 (0.2226, 25.9270),
 (0.1478, 25.9331),
 (0.0737, 25.9370),
 (-0.0000, 25.9651),
 (-0.0000, 48.7065),
 (0.0962, 48.7777),
 (0.2992, 48.7538),
 (0.4008, 48.7664),
 (0.4861, 48.8265),
 (0.5702, 48.8809),
 (0.4804, 49.2161),
 (0.7437, 48.9763),
 (0.7816, 49.3325),
 (0.7329, 49.4675),
 (0.9611, 49.5103),
 (0.9455, 49.6084),
 (0.8930, 49.7856),
 (1.0014, 49.8414),
 (1.1356, 50.0000),
 (1.1161, 50.4623),
 (2.0052, 51.0217),
 (0.9944, 50.7224),
 (1.7433, 51.4889),
 (1.4476, 51.6950),
 (0.7156, 50.9849),
 (0.6315, 51.0304),
 (0.5467, 51.0730),
 (0.4704, 51.1357),
 (0.3880, 51.1942),
 (0.2861, 51.1918),
 (0.1945, 51.2281),
 (0.1003, 51.2745),
 (-0.0000, 51.2619),
 (-0.0000, 74.0079),
 (0.0762, 74.0313),
 (0.1224, 74.2271),
 (0.1116, 74.5352),
 (0.2020, 74.3783),
 (0.3031, 74.2683),
 (0.4017, 74.3445),
 (0.4092, 74.4368),
 (0.4908, 74.4254),
 (0.5431, 74.4569),
 (0.6098, 74.4792),
 (0.6620, 74.5943),
 (0.9113, 74.5357),
 (0.9251, 74.6168),
 (0.9440, 74.6933),
 (0.9315, 74.7764),
 (0.9462, 74.8501),
 (0.9426, 74.9258),
 (0.9663, 75.0000),
 (0.9543, 75.0751),
 (0.9502, 75.1505),
 (0.9148, 75.2196),
 (0.8988, 75.2920),
 (0.8769, 75.3632),
 (0.8452, 75.4307),
 (0.7942, 75.4867),
 (0.7640, 75.5551),
 (0.7118, 75.6079),
 (0.6682, 75.6682),
 (0.6079, 75.7118),
 (0.5503, 75.7574),
 (0.4913, 75.8017),
 (0.4268, 75.8376),
 (0.3551, 75.8572),
 (0.2933, 75.9027),
 (0.2256, 75.9397),
 (0.1512, 75.9549),
 (0.1064, 76.3522),
 (-0.0000, 76.2689)
]
# Conversion Mètres -> Centimètres pour le plot
xs = [p[0] * 100 for p in data]
ys = [p[1] * 100 for p in data]

plt.figure(figsize=(12, 10))
plt.plot(ys, xs, color='darkblue', linewidth=2, label="Contour obstacle")
plt.scatter(ys, xs, color='blue', label="Points détectés", s=50, alpha=0.7)

# --- Position du ROVER ---
# Rover à x=0, y=0 (position initiale du scan)
rover_x = 0
rover_y = 0
plt.scatter([rover_x], [rover_y], color='red', marker='^', s=200, label="Rover", zorder=5)
plt.axvline(x=0, color='red', linestyle='--', alpha=0.3, linewidth=1)  # Ligne de référence x=0
plt.text(rover_x + 10, rover_y + 5, "Rover\nx=0", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

# --- GRILLE 1 CARREAU = 1 CM ---
# On définit une zone de vue qui couvre tous les points
plt.xlim(-100, 100)
plt.ylim(-50, 180)

# Pas de grille adapté aux nouvelles données
plt.xticks(range(-100, 101, 20)) 
plt.yticks(range(-50, 181, 20))

plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True, which='both', linestyle='-', alpha=0.3)
plt.xlabel("Y (cm)")
plt.ylabel("X (cm)")
plt.title("Carte des obstacles - Vue en CM (1 carreau = 1 cm)")
plt.legend(loc='upper right')
plt.tight_layout()

# --- VERSION HTML AVEC PLOTLY ---
fig = go.Figure()

# Ajouter les points
fig.add_trace(go.Scatter(
    x=ys, 
    y=xs,
    mode='lines+markers',
    name='Contour obstacle',
    line=dict(color='darkblue', width=2),
    marker=dict(color='blue', size=5, opacity=0.7),
    hovertemplate='<b>Point</b><br>Y: %{x:.2f} cm<br>X: %{y:.2f} cm<extra></extra>'
))

# Ajouter la position du rover
fig.add_trace(go.Scatter(
    x=[rover_y],
    y=[rover_x],
    mode='markers',
    name='Rover',
    marker=dict(symbol='triangle-up', color='red', size=15),
    hovertemplate='<b>Rover</b><br>Y: %{x:.2f} cm<br>X: %{y:.2f} cm<extra></extra>'
))

# Configurer le layout
fig.update_layout(
    title='Carte des obstacles - Vue en CM (1 carreau = 1 cm)',
    xaxis_title='Y (cm)',
    yaxis_title='X (cm)',
    height=800,
    width=1000,
    hovermode='closest',
    template='plotly_white',
    xaxis=dict(
        range=[-100, 100],
        gridwidth=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='red'
    ),
    yaxis=dict(
        range=[-50, 180],
        scaleanchor="x",
        scaleratio=1
    )
)

# Sauvegarder en HTML
fig.write_html("plot_map.html")
print("✓ Fichier HTML généré : plot_map.html")

# Sauvegarder le plot matplotlib en PNG
plt.savefig("plot_map.png", dpi=150, bbox_inches='tight')
print("✓ Fichier PNG généré : plot_map.png")