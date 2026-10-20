# SQLite-Dumper aus dem Bestand ableiten

## Vertrag der Vorlage

[db_dump.py.example](../templates/db_dump.py.example) ist eine anpassbare
Ausgangsbasis, kein bei Installation gestarteter Job. Der Agent ermittelt die
DB-Dateien selbst und erzeugt daraus ein eigenständiges Skript samt Aufruf mit
expliziter Quellenliste. Keine fremden Quellen aus einem Beispiel übernehmen.

- `--home`: geprüfter absoluter Hermes-Home-Pfad; kein stilles Default-Profil.
- `--db`: genau ein freigegebener relativer SQLite-Pfad; für jede DB wiederholen.
- `--out-base`: standardmäßig `~/backups/hermes`, außerhalb des Quellbaums.
- Alle aufgeführten Quellen sind Pflicht. Fehlende/nicht lesbare Dateien, fremde
  Eigentümer, Symlinks, Hardlinks, Nicht-SQLite oder leere Quellenliste brechen ab.
  Bei frischem Hermes ohne DBs keinen leeren „erfolgreichen“ DB-Job anlegen;
  Bestandsprüfung nach tatsächlicher Erstnutzung wiederholen.
- Sicherung über die SQLite-Backup-API, einschließlich FTS und WAL-Inhalt. WAL/SHM/
  Journal nicht als selbständige DB sichern. Keine Live-Dateikopie, kein `iterdump()`.
- Einzeldatenbanken werden konsistent gesichert; mehrere DBs, Credentials und
  Hindsight haben keinen global atomaren gemeinsamen Sicherungszeitpunkt.
- Quellverbindung `mode=ro`; keine App-Daten ändern. SQLite kann dabei notwendige
  WAL-/SHM-Verwaltung benötigen: bei Read-only-/WAL-Problemen stoppen und passend
  prüfen, nicht `immutable=1` einsetzen und dadurch aktuelle WAL-Daten übergehen.
- Nach Snapshot: `PRAGMA integrity_check`, gzip, vollständige Dekompression,
  Byte-Hashvergleich und erneute Integritätskontrolle. Keine Gleichheitsbehauptung
  gegen eine währenddessen weitergeschriebene Live-DB.
- Relative Ordnerstruktur erhalten, z. B. `db/cron/executions.db.gz`; kein
  Bindestrich-Flattening, bei dem verschiedene Quellpfade kollidieren können.
- Neuer Zeitstempelordner pro Lauf; Dateirechte geschützt, kein Überschreiben alter
  Sätze. Einzel-DB-Fehler werden gesammelt; weitere DBs werden trotzdem versucht.
  Fehler vor der Quellenfreigabe brechen den ganzen Lauf vor Dumpbeginn ab.
- `manifest.json` nennt Quellen, Dateipfade, Größe, Hashes und Fehlerarten.
  `COMPLETE.json` entsteht nur nach Gesamterfolg; Erfolg still, Fehler auf stderr
  und Exit ungleich null. `INCOMPLETE.json`/Teilstände bei Fehler erhalten.
- Nur eigene temporäre Snapshot-/Prüfdateien aus dem aktuellen Lauf werden nach
  erfolgreicher Prüfung entfernt. Keine Aufbewahrungsrotation in der Vorlage.

## Ableitung und späterer Aufruf

1. Vorhandene Skripte zunächst lesen; passende Mechanik erhalten, keinen zweiten
   Job neben eine funktionierende Sicherung setzen.
2. Quellenmatrix erstellen, einschließlich DBs aus freigegebenen Profilen/Plugins.
   Unbekannte DB-Formate, externe Ziele und fehlende Rechte nicht still auslassen.
3. Vorlage nach dem vereinbarten Skriptziel kopieren, nötige Anpassungen durchführen
   und die ermittelte Quellenliste als expliziten Aufruf/Wrapper festhalten.
   Interpreter und Dateipfade absolut und shell-sicher quotieren. Niemals `eval`.
4. Aufbewahrung und Zeitplan gemäß Hauptskill ausdrücklich abfragen, dann die
   bestätigte Rotation mit Quellidentität/Manifestprüfung und Erhalt des letzten
   erfolgreichen Satzes ergänzen. Ohne Freigabe keine alten Sätze löschen.
5. Erst bei ausdrücklich beauftragter Ausführung verwenden. Beispiel ausschließlich
   für eine Installation, in der `state.db` tatsächlich gefunden/freigegeben wurde:

   ```bash
   python3 "$HERMES_HOME/scripts/hermes-db-backup.py" --home "$HERMES_HOME" --out-base "$HOME/backups/hermes" --db state.db
   ```

   `$HERMES_HOME` vorher auf das tatsächlich gewählte Ziel auflösen. Im Cron den
   ermittelten absoluten Python-Pfad verwenden, nicht auf interaktiven PATH vertrauen.
   Das Paket enthält diese Zielinstallation nicht.

## Restore-Abnahme

Im separat freigegebenen Prüfverzeichnis Snapshot dekomprimieren, Hash gegen
`sqlite_sha256` im Manifest vergleichen und `PRAGMA integrity_check` ausführen.
Benötigte Tabellen und FTS-Suche mit geeigneten Testabfragen prüfen, ohne private
Inhalte auszugeben. Kein `cp` über eine laufende DB. Ein späterer produktiver
Restore braucht eigenen Plan für Schreibpause, WAL/SHM, Rollback und Freigabe.

## Grenzen der Vorlage

Python 3.10+ mit SQLite erforderlich. Keine verschlüsselten SQLite-Dateien oder
anderen DB-Formate. SQLite-Backup/Integritätsprüfung haben jeweils ein Zeitbudget;
große Datenbanken benötigen eine begründete Anpassung. Pfadprüfungen setzen
vertrauenswürdige eigene Quell-/Zielverzeichnisse voraus, keine böswilligen
konkurrierenden Pfadwechsel oder fremden Bind-Mounts. Gleichzeitige Läufe schreiben
in getrennte neue Ordner; bei der späteren Cronintegration Überlappungen vermeiden.

**Paketabnahme ist statisch.** Keine Vorlage wurde hierfür gestartet/importiert;
WAL-, FTS-, Fehlerfall- und Restore-Verhalten sind erst am freigegebenen Testziel
praktisch zu verifizieren. Die eingebauten Prüfungen sind Code, kein hier erzielter
Laufzeitnachweis.

[Python SQLite Backup-API](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup)
