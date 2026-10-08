# Angewandtes Quantencomputing Projektlabor

Dieses Repository enthält Laborübungen in Form von Jupyter Notebooks.
Um die Notebooks auszuführen, müssen Sie zunächst eine geeignete Python-Umgebung einrichten.

## Voraussetzungen

Bitte stellen Sie sicher, dass die folgende Software installiert ist:

-   Python ≥ 3.10
-   pip (wird normalerweise zusammen mit Python installiert)
-   Optional, aber empfohlen: Git (zum Herunterladen der aktuellen Kursmaterialien)
-   Optional, aber empfohlen: VS Code oder PyCharm Professional (zum Anzeigen, Ausführen und Bearbeiten der Notebooks)

Sie können Ihre Installation mit folgendem Befehl überprüfen:

``` bash
python --version
```

Möglicherweise müssen Sie den korrekten Pfad zu Ihrer Python-Installation angeben.
Wenn mehrere Python-Versionen installiert sind, muss Python möglicherweise mit folgendem Befehl aufgerufen werden:

``` bash
python3 --version
```

oder

``` bash
python3.10 --version
```

## Repository klonen

Um das Repository zu klonen, kopieren Sie den unter `Clone` angezeigten Link und führen Sie folgende Befehle aus:

``` bash
git clone <repository-url>
cd <repository-name>
```

Alternativ kann das Repository als ZIP-Datei von GitLab oder ILIAS heruntergeladen und anschließend entpackt werden.

## Installation mit venv (empfohlen)

Die empfohlene Methode ist die Verwendung einer virtuellen Umgebung mit `venv` (Standard seit Python 3.3).

### 1. Virtuelle Umgebung erstellen

#### macOS / Linux

``` bash
python3 -m venv .venv
```

#### Windows (PowerShell)

``` powershell
python -m venv .venv
```

Dadurch wird im Projektverzeichnis ein Ordner mit dem Namen `.venv` erstellt.

### 2. Umgebung aktivieren

#### macOS / Linux

``` bash
source .venv/bin/activate
```

#### Windows (PowerShell)

``` powershell
.\.venv\Scripts\Activate.ps1
```

Falls eine Fehlermeldung bezüglich der Ausführungsrichtlinie angezeigt wird:

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Abhängigkeiten installieren

Nach dem Aktivieren der Umgebung:

``` bash
pip install --upgrade pip
pip install -r requirements.txt
```

Im Laufe des Kurses können sich die Abhängigkeiten ändern. In diesem Fall führen Sie einfach erneut

``` bash
pip install -r requirements.txt
```

aus, nachdem die Datei `requirements.txt` aktualisiert wurde.

## Alternative: Installation mit Conda

Falls Sie Anaconda oder Miniconda verwenden:

### Umgebung erstellen

``` bash
conda create -n course python=3.11
```

### Aktivieren

``` bash
conda activate course
```

### Abhängigkeiten installieren

``` bash
pip install -r requirements.txt
```

## Notebooks ausführen

Es gibt mehrere Möglichkeiten, die Notebooks zu öffnen und auszuführen.

### 1. Mit Visual Studio Code (empfohlen)

1.  Starten Sie VS Code.
2.  Wählen Sie „Open Folder“ → und anschließend den Projektordner.
3.  Falls erforderlich: Installieren Sie die Python-Erweiterung.
4.  Wählen Sie unten rechts den Python-Interpreter (`.venv`) aus.

Anschließend können Sie ein Notebook durch Anklicken öffnen.
Zellen können über das Play-Symbol oder mit **Shift + Enter** ausgeführt werden.

Falls die Umgebung nicht automatisch erkannt wird:

-   `Ctrl + Shift + P`
-   „Python: Select Interpreter“
-   `.venv` auswählen

### 2. Mit PyCharm Professional

JetBrains-IDEs unterstützen Jupyter Notebooks direkt.

Vorgehen:

1.  Öffnen Sie das Projekt.
2.  Wählen Sie unter *Settings → Python Interpreter* die Umgebung `.venv` aus.
3.  Öffnen Sie die Notebook-Datei (`.ipynb`).
4.  Führen Sie Zellen über die Play-Schaltfläche oder mit **Shift + Enter** aus.

Hinweis:
Die Community Edition von PyCharm unterstützt Jupyter Notebooks
nicht direkt.
Sie benötigen die lizenzierte Version PyCharm Professional, die Sie
über Ihren Studierenden-Account erhalten können.

### 3. Mit JupyterLab

Nach dem Aktivieren der Umgebung:

``` bash
jupyter lab
```

Es öffnet sich automatisch ein Browserfenster.
Dort können Sie das gewünschte Notebook (`.ipynb`) öffnen und Zellen mit **Shift + Enter** ausführen.

Falls `jupyter lab` nicht gefunden wird, installieren Sie es zunächst:

``` bash
pip install jupyterlab
```

## Umgebung deaktivieren

Geben Sie im Terminal folgenden Befehl ein:

``` bash
deactivate
```
