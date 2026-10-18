# =====================================================================
# Red de informalidad y pluriempleo por actividad económica - EH2025 (INE)
# =====================================================================
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.lines import Line2D

RUTA_DATOS = r"E:/William Collegue/Fall - First Semester/Developing Macroeconomics 505 Kuttner/Memo Cesar/Survey_Household/EH2025_Persona.dta"
RUTA_SALIDA = r"E:/William Collegue/Fall - First Semester/Developing Macroeconomics 505 Kuttner/Memo Cesar/Survey_Household/resultados"
os.makedirs(RUTA_SALIDA, exist_ok=True)

MIN_OBS_ENLACE = 5      # mínimo de observaciones muestrales para dibujar un enlace
TOP_HUB = 10            # sectores conectados a la estrella central

# Fuentes incrustadas como texto (se ven nítidas y se pueden seleccionar en el PDF)
matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                            "font.family": "DejaVu Sans", "font.size": 7.5})

# ---------------------------------------------------------------------
# 1. Datos: ocupados de 14 años o más
# ---------------------------------------------------------------------
df = pd.read_stata(RUTA_DATOS, convert_categoricals=False)
oc = df[(df["condact"] == 1) & (df["pet"] == 1)].copy()

# ---------------------------------------------------------------------
# 2. Mercado de trabajo e informalidad (misma definición que el do-file)
# ---------------------------------------------------------------------
cat, adm, tam = oc["s04b_12"], oc["s04b_13"], oc["s04b_14"]
mt = pd.Series(np.nan, index=oc.index)
mt[cat == 8] = 1                                                      # Doméstico
mt[mt.isna() & adm.isin([1, 2])] = 2                                  # Estatal
mt[mt.isna() & cat.isin([3, 6, 7])] = 3                               # Familiar
mt[mt.isna() & cat.isin([1, 2, 4, 5]) & (tam <= 5)] = 4               # Semiempresarial
mt[mt.isna() & cat.isin([1, 2, 4, 5]) & (tam > 5) & tam.notna()] = 5  # Empresarial

informal = (oc["s04f_36"] != 1).astype(int)        # no aporta a la Gestora
informal[cat.isin([6, 7])] = 1                     # familiares y aprendices sin remuneración
informal[cat.isin([2, 4]) & (mt == 5)] = 0         # empleadores en unidades > 5 personas
oc["informal"] = informal

# ---------------------------------------------------------------------
# 3. Actividad económica (CAEB 2022) agrupada en 42 sectores (nombres en inglés)
# ---------------------------------------------------------------------
def sector(cod, publico=False):
    if not isinstance(cod, str) or cod.strip() == "":
        return None
    c = cod.strip()
    if not c[0].isdigit():                      # algunos códigos vienen solo con la letra de sección
        return {"A": "Crop farming", "B": "Metal mining", "C": "Bakery & other food",
                "F": "Building construction", "G": "Retail trade", "H": "Land transport",
                "I": "Food & beverage services", "O": "Public administration",
                "P": "Private education", "Q": "Private health", "S": "Other personal services",
                "T": "Domestic work"}.get(c[0].upper())
    if len(c) < 2:
        return None
    d2, d3, d4 = int(c[:2]), c[:3], c[:4]
    if d2 == 1:
        if d4 == "0128":           return "Coca & spice crops"
        if d3 == "014":            return "Livestock"
        return "Crop farming"
    if d2 in (2, 3):               return "Forestry & fishing"
    if d2 == 7:                    return "Metal mining"
    if d2 in (5, 6, 8, 9):         return "Oil, gas & other mining"
    if d2 == 10:
        return "Meat & dairy" if d3 in ("101", "105") else "Bakery & other food"
    if d2 in (11, 12):             return "Beverages & tobacco"
    if d2 in (13, 15):             return "Textiles, leather & footwear"
    if d2 == 14:                   return "Apparel"
    if d2 == 16:                   return "Wood products"
    if d2 in (17, 18):             return "Paper & printing"
    if d2 in (19, 20, 21, 22):     return "Chemicals & plastics"
    if d2 == 23:                   return "Non-metallic minerals"
    if d2 in (24, 25):             return "Metal products"
    if d2 in (26, 27, 28, 29, 30, 33): return "Machinery & equipment"
    if d2 in (31, 32):             return "Furniture & other mfg."
    if 35 <= d2 <= 39:             return "Electricity, gas & water"
    if d2 == 41:                   return "Building construction"
    if d2 == 42:                   return "Civil engineering"
    if d2 == 43:                   return "Specialized construction"
    if d2 == 45:                   return "Vehicle trade & repair"
    if d2 == 46:                   return "Wholesale trade"
    if d2 == 47:                   return "Retail trade"
    if d2 == 49:                   return "Land transport"
    if 50 <= d2 <= 53:             return "Storage & other transport"
    if d2 == 55:                   return "Accommodation"
    if d2 == 56:                   return "Food & beverage services"
    if 58 <= d2 <= 63:             return "Information & communication"
    if 64 <= d2 <= 66:             return "Financial services"
    if d2 == 68:                   return "Real estate"
    if 69 <= d2 <= 75:             return "Professional services"
    if 77 <= d2 <= 82:             return "Administrative services"
    if d2 == 84:                   return "Public administration"
    if d2 == 85:                   return "Public education" if publico else "Private education"
    if 86 <= d2 <= 88:             return "Public health" if publico else "Private health"
    if 90 <= d2 <= 93:             return "Arts & recreation"
    if 94 <= d2 <= 96:             return "Other personal services"
    if d2 in (97, 98):             return "Domestic work"
    return None                    # 99: organismos extraterritoriales

