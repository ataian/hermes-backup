# Strategie: Hermes-Home und zugehörige Hindsight-Datenbank

## Erst Bestand, dann Sicherungsweg

Bei einer **frischen** Installation können Datenbanken erst nach der ersten
Benutzung entstehen. Bei einer **gewachsenen** Installation können Profile,
Plugins und ältere Versionen zusätzliche Speicherorte angelegt haben.
Fehlende Beispiele nicht erzeugen; gefundene unbekannte Dateien nicht still ignorieren.

1. Tatsächliches Hermes-Home und freigegebene Profile bestimmen. Eine Installation
   kann `~/.hermes` oder ein anderes durch `HERMES_HOME` bestimmtes Verzeichnis sein.
   Das bedeutet keine Erlaubnis, das gesamte Benutzer-Home zu durchsuchen.
2. Bestehende Backupskripte, Jobdefinitionen, `.gitignore`, Git-Index und Zielpfade
   lesend prüfen. Etablierte Sicherungen nicht ersetzen oder doppelt anlegen.
3. Im vereinbarten Quellbaum reguläre Dateien inventarisieren. Symlinks und Mounts
   als eigene Befunde führen; keine externen Ziele verfolgen. Andere Profile nur
   im freigegebenen Umfang berücksichtigen. Caches, Installationsbäume, `.git`,
   `node_modules` und virtuelle Umgebungen nicht unkontrolliert rekursiv einlesen.
   Bei dort gefundenen Nutzerdaten die Grenze gezielt prüfen statt pauschal verwerfen.
4. Nach `.db`, `.sqlite`, `.sqlite3` und weiteren DB-Kandidaten suchen. Zusätzlich
   Speicherorte aus tatsächlich installierten Plugins und eigener Automation
   ermitteln, damit auch abweichende Dateinamen erfasst werden. Für DB-Kandidaten
   genügt zunächst der Header `SQLite format 3\0`; keine Datensätze ausgeben.
   Endung allein beweist weder SQLite noch Wiederherstellbarkeit. Verschlüsselte,
   unbekannte oder nicht lesbare Kandidaten als offene Abdeckung melden.
5. Credential-Kandidaten nach [Credential-Regeln](credentials.md) getrennt aufnehmen.
   Nur Pfade/Typen/Eigentümer/Rechte berichten, keine Werte. Das Einlesen zum später
   freigegebenen Archivieren ist von einer Inhaltsausgabe zu unterscheiden.
6. Jede relevante Datei bekommt einen verifizierten Sicherungsweg. Nur nachweislich
   regenerierbare oder ausdrücklich nicht benötigte Inhalte begründet ausschließen;
   unbekannt oder ignoriert bedeutet nicht entbehrlich.
   Nach Updates/neuen Plugins die Bestandsprüfung wiederholen und Quellenlisten
   neu abnehmen. Ein festes Laufskript entdeckt neue Dateien nicht automatisch.

## Quellenmatrix — Hinweise, keine feste Allowlist

| Gefundener Inhalt | Sicherungsweg |
|---|---|
| SOUL, Agentenregeln, eigene Skills/Referenzen, Skripte, Memories, Pläne | Täglicher lokaler Git-Commit, optionaler Push |
| Konfigurationen, Profildefinitionen, Cron-Definitionen | Git nur nach Secret-Prüfung; sonst geschützter Dateisnapshot/Credentials |
| SQLite: etwa `state.db`, Projekt-/Board-DBs, `cron/*.db`, Plugin-DBs | Konsistenter DB-Dump, nicht Git und nicht rohe Dateikopie |
| `.env`, Auth-/Token-Dateien, sensitive Plugin-Konfiguration | Eigenes Credential-Skript, niemals Git |
| Benötigte Sessions, Anhänge oder sonstige Nutzdaten, die Git ausschließt | Separater geschützter Dateisnapshot innerhalb des vereinbarten Quellbaums |
| `.git`-Metadaten | Bestandteil des Git-Sicherungswegs; keine zusätzliche Sicherung und keine Abdeckungslücke |
| Installationen, Cache, Logs, PID-/Lock-Dateien | Nur bei begründetem Wiederherstellungsbedarf; sonst regenerierbar |
| Zugehörige Hindsight-Datenbank, gegebenenfalls extern | Eigener, an die tatsächliche Betriebsart angepasster DB-Backup-Schritt |
| Andere Daten außerhalb des Hermes-Homes | Außerhalb dieses Skills, keine Aufnahme |

