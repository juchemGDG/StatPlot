"""Erzeugt tests/fixtures.json aus den Python-Originalen in NIT_Code.

StatPlot ist eine Portierung der Datenauswertung aus NIT_Code (csv_stats.py,
stat_tests.py, csv_codegen.py, read_csv/_nice_ticks aus csv_plot.py, Stand
NIT_Code v1.10.1). Dieses Skript ruft die Python-Funktionen mit festen Eingaben
auf und speichert die Ergebnisse; tests/test_stats.js vergleicht stats.js damit.

    python3 tests/make_fixtures.py /pfad/zu/NIT_Code      # (Tag v1.10.1)

Nur nötig, wenn neue Testfälle dazukommen – fixtures.json liegt im Repository.
"""
import json
import math
import os
import random
import sys
import tempfile

if len(sys.argv) < 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.abspath(sys.argv[1]))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from nit_code import csv_stats as S          # noqa: E402
from nit_code import stat_tests as T         # noqa: E402
from nit_code.csv_codegen import generate_code   # noqa: E402
from nit_code.csv_plot import _nice_ticks, read_csv   # noqa: E402 (braucht PyQt6)

HERE = os.path.dirname(os.path.abspath(__file__))
rnd = random.Random(42)


def clean(v):
    """JSON-tauglich: Tupel → Listen, nan/inf → Text."""
    if isinstance(v, float) and not math.isfinite(v):
        return str(v)
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    return v


datasets = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [2, 4, 4, 4, 5, 5, 7, 9],
    [3.5],
    [10, 20],
    [152.5, 160, 171.2, 168, 149.9, 180.3, 175, 158.4, 163, 177.7, 169.1],
    [round(rnd.gauss(50, 12), 2) for _ in range(57)],
    [rnd.randint(0, 6) for _ in range(40)],
    [0.001, 0.0005, 0.002, 0.0031],
    [-5, -2.5, 0, 2.5, 5, 100],
]

fx = {}

fx["fmt_num"] = []
for v in [0, 1, -3, 2.5, 3.14159265, 1234.5678, 0.000123456, 1e-5, 2.5e-7, 1234567.891,
          9.87654e9, -0.5, 1e12 + 0.5, 0.1 + 0.2, 100.0, 42.000001, 0.0012345, 123456.789]:
    for d in (1, 2, 3, 4):
        fx["fmt_num"].append([v, d, S.fmt_num(v, d)])
fx["fmt_num"].append([None, 4, S.fmt_num(None)])

fx["describe"] = [[d, clean(S.describe(d))] for d in datasets]
fx["quartiles"] = [[d, clean(S.quartiles(d))] for d in datasets]
fx["whiskers"] = []
for d in datasets:
    q1, _, q3 = S.quartiles(d)
    fx["whiskers"].append([d, clean(S.tukey_whiskers(d, q1, q3))])

fx["histogram"] = []
for d in datasets:
    for w in (0, 0.5, 1, 2.5, 10):
        fx["histogram"].append([d, w, clean(S.histogram_bins(d, w))])

fx["nice_ticks"] = []
for lo, hi, cnt, pad in [(0, 10, 5, 0), (0.3, 7.9, 5, 0.03), (-12, 260, 5, 0), (5, 5, 5, 0),
                         (149.9, 180.3, 5, 0.03), (0, 0.0042, 5, 0), (0, 37, 8, 0),
                         (1e6, 3.5e6, 5, 0.03)]:
    fx["nice_ticks"].append([lo, hi, cnt, pad, clean(_nice_ticks(lo, hi, cnt, pad))])

fx["regression"] = []
for xs, ys in [([1, 2, 3, 4], [2, 4.1, 5.9, 8.2]), ([0, 1, 2], [5, 5, 5]),
               ([1.5, 2.5, 3.1, 4.9, 6.0], [10, 7, 6.5, 2, -1])]:
    reg = S.linear_regression(xs, ys)
    fx["regression"].append([xs, ys, clean(reg), S.regression_text(*reg)])

fx["cumulate"] = [[[["a", 3], ["b", 5], ["c", 2]], clean(S.cumulate([("a", 3), ("b", 5), ("c", 2)]))]]

