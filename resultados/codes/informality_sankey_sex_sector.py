# =====================================================================
# Diagrama de Sankey de la informalidad - EH2025 (INE)
# =====================================================================
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.path import Path
from matplotlib.patches import PathPatch

RUTA_DATOS = r"E:/William Collegue/Fall - First Semester/Developing Macroeconomics 505 Kuttner/Memo Cesar/Survey_Household/EH2025_Persona.dta"
RUTA_SALIDA = r"E:/William Collegue/Fall - First Semester/Developing Macroeconomics 505 Kuttner/Memo Cesar/Survey_Household/resultados"
os.makedirs(RUTA_SALIDA, exist_ok=True)


# Fuentes incrustadas como texto 
matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                            "font.family": "DejaVu Sans", "font.size": 7.5})

# ---------------------------------------------------------------------
# 1. Datos: ocupados de 14 años o más
# ---------------------------------------------------------------------
df = pd.read_stata(RUTA_DATOS, convert_categoricals=False)
oc = df[(df["condact"] == 1) & (df["pet"] == 1)].copy()

# ---------------------------------------------------------------------
# 2. Mercado de trabajo e informalidad 
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
# 5. Jerarquía: grandes sectores -> actividades
# ---------------------------------------------------------------------
GRUPOS = {
    "Agriculture":   ["Crop farming", "Coca & spice crops", "Livestock", "Forestry & fishing"],
    "Mining":        ["Oil, gas & other mining", "Metal mining"],
    "Manufacturing": ["Meat & dairy", "Bakery & other food", "Beverages & tobacco",
                      "Textiles, leather & footwear", "Apparel", "Wood products", "Paper & printing",
                      "Chemicals & plastics", "Non-metallic minerals", "Metal products",
                      "Machinery & equipment", "Furniture & other mfg."],
    "Construction\n& utilities": ["Electricity, gas & water", "Building construction",
                                  "Civil engineering", "Specialized construction"],
    "Trade":         ["Vehicle trade & repair", "Wholesale trade", "Retail trade"],
    "Transport":     ["Land transport", "Storage & other transport"],
    "Hospitality":   ["Accommodation", "Food & beverage services"],
    "Business\nservices": ["Information & communication", "Financial services", "Real estate",
                           "Professional services", "Administrative services"],
    "Public\nsector": ["Public administration", "Public education", "Public health"],
    "Other\nservices": ["Private education", "Private health", "Arts & recreation",
                        "Other personal services", "Domestic work"],
}


# ---------------------------------------------------------------------
# 5. Variables para las columnas del Sankey (todas con nombres en inglés)
# ---------------------------------------------------------------------
oc["condicion"] = np.where(oc["informal"] == 1, "Informal", "Formal")

oc["pobreza"] = np.where(oc["pext0"] == 1, "Extreme poverty",
                np.where(oc["p0"] == 1, "Moderate poverty", "Non-poor"))
oc.loc[oc["p0"].isna(), "pobreza"] = np.nan

oc["sexo"] = oc["s01a_02"].map({1: "Men", 2: "Women"})
grupo_de = {a: g.replace("\n", " ") for g, acts in GRUPOS.items() for a in acts}
oc["grupo"] = oc["sec"].map(grupo_de)

# Orden de arriba hacia abajo dentro de cada columna
ORDEN_NODOS = {
    "condicion": ["Formal", "Informal"],
    "pobreza":   ["Non-poor", "Moderate poverty", "Extreme poverty"],
    "sexo":      ["Men", "Women"],
    "grupo":     [g.replace("\n", " ") for g in GRUPOS],
}
TITULO_COLUMNA = {"sexo": "Sex", "grupo": "Economic sector",
                  "condicion": "Employment status", "pobreza": "Household poverty"}

COLUMNAS = ["sexo", "grupo", "condicion", "pobreza"]     # de izquierda a derecha
ARCHIVO = "informality_sankey_sex_sector"

# ---------------------------------------------------------------------
# 6. Flujos: personas (expandidas) entre columnas vecinas
# ---------------------------------------------------------------------
d = oc.dropna(subset=COLUMNAS)
total = d["factor"].sum()
tamano = {c: d.groupby(c)["factor"].sum() for c in COLUMNAS}
flujos = []
for c1, c2 in zip(COLUMNAS[:-1], COLUMNAS[1:]):
    f = d.groupby([c1, c2])["factor"].sum().reset_index()
    f.columns = ["origen", "destino", "personas"]
    f["col"] = COLUMNAS.index(c1)
    flujos.append(f)
flujos = pd.concat(flujos)