**Hindsight:** Eine `hindsight/config.json` innerhalb des Hermes-Homes kann
Credentials enthalten und gehört dann zur separaten Sicherung. Die zugehörige
Hindsight-Datenbank ist die einzige Ausnahme außerhalb des Hermes-Homes. Den
[Hindsight-Schritt](hindsight.md) laden; Speicherort, Betriebsart, Zugriff und
Zuständigkeit selbst ermitteln oder gezielt erfragen. Keine lokale Standardtopologie
unterstellen und nicht automatisch alle Banken einer gemeinsam genutzten DB sichern.
Auch vorhandene SSH-Schlüssel außerhalb von `.hermes`, externe Vaults und Projekte
werden nicht aufgenommen. Eine SQLite-Datei innerhalb eines freigegebenen
Plugin-Verzeichnisses bleibt hingegen ein DB-Kandidat.

## .gitignore nach .hermes kopieren — mit Bestandsprüfung

[templates/gitignore.hermes](../templates/gitignore.hermes) ist die vom Benutzer
angepasste Referenz auf Basis einer gewachsenen Installation, keine universelle
fertige Zielkonfiguration. Verbliebene historische Pfade, Kommentare und Ausnahmen
begründen weder Zugriff
noch ein Sicherungsziel bei einem anderen Benutzer.

- Frisch, ohne vorhandene `.gitignore`: Vorlage prüfen, dann bei Einrichtungsauftrag
  nach `<HERMES_HOME>/.gitignore` kopieren und lokale Besonderheiten gezielt anpassen.
- Bestehend: vorhandene Datei sichern, Diff bilden und Regeln gezielt zusammenführen.
  Eigene Ausnahmen, verschachtelte `.gitignore` und bereits etablierte Ablagen erhalten.
- Die aktuelle Paketvorlage bei Zielnutzung nicht verändern; Anpassungen gehören in die Zielkopie.
- Breite Muster wie `state/`, `sessions/`, `tools/`, `bin/`, `*.db*` und
  `profiles/*/home/` gegen tatsächliche Nutzdaten prüfen. Eigene Skripte/Tools
  dürfen nicht ohne anderen Sicherungsweg verschwinden.
- Die Vorlage deckt nicht jede sensitive Plugin-Datei ab: insbesondere
  `hindsight/config.json` ist nicht generell ausgeschlossen. Für jede konkret
  gefundene Credential-Datei eine wirksame Ignore-Regel ergänzen; mögliche Secrets
  in normalen Konfigurationen separat berücksichtigen.
- `.gitignore` wirkt **nicht rückwirkend** auf bereits getrackte Dateien oder
  Git-Historie. `git ls-files` und `git check-ignore --no-index -v -- <relativer-pfad>`
  prüfen. Befunde ohne Inhalte melden. Indexbereinigung, History-Rewrite oder
  Credential-Rotation sind keine automatische Nebenaktion.
- Der tägliche lokale Commit im Hermes-Home ist Pflicht, ein Push ist optional.
  [Git/Cron](git-cron.md) verbindlich laden: Remote-Wunsch abfragen, bei Ja Ziel
  vom Benutzer nennen lassen, Schreibzugriff prüfen und bei der Einrichtung helfen.
  Sicher stagen und täglich committen; keine pauschale Aufnahme sensibler Dateien.
  Ein Hermes-Konfigurationsbackup gehört normalerweise in ein **privates** Ziel;
  das öffentliche Repository dieses Skills enthält nur das Werkzeug, keine Backups.

## Ablage und Lebenszyklus

