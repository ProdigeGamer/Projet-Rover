import matplotlib
matplotlib.use('Agg')  # Mode non-interactif pour matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Copie ici le contenu de points.txt
data =[
 (0.0205, -0.2608),
 (0.0361, -0.2282),
 (0.0530, -0.2208),
 (0.0688, -0.2116),
 (0.0817, -0.1973),
 (0.0949, -0.1862),
 (0.1026, -0.1674),
 (0.1136, -0.1564),
 (0.1267, -0.1484),
 (0.1376, -0.1376),
 (0.1388, -0.1186),
 (0.1536, -0.1116),
 (0.1573, -0.0964),
 (0.1686, -0.0859),
 (0.1698, -0.0703),
 (0.1754, -0.0570),
 (0.1835, -0.0441),
 (0.1817, -0.0288),
 (0.1786, -0.0141),
 (0.1839, 0.0000),
 (0.1863, 0.0147),
 (0.1857, 0.0294),
 (0.1785, 0.0429),
 (0.1788, 0.0581),
 (0.1739, 0.0720),
 (0.1675, 0.0854),
 (0.1628, 0.0998),
 (0.1554, 0.1129),
 (0.1484, 0.1267),
 (0.1392, 0.1392),
 (0.1260, 0.1475),
 (0.1210, 0.1666),
 (0.1054, 0.1721),
 (0.1013, 0.1987),
 (0.3303, 0.7974),
 (0.2589, 0.7969),
 (-0.0000, 0.9285),
 (0.0514, 24.6753),
 (0.0779, 24.6757),
 (0.0992, 24.6947),
 (0.0925, 24.7767),
 (0.1033, 24.7972),
 (0.1165, 24.8098),
 (0.1268, 24.8255),
 (0.1418, 24.8340),
 (0.1574, 24.8426),
 (0.1656, 24.8586),
 (0.1760, 24.8721),
 (0.1767, 24.8917),
 (0.1848, 24.9058),
 (0.1966, 24.9186),
 (0.1979, 24.9357),
 (0.2002, 24.9519),
 (0.2057, 24.9674),
 (0.2076, 24.9837),
 (0.2076, 25.0000),
 (0.2117, 25.0167),
 (0.2064, 25.0327),
 (0.2106, 25.0506),
 (0.2019, 25.0656),
 (0.2043, 25.0846),
 (0.1971, 25.1004),
 (0.1886, 25.1156),
 (0.1894, 25.1376),
 (0.1750, 25.1495),
 (0.6216, 25.6216),
 (0.5578, 25.6531),
 (0.5232, 25.7201),
 (0.4546, 25.7418),
 (0.4067, 25.7981),
 (0.2040, 25.6280),
 (0.1383, 25.5759),
 (0.0943, 25.5956),
 (0.0461, 25.5854),
 (-0.0000, 25.5783),
 (0.0537, 49.6610),
 (0.0801, 49.6664),
 (0.0797, 49.7547),
 (0.0858, 49.7928),
 (0.1021, 49.7996),
 (0.1153, 49.8119),
 (0.1238, 49.8296),
 (0.1382, 49.8382),
 (0.1486, 49.8514),
 (0.1624, 49.8613),
 (0.1694, 49.8769),
 (0.1821, 49.8884),
 (0.1862, 49.9051),
 (0.1929, 49.9201),
 (0.1979, 49.9357),
 (0.2017, 49.9516),
 (0.2057, 49.9674),
 (0.2076, 49.9837),
 (0.2023, 50.0000),
 (0.2037, 50.0160),
 (0.2030, 50.0322),
 (0.2065, 50.0496),
 (0.1853, 50.0602),
 (0.2043, 50.0846),
 (0.1936, 50.0986),
 (0.1997, 50.1224),
 (0.1861, 50.1352),
 (0.1944, 50.1660),
 (0.2046, 50.2046),
 (0.5190, 50.6077),
 (0.4741, 50.6526),
 (0.4282, 50.6988),
 (0.3916, 50.7686),
 (0.3642, 50.8794),
 (0.1962, 50.6037),
 (0.1432, 50.5966),
 (0.0933, 50.5890),
 (0.0454, 50.5774),
 (-0.0000, 50.5916),
 (0.0406, 74.7439),
 (0.0768, 74.6800),
 (0.0786, 74.7580),
 (0.0909, 74.7804),
 (0.1055, 74.7929),
 (0.1168, 74.8094),
 (0.1315, 74.8190),
 (0.1422, 74.8335),
 (0.1513, 74.8487),
 (0.1660, 74.8582),
 (0.1694, 74.8769),
 (0.1821, 74.8884),
 (0.1825, 74.9070),
 (0.1929, 74.9201),
 (0.2021, 74.9343),
 (0.1982, 74.9524),
 (0.2057, 74.9674),
 (0.2076, 74.9837),
 (0.2125, 75.0000),
 (0.2117, 75.0167),
 (0.2097, 75.0332),
 (0.2007, 75.0482),
 (0.2019, 75.0656),
 (0.2037, 75.0844),
 (0.1856, 75.0945),
 (0.1886, 75.1156),
 (0.1895, 75.1377),
 (0.1750, 75.1495),
 (0.2077, 75.2077),
 (0.5067, 75.5932),
 (0.4734, 75.6516),
 (0.4144, 75.6762),
 (0.4361, 75.8558),
 (0.3669, 75.8857),
 (0.1365, 75.5686),
 (0.0936, 75.5907),
 (0.0464, 75.5899),
 (-0.0000, 75.5828)
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