# Orden alrededor del círculo (agrupado por gran sector, en sentido horario desde arriba)
ORDEN = ["Crop farming", "Coca & spice crops", "Livestock", "Forestry & fishing",
         "Oil, gas & other mining", "Metal mining",
         "Meat & dairy", "Bakery & other food", "Beverages & tobacco",
         "Textiles, leather & footwear", "Apparel", "Wood products", "Paper & printing",
         "Chemicals & plastics", "Non-metallic minerals", "Metal products",
         "Machinery & equipment", "Furniture & other mfg.", "Electricity, gas & water",
         "Building construction", "Civil engineering", "Specialized construction",
         "Vehicle trade & repair", "Wholesale trade", "Retail trade",
         "Land transport", "Storage & other transport",
         "Accommodation", "Food & beverage services", "Information & communication",
         "Financial services", "Real estate", "Professional services",
         "Administrative services", "Public administration", "Public education",
         "Private education", "Public health", "Private health", "Arts & recreation",
         "Other personal services", "Domestic work"]

oc["sec"] = [sector(c, p) for c, p in zip(oc["s04b_10a_cod"], oc["s04b_13"].isin([1, 2]))]
oc = oc[oc["sec"].notna()]

# ---------------------------------------------------------------------
# 4. Nodos: ocupados (expandidos) y tasa de informalidad por sector
# ---------------------------------------------------------------------
oc["w_inf"] = oc["factor"] * oc["informal"]
nodos = oc.groupby("sec").agg(ocupados=("factor", "sum"), informales=("w_inf", "sum"),
                              n=("factor", "size")).reindex(ORDEN)
nodos["tasa"] = 100 * nodos["informales"] / nodos["ocupados"]

# ---------------------------------------------------------------------
# 5. Enlaces: ocupación principal en un sector y secundaria en otro
# ---------------------------------------------------------------------
pl = oc[oc["s04e_25"] == 1].copy()
pl["sec2"] = [sector(c, p) for c, p in zip(pl["s04e_26_cod"], pl["s04e_28"].isin([1, 2]))]
pl = pl[pl["sec2"].notna() & (pl["sec"] != pl["sec2"])]
pl["par"] = [tuple(sorted(t)) for t in zip(pl["sec"], pl["sec2"])]
enl = pl.groupby("par").agg(personas=("factor", "sum"), n=("factor", "size"))
enl = enl[enl["n"] >= MIN_OBS_ENLACE].sort_values("personas")

top = nodos.sort_values("informales", ascending=False).head(TOP_HUB)
cuota_top = 100 * top["informales"].sum() / nodos["informales"].sum()

# ---------------------------------------------------------------------
# 6. Escalas y colores
#    Color: 5 clases de informalidad (rampa de un solo tono, validada para
#    daltonismo y contraste con el fondo blanco)
# ---------------------------------------------------------------------
CLASES = [0, 25, 50, 75, 90, 100]
RAMPA = ["#eba273", "#dd7449", "#c64b33", "#992e2c", "#5c1a25"]
CMAP = colors.ListedColormap(RAMPA)
NORM = colors.BoundaryNorm(CLASES, CMAP.N)
GRIS_ENLACE = "#59606b"
AZUL = "#2a78d6"          # líneas punteadas hacia la estrella
AZUL_OSCURO = "#184f95"   # estrella
TINTA, TINTA_2 = "#1f1f1f", "#52514e"

FIG_W, FIG_H = 8.0, 9.0
AX_POS = [0.0, 0.13, 1.0, 0.87]          # red arriba, leyenda abajo
LIM = 1.92
PT_POR_UNIDAD = 72 * min(FIG_W * AX_POS[2], FIG_H * AX_POS[3]) / (2 * LIM)

def area_nodo(x):                        # área del círculo (pt²) proporcional a los ocupados
    return 25 + 800 * x / nodos["ocupados"].max()

WMAX = enl["personas"].max()
def ancho_enlace(w):                     # grosor de la línea (pt)
    return 0.35 + 4.2 * (w / WMAX) ** 0.8

