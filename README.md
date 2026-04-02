# Projektstruktur – Zuverlässigkeits-Hausübung

Dieses Repository enthält die Lösung der Hausübung zur **probabilistischen Zuverlässigkeitsanalyse einer Freileitungs-Erdkabel-Übertragungsstrecke**.

Ziel ist eine saubere, modulare und nachvollziehbare Implementierung in Python.

---

## 📁 Projektstruktur

```text
zuverlaessigkeit-aufgabe/

.venv/              # virtuelle Umgebung (nicht im Repo)
src/
    components.py   # Definition von Klassen und Grundstrukturen
    datasets.py     # konkrete Datensätze aus der Aufgabenstellung
    topology.py     # Modellierung der Netzstrukturen
    reliability.py  # Zuverlässigkeitsberechnung (NV, Zustände)
    economics.py    # wirtschaftliche Bewertung
    main.py         # Einstiegspunkt für die Berechnung

data/               # optionale externe Daten
docs/               # zusätzliche Dokumentation
notebooks/          # Jupyter Notebooks für Tests/Exploration
results/            # Ergebnisse / Outputs

README.md
requirements.txt
.gitignore
```

---

## 🧠 Grundprinzip der Struktur

Das Projekt folgt einer klaren Trennung von:

* **Struktur (Modelle)**
* **Daten (Aufgabenstellung)**
* **Berechnung (Methoden)**
* **Anwendung (Ausführung)**

---

## 🔧 Dateien im Detail

### `components.py` → Struktur / Modelle

Enthält die grundlegenden Klassen, z. B.:

* Datensatzstruktur (`ReliabilityDataset`)
* später: Komponenten (Leitung, Kabel, Schalter)

👉 Antwortet auf die Frage:
**„Wie ist ein Systemelement oder Datensatz aufgebaut?“**

---

### `datasets.py` → konkrete Werte

Enthält die tatsächlichen Zahlen aus der Aufgabenstellung:

* Datensatz 1
* Datensatz 2
* Datensatz 3

👉 Antwortet auf die Frage:
**„Welche konkreten Parameter werden verwendet?“**

---

### `topology.py` → Netzlogik

Beschreibt die beiden Topologien:

* Topologie 1 (einfache KÜS)
* Topologie 2 (mit Schaltanlage)

👉 Enthält Regeln wie:

* Serie / Parallel
* Redundanzen
* verfügbare Kapazität je Zustand

---

### `reliability.py` → Zuverlässigkeitsrechnung

Hier wird implementiert:

* Nichtverfügbarkeit (NV)
* Zustandswahrscheinlichkeiten
* Kombination von Komponenten

👉 Antwortet auf die Frage:
**„Wie wahrscheinlich ist welcher Systemzustand?“**

---

### `economics.py` → Kostenmodell

Berechnet:

* nicht gelieferte Energie
* Kosten durch Ausfälle
* Annuität der Investitionen

👉 Antwortet auf die Frage:
**„Welche Topologie ist wirtschaftlich optimal?“**

---

### `main.py` → Ausführung

* lädt Datensätze
* erstellt Modelle
* führt Berechnungen aus
* gibt Ergebnisse aus

👉 Einstiegspunkt des Projekts

---

## 🚫 Virtuelle Umgebung (.venv)

Die virtuelle Umgebung liegt im Projektordner:

```text
.venv/
```

Wird aber **nicht in Git gespeichert** (siehe `.gitignore`).

Abhängigkeiten werden stattdessen über `requirements.txt` verwaltet.

---

## 🧠 Warum diese Struktur?

Diese Trennung ist wichtig, weil:

* die Hausübung mehrere Datensätze verwendet
* Modelle wiederverwendbar bleiben
* Berechnungen nachvollziehbar sind
* Fehler leichter gefunden werden können
* Erweiterungen einfacher möglich sind

---

## ❌ Typischer Fehler

Alles in eine Datei schreiben:

```python
# NICHT EMPFOHLEN
class Dataset:
    ...

dataset_1 = ...
dataset_2 = ...
```

👉 führt schnell zu unübersichtlichem Code

---

## ✅ Mentales Modell

* `components.py` → **Theorie / Struktur**
* `datasets.py` → **Aufgabenstellung / Zahlen**
* `reliability.py` → **Mathematik**
* `topology.py` → **Systemlogik**
* `economics.py` → **Kosten**
* `main.py` → **Ausführung**

---

## 🚀 Nächster Schritt

Als nächstes wird implementiert:

1. Datensätze (`datasets.py`)
2. Komponentenmodell (`components.py`)
3. erste Berechnung der Nichtverfügbarkeit

Damit entsteht ein erstes lauffähiges Grundgerüst.

