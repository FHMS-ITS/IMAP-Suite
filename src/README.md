# Entwicklerinformationen
## ImapSuite.py
Startet das Tool ImapSuite.
## imap
Dieser Ordner enthält alle Imap-spezifischen Klassen und -funktionen.
### IMAP4rev1Classes.py
In dieser Datei sind die Klassendefinitonen für den lark-Transformer. Die Objekte dieser Klassen können mit der str(...)-Funktion serialisiert werden. Der String entspricht dabei einer Imap-Nachricht, die zu einem Peer übertragen werden kann.
### Imap4rev1Parser.py
In dieser Datei wird die Imap4rev1Parser Klasse definiert. In dieser Klasse findet man die verwendete Grammatik und selbst definierte Exceptions, die beim Parsen geraised werden könnten.
Als Parsing Library wird lark-parser verwendet. Der Konstruktor nimmt als String die Regeln an, die als Startregel verwendet werden soll. So kann ohne Änderung der Grammatik an verschiedenen Stellen gestartet werden.
### Imap4rev1StateMachine.py
Die Klasse ImapMachine ist eine State-Machine die auf der Library python-statemachine basiert. Der Übergangsautomat kann in der README.md im Rootverzeichnis eingesehen werden.
### Imap4rev1Transformer.py
In dieser Datei wird der lark-Transformer für die verwendete Grammatik implementiert. Für jede Regel der Grammatik wurde eine Funktion implementiert, die angibt, wie der resultierende Parsing-Tree zu shapen ist. Dabei wird aus dem Parsing-Tree ein Objekt der entsprechenden Klasse der Regel erstellt. 
### ImapSession.py
Die Datei implementiert mehrere Klassen, die essentiell für den Proxy sind.

Die Klasse ImapSession wird für jede eingehende Verbindung instantiiert. Sie verwaltet unter anderem Verbindungsinformationen zu den beiden Peers, legt die Historie des Commands und Responses an, stellt Parser und Transformer bereit und übernimmt die Kommunikation mit den Peers. Für die Funktionen wurden möglichst sprechende Namen verwendet:
- def history...(...): sind Funktionen, die die Historie bearbeiten. Es können neue Commands hinzugefügt werden, Responses anhand der Tag zu bestehenden Command-Einträgen hinzugefügt werden, sowie bestehende Comands und Responses erweitert werden.
- def read...(...): sind Funktionen die von den Peers lesen und eine Liste entsprechender Parsing-Trees zurückgeben, sollte das Parsen erfolgreich gewesen sein. Die Funktionen geben None zurück, wenn die empfangenen Daten (noch) nicht geparsed werden konnten.
- def send...(...): encodiert und versendet die übergebenen Argumente an den entsprechenden Peer.
- def stateMachineTransit...(...): triggert Transitions in der StateMachine für diese Session. 

Die Klassen ImapGreeting, ImapCommand und ImapResponse werden für die Historie und die GUI verwendet. Dazu halten sie verschiedene Arten einer Nachricht vor (raw, Parsing-Tree, Objekt) und stellen diverse getter- und setter-Methoden bereit.

### imap_proxy.py
Diese Datei stellt Funktionen für die Hauptfunktionalität des Proxys bereit.
##### def startProxy(...):
Die Funktion startet den MainLoop des Proxys. Für jede eingehende Verbindung wird ein neuer Thread erstellt, der diese ImapSession verwaltet.
##### def handleConnection(...):
Diese Funktion startet den Loop für jede einzelne Session. Anhand der verschiedenen States der ImapSession verändert sich das Verhalten des Proxys. 

## qt_generated
In diesem Ordner landen die aus .ui-Dateien generierten Python-Klassen für die GUI.
Die Klassen können mit folgendem Befehl generiert werden:

```bash
pyuic5 -x qt_ui/qt-gui.ui -o qt_generated/gui.py && pyuic5 -x qt_ui/qt-imapSession.ui -o qt_generated/gui_imapSession.py && pyuic5 -x qt_ui/qt-pendingDialog.ui -o qt_generated/qui_pendingDialog.py
```

Diese Klassen sollten nicht verändert werden, da alle Änderungen bei der Neugenerierung überschrieben werden!
## qt_implementation
Dies sind die Implementierungen der generierten Qt-Klassen. Die Klassen erben jeweils von den generierten Klassen.
## qt_ui
.ui-Dateien, die bspw. mit dem Qt-Designer bearbeitet werden können. Änderungen werden erst übernommen, wenn die Dateien im Ordner qt_generated neu generiert wurden.
## qt_utils
Der Ordner enthält Hilfsklassen und -funktionen, die für die Darstellung und die Funktionalität der GUI verwendet werden.
### qt_QThreads.py
Diese Datei beinhaltet alle definierten QThreads, die aufgrund von diversen User-Aktionen gestartet werden. Die Namen des Klassen wurden sprechend gewählt.
### qt_ViewModels.py
Diese Datei enthält verschiedene Klassen, die als Schnittstelle zwischen den rein internen Klassen und der GUI dienen. Sie bereiten die intern gespeicherten Daten so auf, dass die GUI diese anzeigen kann.
### qt_utils.py
Hier werden zwei Hilfsfunktionen definiert, die interne Daten in eine Form bringen, sodass sie von den ViewModels verarbeitet werden können.
## sockets
In diesem Ordner werden UNIX-Sockets angelegt, die für das injecten von Commands in eine bestehende Verbindung verwendet werden. Sollte es Probleme mit dem injecten von Commands geben, sollte man vor Start des Tools alle Dateien in diesem Ordner löschen.
## utils
Der Ordner enthält diverse Skripte, die Hilfsklassen und -funktionen bereitstellen, die keinen direkten Bezug zur GUI haben.
### AbstractParser.py
Abstrakte Klasse, die eine Hilfsfunktion definiert, die jeder verwendete Parser benötigt.
### abnf-to-lark.py
Dies ist ein Skript, dass eine Grammatik, die in der ABNF vorliegt, in eine Form unwandelt, die der lark-parser akzeptiert. In speziellen Fällen ist jedoch eine händische Nachbearbeitung notwendig. 
### imap_constants-py
In dieser Datei werden diverse Konstanten definiert, die im Tool häufig referenziert werden. Unter anderem kann an dieser Stelle die verwendete Kodierung geändert werden. Zur Zeit ist latin1 eingestellt, das die Grammatik Zeichen erlaubt, die nicht in ASCII vorhanden sind. UTF-8 kann nicht verwendet werden, da bei der Kodierung unter Umständen Bytes hinzugefügt werden (bspw. beim Zeichen 'ü').
### parse_response.py
Dieses Skript hat nichts mit dem Tool zutun, sondern dient lediglich als manuelles Testskript.
### parser_utils.py
In diesem Skript wird eine Funktion implementiert, die das Streaming der Eingabestrings in den lark-parser ermöglicht. Es wird eine Liste aller geparsten Nachrichten und der "Rest", der nicht geparsed werden konnte, zurückgegeben. Wenn nichts geparsed werden konnte, wird die komplette Eingabe als Rest zurückgegeben. 