- Vorschlag: `~/backups/hermes/YYYY-MM-DD_HHMMSS_ffffff/`.
- Pro Lauf frisches Verzeichnis mit lokalem Datum, Uhrzeit und Mikrosekunden;
  Zeitzone mit UTC-Offset im Manifest dokumentieren. Gleiche Sekunde überschreibt
  nichts. Jede Skriptausführung erzeugt einen eigenen Satz.
- Verzeichnisse `0700`, Dateien `0600`, eigener Benutzer; ausreichenden freien
  Speicher prüfen. Ziel außerhalb des Quellbaums, keine Symlinks oder gemeinsamen
  fremd beschreibbaren Arbeitsbereiche. Backupdaten nicht in dieses Skill-Repo legen.
- DB-Lauf: komprimierte Snapshots unter `db/<relativer-quellpfad>.gz`.
- Credential-Lauf: `credentials.tar.gz` und Manifest im eigenen Laufverzeichnis.
- `INCOMPLETE.json` beim Start, `COMPLETE.json` erst nach vollständiger Prüfung;
  Fehler liefern Exit ungleich null. Nicht allein nach Zeitstempel oder Dateigröße
  über Erfolg entscheiden. Erfolgreiche Teildumps ersetzen keinen vollständigen Satz.
- Standardvorlagen löschen keine alten Backups. **Aufbewahrungsdauer ausdrücklich
  abfragen; Vorschlag: 30 Tage.** Erst den bestätigten Wert verwenden. Rotation nur
  nach passender Freigabe, ausschließlich für eigene vollständige Sätze nach neuem
  Erfolg, unter Erhalt des letzten guten Satzes. Fremde/unklare/angefangene Sätze behalten.
- **Cronzeit ausdrücklich abfragen; Vorschlag: täglich 05:00 Uhr morgens in der
  ermittelten lokalen Zeitzone.** Zeitzone anzeigen, beide Antworten dokumentieren.
  Bestehende Jobs benennen und eine gewünschte Änderung abstimmen, keine Doppeljobs.
  Fehlerzustellung und native Scheduler-Syntax vor Einrichtung prüfen. Die Antwort
  auf die Uhrzeit allein ist keine Freigabe für Löschungen oder Infrastrukturänderungen.
- Der tägliche Orchestrator läuft als `no_agent=true`-Skriptjob vollständig ohne LLM.
  Er enthält immer den lokalen Git-Commit, den optional bestätigten Push und alle
  erforderlichen Sicherungsschritte. Teilerfolge getrennt erfassen; ein Fehler
  verhindert nicht die unabhängigen anderen Backups, aber die Gesamterfolgsmeldung.
  Die Snapshot-Retention kürzt weder Git-Historie noch Remote-Branches.
- **Off-Host:** Gleiches System schützt nicht vor Hostverlust. Benutzer muss eine
  geschützte externe Kopie der nicht in Git enthaltenen Daten organisieren. Der
  optionale Git-Push samt Zugangseinrichtung ist Teil dieses Skills, eine zusätzliche
  Snapshot-Spiegelung oder Netzwerk-/Tunneländerung nicht. Zugangsdaten vor externer
  Übertragung angemessen verschlüsseln.

## Verbindliche Backupvollständigkeit

**Keine erfolgreiche Gesamtabnahme bei ungesicherten relevanten Daten.**

- Ein verifizierter Commit deckt die darin enthaltenen Dateien ab; ein zusätzliches Backup ist dafür nicht erforderlich.
  Separate Dumps/Backups sind für relevante Daten außerhalb dieses Git-Sicherungswegs
  vorgesehen. `.git` selbst bleibt von Dateisnapshots und der Suche nach ungedeckten
  Nutzdaten ausgeschlossen; fehlende Git-Bundles oder `.git`-Kopien sind keine Abnahmelücke.
