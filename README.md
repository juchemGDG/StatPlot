# StatPlot

Werkzeug zur **Datenauswertung** im Unterricht: Eine CSV-Datei – etwa eine
Messreihe vom Mikrocontroller oder eine Klassenumfrage – wird als Tabelle
gezeigt, als Diagramm dargestellt, mit Kennwerten beschrieben und mit
Signifikanztests geprüft. Schwesterprojekt zum
[PAP Editor](https://github.com/juchemGDG/PAP_Editor) und
[IBD Editor](https://github.com/juchemGDG/IBD_Editor): gleiche Bedienung,
gleiches Aussehen.

StatPlot war ursprünglich die „Datenauswertung“ in
[NIT_Code](https://github.com/juchemGDG/NIT_Code). Als Web-App läuft es jetzt
auch für sich allein im Browser (z. B. auf dem iPad), als Desktop-Version und
weiterhin eingebettet in NIT_Code.

## Funktionen

- **Daten laden:** CSV-Datei öffnen oder auf das Fenster ziehen. Trennzeichen
  `;`, `,` oder Tabulator, deutsches Dezimalkomma und eine Kopfzeile werden
  automatisch erkannt; Dateien aus Excel (Windows-1252) gehen auch.
  „Beispieldaten“ lädt eine kleine Klassenumfrage.
- **Diagramme:** Streu-, Linien-, Säulen-, Balken-, Kreisdiagramm, Histogramm
  und Boxplot. Eine beliebige Spalte dient als **Kategorie**: Punkte werden je
  Kategorie eingefärbt, Säulen/Kreisstücke/Boxplots je Kategorie gebildet.
  Säulen und Balken zeigen die Anzahl oder Mittelwert/Summe/Median/Minimum/
  Maximum einer Spalte.
- **Optionen:** Ausgleichsgerade mit Gleichung und R² (Streudiagramm),
  Klassenbreite und relative Häufigkeit (Histogramm), Ausreißer nach der
  1,5·IQR-Regel und beschriftete Kennwerte (Boxplot).
- **Reiter:** Rohdaten-Tabelle, Kennwerte (n, Minimum, Quartile, Median,
  Maximum, Spannweite, Quartilsabstand, Mittelwert, σ und s – auch je Gruppe),
  Häufigkeiten (absolut, relativ, kumuliert) und Statistik-Tests.
  „Tabelle kopieren“ liefert tabulatorgetrennten Text für Tabellenkalkulationen.
- **Statistik-Tests:** Signifikanztest für eine Wahrscheinlichkeit
  (Binomialtest, wie in der Kursstufe), t-Test für eine Stichprobe, t-Test für
  zwei Stichproben (Welch, gleiche Varianzen, verbunden) – jeweils mit
  Hypothesen, p-Wert, Konfidenzintervall, Effektstärke und Entscheidung.
- **Weiterverwenden:** Export als PNG oder SVG; **Als Python-Code** zeigt ein
  Programm (`csv` + `matplotlib`, ohne pandas), das genau dieses Diagramm
  zeichnet – Brücke vom Klicken zum Programmieren.
- Touch-Bedienung (iPad), schmale Bildschirme mit Menü statt Leiste.
- Die zuletzt geladenen Daten bleiben im Browser gespeichert (nur auf diesem
  Gerät, nicht in der Einbettung).

## Rechenregeln

Wie in der Schulmathematik (Bildungsplan BW, „Daten und Zufall“):

- **Quartile** = Median der unteren bzw. oberen Hälfte der sortierten Werte; bei
  ungeradem n gehört der Median zu keiner Hälfte. (Der Python-Code nutzt
  deshalb eigene Kennwerte statt `plt.boxplot()`, das anders interpoliert.)
- **Standardabweichung:** σ teilt durch n, s (wie „sx“ am Taschenrechner) durch n − 1.
- **Histogrammklassen** sind halboffen [a; b), die letzte Klasse schließt das
  Maximum ein. Automatische Klassenbreite nach Sturges, auf 1, 2 oder 5 · 10ᵏ gerundet.
- **Binomialtest:** exakte Binomialverteilung; zweiseitig höchstens α/2 je Seite.
- **t-Verteilung** über die regularisierte unvollständige Betafunktion
  (Kettenbruch nach Lentz), Quantile per Bisektion – ohne externe Bibliotheken.

## Aufbau

| Datei | Inhalt |
|---|---|
| `web/static/stats.js` | Rechenkern ohne DOM: CSV einlesen, Kennwerte, Klassen, Tests, Python-Code-Export. Läuft auch unter Node. |
| `web/static/statplot.js` | Oberfläche: Diagramme als SVG, Tabellen, Tests, Export, Einbettung, Desktop-Anbindung |
| `web/static/statplot.css`, `index.html` | Aussehen und Gerüst (wie PAP/IBD) |
| `web/static/beispiele/` | Beispieldaten |
| `desktop/statplot_desktop.py` | Desktop-Hülle (pywebview) |
| `tests/` | Regressionstest gegen die Python-Originale aus NIT_Code |

Anzeige und SVG-Export sind dieselbe Zeichenroutine; PNG entsteht im Browser
aus diesem SVG (2-fache Auflösung).

## Tests

```bash
node tests/test_stats.js
```

Der Test vergleicht `stats.js` mit den Ergebnissen der ursprünglichen
Python-Module aus NIT_Code (Kennwerte, Klassen, Achsenteilung, Regression,
t-Verteilung, Binomial- und t-Tests, CSV-Einlesen und den erzeugten
Python-Code – Zeichen für Zeichen). Die Referenzwerte stehen in
`tests/fixtures.json` und wurden mit `tests/make_fixtures.py` aus NIT_Code
v1.10.1 erzeugt. Beim CSV-Einlesen ist StatPlot in zwei Fällen bewusst besser
als Pythons `csv.Sniffer` (deutsches Dezimalkomma ohne Kopfzeile,
Tab-Dateien mit kürzerer letzter Zeile).

## Start

```bash
bash web/start_web.sh          # Web-Version lokal: http://localhost:5001
bash start_statplot.sh         # Desktop-Version
```

## Web-Version auf den Server bringen

Die Web-Version besteht nur aus statischen Dateien. Aus `web/static/`
hochladen (z. B. nach `statplot.mint-checker.de`):

```
index.html
stats.js
statplot.js
statplot.css
favicon.svg
favicon-32.png
apple-touch-icon.png
beispiele/klassenumfrage.csv
.htaccess        <- versteckte Datei! im FTP-Programm sichtbar schalten
```

Nach jedem Update in `index.html` die Cache-Buster hochzählen
(`statplot.css?v=N`, `stats.js?v=N`, `statplot.js?v=N`) und alle Dateien
zusammen hochladen.

Der Menüpunkt „Desktop-Version“ fragt das neueste GitHub-Release ab
(`GITHUB_REPO` oben in `statplot.js`, nur bei öffentlichem Repository) und
fällt sonst auf Dateien im Ordner `downloads/` zurück.

## Desktop-Version

Die Desktop-Version zeigt dieselbe Oberfläche in einem eigenen Fenster
(`desktop/statplot_desktop.py`, [pywebview](https://pywebview.flowrl.com)) –
ohne Internet, mit nativen Dialogen zum Öffnen und Speichern. Weil der
Öffnen-Dialog den vollen Pfad kennt, steht er auch im exportierten
Python-Code.

```bash
pip install -r requirements.txt
python3 desktop/statplot_desktop.py            # eigenes Fenster
python3 desktop/statplot_desktop.py --browser  # ohne pywebview: im Browser
```

Pakete (`.dmg`, Setup-`.exe`, `.tar.gz`) baut der Workflow
`.github/workflows/build-packages.yml`: Actions → „Pakete bauen“ → Run
workflow, oder einen Tag `v1.0.0` pushen – dann hängen die Dateien am
Release. Lokal: `pyinstaller statplot.spec`. Quelle aller Icons ist
`assets/icon.svg`; `python3 packaging/make_icons.py` erzeugt daraus `.png`,
`.ico`, `.icns` und die Web-Icons (benötigt `cairosvg` und `Pillow`).

## Einbettung in andere Web-Apps (`?embed=1`)

Wie beim PAP Editor: Mit `?embed=1` im iframe erscheinen die Knöpfe „In
Projekt übernehmen“ und „Schließen“, der Hinweis auf die Desktop-Version
entfällt. Protokoll über `window.postMessage`:

| Richtung | Nachricht |
|---|---|
| App → Host | `{source:'statplot', event:'ready'}` |
| Host → App | `{target:'statplot', action:'load', csv?, name?, path?, downloads?, open?, code?, clipboard?, nit?}` |
| App → Host | `{source:'statplot', event:'save', svg, name, width, height}` |
| App → Host | `{source:'statplot', event:'exit'}` |
| App → Host | `{source:'statplot', event:'download', name, mime, blob}` |
| App → Host | `{source:'statplot', event:'open'}` |
| App → Host | `{source:'statplot', event:'code', code, title}` |
| App → Host | `{source:'statplot', event:'copy', text}` |

Die Schalter in `load` beschreiben, was der Host kann:

- `csv`, `name`, `path`: Daten laden (jede weitere `load`-Nachricht mit `csv`
  lädt neue Daten; `path` erscheint im Python-Code).
- `downloads:true`: Dateien (PNG, SVG, `.py`) gehen als `download` an den Host
  statt als Browser-Download – Browser blockieren Downloads im iframe oft.
- `open:true`: „CSV öffnen“ schickt `open`; der Host zeigt seinen Dateidialog
  und antwortet mit `load` + `csv`.
- `code:true`: Im Code-Dialog erscheint „In neuen Editor-Tab“ (`code`-Nachricht).
- `clipboard:true`: Kopieren läuft über den Host (`copy`-Nachricht).
- `nit:true`: Der Python-Code verweist auf NIT_Codes Paket-Menü.

„In Projekt übernehmen“ schickt das Diagramm als SVG; gerastert wird beim Host
(im Browser: SVG → `<img>` → Canvas → PNG).

Die App nimmt nur Nachrichten ihres Eltern-Fensters an und schickt Daten nur
an dessen Origin. Der Host sollte umgekehrt `event.origin` und `event.source`
prüfen.
