# hermes-backup

Ein Hermes-Skill für Backupstrategien einer frischen oder gewachsenen Installation.
Der Agent prüft zuerst den tatsächlichen Bestand und leitet daraus passende Skripte
ab — statt eine starre Liste aus einer fremden Installation zu übernehmen.

## Installation in Hermes

Nach Veröffentlichung im öffentlichen Repository
[ataian/hermes-backup](https://github.com/ataian/hermes-backup):

```bash
hermes skills install ataian/hermes-backup/
hermes skills list --source hub
```

Der abschließende `/` bezeichnet das Repository-Root mit der `SKILL.md`.
Für ein benanntes Profil den Installationsbefehl mit `hermes -p PROFILNAME skills install ataian/hermes-backup/`
ausführen; `PROFILNAME` durch das gewünschte vorhandene Profil ersetzen.
Die Installation stellt den Skill bereit, führt aber keine Backupvorlage aus.
Sicherheitsprüfung nicht mit `--force` umgehen. Danach vollständige Verfügbarkeit
von `SKILL.md`, `references/` und beiden `templates/*.py.example` sowie
`templates/gitignore.hermes` kontrollieren; eine Erfolgsmeldung allein beweist
keinen vollständigen Download.

Die Syntax folgt der [Hermes-Skills-Dokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
und der GitHub-Root-Auflösung im geprüften Hermes-Quellstand. Die Installation aus
diesem Repository wird erst nach dessen Veröffentlichung praktisch prüfbar;
hier wurde weder veröffentlicht noch installiert.

## Verwenden

In Hermes:

```text
/hermes-backup Prüfe meine Installation und bereite eine Backupstrategie sowie passende Skripte vor. Noch nichts aktivieren oder ausführen.
```

Oder ohne Installation den Agenten die lokale [SKILL.md](SKILL.md) samt ihren
verpflichtenden Referenzen lesen lassen.

## Umfang

| Baustein | Ergebnis |
|---|---|
| Bestandsprüfung | Konkrete Quellenliste für die eigene Installation, einschließlich alter/zusätzlicher DBs und Credential-Speicher |
| Git | Angepasste `.gitignore` als Referenz; täglicher lokaler Commit in `.hermes` ist Pflicht, auch ohne Änderungen als Checkpoint |
| Optionaler Push | Bei Einrichtung abfragen; bei Ja nennt der Benutzer Remote-Ziel und Branch. Schreibzugriff im Cron-Kontext prüfen und bei fehlendem Zugriff bei der Einrichtung helfen |
| SQLite | Eigenes abgeleitetes DB-Backupskript, konsistente Snapshots und Integritätsprüfung |
| Credentials | Eigenes separates Backupskript für `.env`, Auth-/Token-Dateien und sensitive Konfigurationen innerhalb von `.hermes` |
| Hindsight | Einziger externer Sonderfall: tatsächliche DB/Betriebsart/Zuständigkeit feststellen oder erfragen, dann eigenen Backup-Schritt ableiten |
| Aufbewahrung und Cron | Ausdrücklich abfragen; Vorschläge **30 Tage** und **täglich 05:00 Uhr morgens in der lokalen Zeitzone** |
| Ohne LLM | Deterministischer Skriptjob mit `no_agent=true`, einschließlich Git-Commit, optionalem Push und aller Backupschritte; kein Agenten-Fallback |
| Ablage | `~/backups/hermes/YYYY-MM-DD_HHMMSS_ffffff/`, ein neuer geschützter Ordner je Lauf |
| Vollständigkeit und Wiederherstellung | Inventar gegen Commit-Baum und echte Archive abgleichen, zusätzliche nötige Dateisnapshots erzeugen und isoliert restoren; keine erfolgreiche Gesamtabnahme mit ungedeckten relevanten Daten |

Externe Projekte, Vaults, SSH-Verzeichnisse und andere externe Dienste gehören
nicht dazu. Hindsight hat bewusst keine fest vorgegebenen Hosts, Container oder
DB-Namen. Eine API-Adresse allein genügt nicht zur Bestimmung der Datenbank.

## Dateien

- [SKILL.md](SKILL.md) — Vorgehen und Freigabegrenzen
- [Strategie](references/strategie.md) — Bestandsprüfung, Git, Ablage und Abnahme
- [Git und LLM-freier Cron](references/git-cron.md) — Pflicht-Commit, optionaler Push, Zugangseinrichtung und Scheduler-Abnahme
- [DB-Dumper](references/db-dumper.md) und [Python-Vorlage](templates/db_dump.py.example)
- [Credentials](references/credentials.md) und [Python-Vorlage](templates/credentials_backup.py.example)
- [Hindsight-DB-Schritt](references/hindsight.md)
- [Gitignore-Vorlage](templates/gitignore.hermes) und [Herkunft/Hash](references/template-origin.json)
- [Statischer Prüfer](tests/check_static.py)

Die `.gitignore` basiert auf der ursprünglichen Betriebsreferenz und wurde vom
Benutzer für dieses Paket angepasst. Der aktuelle Vorlagenstand bleibt bei der
Zielnutzung erhalten. Verbliebene historische Kommentare sind keine Zielvorgaben und kein Nachweis,
dass eine andere Installation bereits ein NAS-/Off-Host-Backup besitzt.
Die Vorlage ist keine vollständige Secret-Erkennung; konkrete Credential-Pfade
müssen bei der späteren Zielprüfung ergänzt werden.

## Paketprüfung

Mit Python und vorhandenem `ruamel.yaml` aus dem Repository-Root:

```bash
python3 tests/check_static.py
```

Der Test prüft YAML, relative Verweise, Vorlagenidentität und Python-AST, ohne
Backupvorlagen zu importieren oder auszuführen. Die Backupvorlagen selbst brauchen
nur Python 3.10+ mit Standardbibliothek auf Linux/macOS.

**Stand:** Paket/Vorlagen, keine aktivierte Sicherung. Kein Backup-, Credential-,
Hindsight-, Cron- oder Restore-Lauf gehört zur Paketerstellung. Statische Prüfung
ist kein Laufzeitnachweis. Die Vorlagen enthalten keine automatische Löschung;
Rotation wird erst aus der bestätigten Aufbewahrung und Löschfreigabe abgeleitet.
Ein DB-Dump plus Credential-Archiv ersetzt nicht die Sicherung weiterer relevanter
Dateien; deren tatsächlich erzeugte Sicherung und isolierte Wiederherstellbarkeit
sind verbindliche Abnahmekriterien. Ungedeckte relevante oder neu gefundene
unbekannte Daten verhindern die Gesamterfolgsmeldung, auch im späteren Cron.
Der Git-Verlauf bleibt von der Snapshot-Retention unberührt. Ein optionaler Push
sichert nur Git-Inhalte, nicht die separat ausgeschlossenen DBs und Credentials.

## Veröffentlichung

Vorgesehenes öffentliches Repository: `git@github.com:ataian/hermes-backup.git`.
Max übernimmt den Push. Dieses Repository enthält ausschließlich Skill und
Vorlagen, niemals persönliche Hermes-Backups oder Zugangsdaten. Es verändert das
separate Projekt `generic-main-agent` nicht.

[MIT-Lizenz](LICENSE) · Max, mit Hermes Agent erstellt.