# Tabla con los números (para el texto o para Stata/Excel)
flujos.assign(pct_del_total=100 * flujos["personas"] / total).round(1).to_csv(
    f"{RUTA_SALIDA}/{ARCHIVO}_flows.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------------
# 7. Colores: informal oscuro, formal claro (los mismos de los otros gráficos)
#    Los flujos que entran a / salen de "Formal" o "Informal" toman su color;
#    los demás van en gris claro.
# ---------------------------------------------------------------------
OSCURO, CLARO, NEUTRO = "#5c1a25", "#eba273", "#c9c6bd"
NODO, TINTA, TINTA_2 = "#3f3e3b", "#1f1f1f", "#52514e"
def color_flujo(origen, destino):
    for nombre in (destino, origen):
        if nombre == "Informal":
            return OSCURO
        if nombre == "Formal":
            return CLARO
    return NEUTRO

# ---------------------------------------------------------------------
# 8. Posiciones de los nodos
# ---------------------------------------------------------------------
ANCHO_NODO = 0.035
max_nodos = max(len(tamano[c]) for c in COLUMNAS)
HUECO = min(0.03, 0.15 / max(max_nodos - 1, 1))   # espacio vertical entre nodos
ALTO_MAX = 1 + HUECO * (max_nodos - 1)
pos = {}                     # (columna, nombre) -> [y_arriba, y_abajo]
for i, c in enumerate(COLUMNAS):
    nombres = [n for n in ORDEN_NODOS[c] if n in tamano[c].index]
    alto_total = 1 + HUECO * (len(nombres) - 1)
    y = alto_total / 2
    for n in nombres:
        h = tamano[c][n] / total
        pos[(i, n)] = [y, y - h]
        y -= h + HUECO

# ---------------------------------------------------------------------
# 9. Dibujo
# ---------------------------------------------------------------------
def banda(ax, x0, y0a, y0b, x1, y1a, y1b, col):
    """Cinta curva entre (x0, y0a..y0b) y (x1, y1a..y1b)."""
    xm = (x0 + x1) / 2
    verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a),
             (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=col, edgecolor="none", alpha=0.6))

fig, ax = plt.subplots(figsize=(9, 5.6))
ax.set_xlim(-0.62, len(COLUMNAS) - 1 + 0.80)
ax.set_ylim(-ALTO_MAX / 2 - 0.11, ALTO_MAX / 2 + 0.02)
ax.axis("off")

y_salida = {}                                   # (col, origen, destino) -> y superior del flujo
libre_sal = {k: v[0] for k, v in pos.items()}   # próximo punto libre a la derecha de cada nodo
libre_ent = {k: v[0] for k, v in pos.items()}   # próximo punto libre a la izquierda
for i in range(len(COLUMNAS) - 1):
    f = flujos[flujos["col"] == i].copy()
    f["oo"] = f["origen"].map({n: k for k, n in enumerate(ORDEN_NODOS[COLUMNAS[i]])})
    f["od"] = f["destino"].map({n: k for k, n in enumerate(ORDEN_NODOS[COLUMNAS[i + 1]])})
    f["h"] = f["personas"] / total
    # salida: dentro de cada nodo de origen, los flujos se apilan según su destino
    for _, r in f.sort_values(["oo", "od"]).iterrows():
        y_salida[(i, r.origen, r.destino)] = libre_sal[(i, r.origen)]
        libre_sal[(i, r.origen)] -= r.h
    # entrada: dentro de cada nodo de destino, se apilan según su origen
    for _, r in f.sort_values(["od", "oo"]).iterrows():
        y0 = y_salida[(i, r.origen, r.destino)]
        y1 = libre_ent[(i + 1, r.destino)]
        libre_ent[(i + 1, r.destino)] -= r.h
        banda(ax, i + ANCHO_NODO, y0, y0 - r.h, i + 1, y1, y1 - r.h, color_flujo(r.origen, r.destino))

# Nodos y etiquetas
for (i, n), (ya, yb) in pos.items():
    ax.add_patch(plt.Rectangle((i, yb), ANCHO_NODO, ya - yb, facecolor=NODO, edgecolor="none", zorder=3))
    valor = tamano[COLUMNAS[i]][n]
    texto = f"{n}\n{100 * valor / total:.1f}%  ({valor / 1e6:.2f} m)"
    if i == 0:                      # primera columna: etiqueta a la izquierda del nodo
        x, ha = i - 0.025, "right"
    else:                           # las demás: a la derecha
        x, ha = i + ANCHO_NODO + 0.025, "left"
    ax.text(x, (ya + yb) / 2, texto, ha=ha, va="center", fontsize=7.5, color=TINTA,
            linespacing=1.15, zorder=4,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75))

# Títulos de las columnas (abajo, como en el ejemplo)
for i, c in enumerate(COLUMNAS):
    ax.text(i + ANCHO_NODO / 2, -ALTO_MAX / 2 - 0.08, TITULO_COLUMNA[c], ha="center", va="bottom", fontsize=8.5,
            weight="bold", color=TINTA)

for ext, dpi in (("pdf", None), ("png", 600)):
    fig.savefig(f"{RUTA_SALIDA}/{ARCHIVO}.{ext}", dpi=dpi, bbox_inches="tight",
                pad_inches=0.05, facecolor="white")
plt.close(fig)
print(f"Listo. Archivos en: {RUTA_SALIDA}")