- Inventar gegen tatsächlich erzeugte Sicherungsartefakte abgleichen: für jede
  relevante Datei Quellpfad, Sicherungsweg, Commit-ID/Archivmitglied, geprüften
  Stand und Restore-Nachweis festhalten. Für DBs den konsistenten Snapshot und
  dessen Manifest zuordnen, nicht Bytegleichheit mit einer weitergeschriebenen DB.
- Auch ignorierte Dateien, breite Ausschlüsse, neue Plugins und eingebettete
  Repositories prüfen. Nicht gesicherte Nutzdaten benötigen einen zusätzlich
  erzeugten geschützten Dateisnapshot; reine Planung oder Nennung reicht nicht.
  Die zusätzliche Sicherung auf Quellen innerhalb des Hermes-Homes begrenzen.
- Den Abschlussbericht programmgesteuert gegen die Quellenmatrix abgleichen:
  keine fehlende relevante Quelle, kein unklassifizierter Fund und kein lediglich
  geplanter Sicherungsweg. Bewusste Ausschlüsse separat mit konkretem Grund führen;
  wichtige Daten nicht als „ausgeschlossen“ umetikettieren, um die Prüfung zu bestehen.
- Neue oder unbekannte Dateien ohne Zuordnung blockieren den Gesamterfolg.
  Der erzeugte Cron prüft die Inventarzuordnung mit festgelegten Regeln ohne LLM;
  bei Neufunden bekannte Sicherungen weiter ausführen, aber einen unvollständigen
  Lauf melden. Aufnahmeregeln erst nach erneuter Bestandsprüfung erweitern.
- Pro Datei/DB ihren gesicherten Stand dokumentieren. Änderungen nach deren
  Snapshot separat behandeln; kein global atomarer Zeitpunkt über Git und DBs.
  Fehlende Rechte, unaufgelöste Links, ungedeckte Hindsight-Abhängigkeiten oder
  fehlende Restore-Belege bleiben Abnahmeblocker, keine stillen Erfolgsausnahmen.

## Abnahme bei späterer Nutzung

1. Vollständigkeitsabgleich bestanden: jeder relevante Fund ist tatsächlich gesichert
   und wiederherstellbar, keine unklassifizierten oder ungedeckten Nutzdaten bleiben.
2. Angepasste `.gitignore` schließt alle ausgewählten DBs/Credentials aus, ohne
   benötigte eigene Dateien unbemerkt zu verlieren. Getrackte Altlasten getrennt melden.
3. Orchestrator und alle erzeugten Skripte statisch prüfen und erst nach
   Ausführungsfreigabe starten. Gespeicherten Cron und tatsächlichen Scheduler-Lauf
   auf LLM-freie Skriptausführung, Zeitplan, neuen lokalen Commit und bei Push-Auswahl
   identischen Remote-Commit prüfen. Ein Lesezugriff allein genügt dafür nicht.
4. Manifest, Archiv-/Snapshot-Hashes, SQLite-Integrität und vollständige Dateien prüfen.
5. Isoliert wiederherstellen; nie als Test über Live-Dateien schreiben. FTS-Funktion,
   wichtige Tabellen und Credential-Dateirechte prüfen, ohne Inhalte auszugeben.
6. Bei genutztem Hindsight DB-Dump und isolierten DB-Restore gesondert abnehmen;
   fehlende DB-Rechte oder unbekannte Zuständigkeit als offene Sicherungslücke melden.
7. Credential-Manifest gegen das Archiv/den Restore prüfen, nicht gegen inzwischen
   erneuerte Live-Tokens. Git-Dateien direkt aus dem vorhandenen Commit in ein
   isoliertes Ziel wiederherstellen; dafür kein Repository-Backup erzeugen.
   Erforderliche Dateisnapshots der nicht durch Git gesicherten Daten separat restoren.
8. Nur tatsächlich belegte Stufen melden. Dieses Paket liefert Vorlagen für DBs und
   Credentials; die verpflichtende Git-/Cron-Automation und alle nötigen weiteren
   Dateisnapshots sind zielabhängig zu erzeugen und vollständig abzunehmen.
   Der Paketstand selbst ist weiterhin kein bereits laufendes Vollbackup.