fx["t_cdf"] = [[t, df, T.t_cdf(t, df)] for t in (-3, -1.2, 0, 0.5, 2.1, 4) for df in (1, 2.5, 7, 30, 120)]
fx["t_ppf"] = [[p, df, T.t_ppf(p, df)] for p in (0.025, 0.05, 0.5, 0.95, 0.975, 0.995) for df in (1, 4, 10.3, 29, 200)]

fx["binomial"] = []
for n, k, p0 in [(100, 62, 0.5), (50, 9, 0.3), (20, 20, 0.7), (1, 0, 0.5), (500, 180, 0.4), (12, 3, 0.1)]:
    for alt in ("two-sided", "less", "greater"):
        for alpha in (0.05, 0.01):
            fx["binomial"].append([n, k, p0, alt, alpha, clean(T.binomial_test(n, k, p0, alt, alpha))])

fx["one_t"] = []
fx["two_t"] = []
fx["paired_t"] = []
for alt in ("two-sided", "less", "greater"):
    for d in datasets[4:7]:
        fx["one_t"].append([d, 55.0, alt, 0.05, clean(T.one_sample_t(d, 55.0, alt, 0.05))])
    for eq in (False, True):
        fx["two_t"].append([datasets[4], datasets[5], eq, alt, 0.05,
                            clean(T.two_sample_t(datasets[4], datasets[5], eq, alt, 0.05))])
    a = datasets[5][:20]
    b = [x + rnd.gauss(1.5, 3) for x in a]
    fx["paired_t"].append([a, b, alt, 0.1, clean(T.paired_t(a, b, alt, 0.1))])

# CSV einlesen (read_csv braucht eine Datei)
csv_texts = [
    "Name;Größe;Gewicht\nAnna;152,5;45\nBen;160;51,2\n\nCem;171,2;60\n",
    "x,y\n1,2\n2,4.5\n3,6\n",
    "1;2,5;3\n4;5,5;6\n",
    "a\tb\tc\n1\t2\t3\n4\t5\n",
    '"Name, voll";Wert\n"Müller, Max";3\n"O""Brien";4\n',
    "\ufeffKlasse;Note\n7a;2\n7b;3\n7a;1\n",
    "Messung,Spannung,Strom\n1,0.5,0.01\n2,1.0,0.021\n3,1.5,0.029\n",
]
fx["read_csv"] = []
for text in csv_texts:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
        f.write(text)
        path = f.name
    try:
        headers, rows, info = read_csv(path)
    finally:
        os.unlink(path)
    fx["read_csv"].append([text, headers, rows, info])

# Python-Code-Export
H = ["Nr", "Klasse", "Größe (cm)", "Gewicht (kg)", "Geschlecht"]
base = dict(path="/home/schule/Messung \"neu\".csv", delimiter=";", header=True, headers=H,
            x_col=2, y_col=3, value_col=None, cat_col=None, numeric_categories=False,
            agg="Mittelwert", bins=[], relative=False, regression=False, outliers=False)
specs = []
for t in ("Streudiagramm", "Liniendiagramm"):
    for cat in (None, 4):
        for reg in (False, True):
            specs.append(dict(base, chart_type=t, cat_col=cat, regression=reg,
                              path=r"C:\Users\sus\Desktop\daten.csv"))
for t in ("Säulendiagramm", "Balkendiagramm", "Kreisdiagramm"):
    for val in (None, 3):
        for agg in ("Mittelwert", "Summe", "Median", "Minimum", "Maximum"):
            specs.append(dict(base, chart_type=t, cat_col=1, value_col=val, agg=agg,
                              numeric_categories=(agg == "Median")))
for rel in (False, True):
    specs.append(dict(base, chart_type="Histogramm", cat_col=1, relative=rel,
                      bins=[140, 145, 150, 155.5, 0.1 + 0.2, 1e-5, 160]))
specs.append(dict(base, chart_type="Histogramm", bins=list(range(0, 30, 2)), header=False,
                  delimiter="\t", path="daten.csv"))
for cat in (None, 1):
    for out in (False, True):
        specs.append(dict(base, chart_type="Boxplot", cat_col=cat, outliers=out, path="/tmp/x\\"))
fx["codegen"] = [[s, generate_code(s)] for s in specs]

with open(os.path.join(HERE, "fixtures.json"), "w", encoding="utf-8") as f:
    json.dump(fx, f, ensure_ascii=False, indent=0)
print(f"fixtures.json: {sum(len(v) for v in fx.values())} Fälle")