# Posiciones en el círculo
ang = np.pi / 2 - 2 * np.pi * np.arange(len(ORDEN)) / len(ORDEN)
pos = {s: (np.cos(a), np.sin(a)) for s, a in zip(ORDEN, ang)}
angulo = dict(zip(ORDEN, ang))

# ---------------------------------------------------------------------
# 7. Gráfico
# ---------------------------------------------------------------------
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes(AX_POS)
ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM)
ax.set_aspect("equal"); ax.axis("off")

# Enlaces de pluriempleo (los más gruesos encima)
for (a, b), fila in enl.iterrows():
    f = fila["personas"] / WMAX
    ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=GRIS_ENLACE,
            lw=ancho_enlace(fila["personas"]), alpha=0.35 + 0.45 * f,
            solid_capstyle="round", zorder=1)

# Líneas punteadas hacia los sectores con más empleo informal
for s in top.index:
    ax.plot([0, pos[s][0]], [0, pos[s][1]], color=AZUL, lw=1.0, ls=(0, (2.5, 2)), zorder=2)

# Nodos y etiquetas radiales
for s in ORDEN:
    x, y = pos[s]
    area = area_nodo(nodos.loc[s, "ocupados"])
    ax.scatter(x, y, s=area, color=CMAP(NORM(nodos.loc[s, "tasa"])),
               edgecolors="white", linewidths=0.8, zorder=3)
    a = angulo[s]
    r = 1 + np.sqrt(area / np.pi) / PT_POR_UNIDAD + 0.03
    izquierda = np.cos(a) < -1e-9
    rot = np.degrees(a) + (180 if izquierda else 0)
    ax.text(r * np.cos(a), r * np.sin(a), f"{s} ({nodos.loc[s, 'tasa']:.0f}%)",
            rotation=rot, rotation_mode="anchor", ha="right" if izquierda else "left",
            va="center", color=TINTA, zorder=4)

# Estrella central
ax.scatter(0, 0, marker="*", s=1300, color=AZUL_OSCURO, edgecolors="white", linewidths=1.2, zorder=5)
ax.text(0, -0.10, "Informal\nemployment", ha="center", va="top", fontsize=8, weight="bold",
        color=TINTA, zorder=6, linespacing=1.0,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))

# ---------------------------------------------------------------------
# 8. Leyenda (abajo, en tres bloques)
# ---------------------------------------------------------------------
lg = fig.add_axes([0.04, 0.0, 0.92, 0.115])
lg.set_xlim(0, 100); lg.set_ylim(0, 10); lg.axis("off")

# Bloque 1: tasa de informalidad
lg.text(0, 9.2, "Informal employment rate (%)", weight="bold", color=TINTA, va="center")
etiquetas = ["0–25", "25–50", "50–75", "75–90", "90–100"]
for i, (c, e) in enumerate(zip(RAMPA, etiquetas)):
    lg.scatter(1.5, 7.3 - 1.55 * i, s=55, color=c, edgecolors="white", linewidths=0.8)
    lg.text(3.5, 7.3 - 1.55 * i, e, va="center", color=TINTA_2)

# Bloque 2: tamaño del nodo
lg.text(30, 9.2, "Employed workers", weight="bold", color=TINTA, va="center")
for i, v in enumerate([100_000, 400_000, 900_000]):
    lg.scatter(32 + 7.5 * i, 4.6, s=area_nodo(v), color="#bdbab3", edgecolors="white", linewidths=0.8)
    lg.text(32 + 7.5 * i, 1.4, f"{v / 1000:,.0f}k", ha="center", va="center", color=TINTA_2)

# Bloque 3: líneas
lg.text(60, 9.2, "Workers with jobs in both sectors", weight="bold", color=TINTA, va="center")
for i, v in enumerate([10_000, 40_000, 75_000]):
    yy = 7.3 - 1.55 * i
    lg.plot([60.5, 67], [yy, yy], color=GRIS_ENLACE, lw=ancho_enlace(v), solid_capstyle="round",
            alpha=0.35 + 0.45 * v / WMAX)
    lg.text(69, yy, f"{v / 1000:,.0f}k", va="center", color=TINTA_2)
yy = 7.3 - 1.55 * 3.3
lg.plot([60.5, 67], [yy, yy], color=AZUL, lw=1.0, ls=(0, (2.5, 2)))
lg.text(69, yy, f"Top {TOP_HUB} sectors by informal employment\n({cuota_top:.0f}% of all informal workers)",
        va="center", color=TINTA_2, linespacing=1.1)

# ---------------------------------------------------------------------
# 9. Guardar
# ---------------------------------------------------------------------
for ext, dpi in (("pdf", None), ("png", 600)):
    fig.savefig(f"{RUTA_SALIDA}/pluriemployment_network.{ext}", dpi=dpi,
                bbox_inches="tight", pad_inches=0.05, facecolor="white")
plt.close(fig)
print(f"Listo. {len(enl)} enlaces. Archivos en: {RUTA_SALIDA}")
