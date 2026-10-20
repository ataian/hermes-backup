---
name: hermes-backup
description: Use when planning or setting up .hermes backups.
version: 0.1.0
author: Max, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [backup, gitignore, sqlite, credentials, restore]
    related_skills: []
---

# Backups für .hermes

Erarbeite für eine frische oder gewachsene Hermes-Installation eine passende
Backupstrategie und erzeuge daraus lokale Backupskripte. Sichere ausschließlich
Inhalte innerhalb des ausdrücklich gewählten Hermes-Homes. Einzige externe
Ausnahme ist die zugehörige Hindsight-Datenbank. Das vorgeschlagene Backupziel
außerhalb der Quellen ist `~/backups/hermes/`.

## Wann verwenden

- `.hermes` erstmals sichern oder bestehende Sicherung auf Lücken prüfen.
- `.gitignore`, konsistente Datenbank-Dumps und separate Credential-Sicherung vorbereiten.
- Nicht für Host-Backups, externe Projekte, Vaults, SSH-Verzeichnisse oder andere externe Datenbankdienste.

## Arbeitsgrenze

**Keine Ausführung bei Paketerstellung:** Wird nur dieser Skill oder ein Skript
angefordert, erzeuge und prüfe Projektdateien statisch. Keine Vorlagen starten,
importieren oder mit `--help` aufrufen; keine Live-Installation, Backups oder Cronjobs.
Das Paket ist unabhängig von `generic-main-agent`; dessen Dateien bleiben unverändert.

Bei später ausdrücklich beauftragter Einrichtung gelten die Schutzregeln des
Zielagenten. Freigabe für Quellen, Schreibziele und Zeitplan klären; Rotation,
Wiederherstellung, andere Profile und geschützte Infrastruktur gesondert abgrenzen.
Installation des Skills allein ist kein Auftrag, Backups einzurichten.

## Voraussetzungen

- Für Bestandsprüfung: lesender Datei-/Git-Zugriff im vereinbarten Hermes-Home;
  für die spätere tägliche Sicherung ein lokales Git-Repository genau dort.
- Für abgeleitete Skripte: Python 3.10+ mit Standardbibliothek, einschließlich
  `sqlite3`; Linux/macOS. Paketerstellung benötigt keine laufende Datenbank.
- Verbindlich laden: [Strategie](references/strategie.md),
  [DB-Dumper](references/db-dumper.md), [Credentials](references/credentials.md)
  sowie [Hindsight-DB](references/hindsight.md) und [Git/Cron](references/git-cron.md).

## Vorgehen — Bestand vor Vorlage

1. **Instanz und Auftrag auflösen.** Das tatsächlich gemeinte Hermes-Home aus
   Profilkontext, `HERMES_HOME` und vorhandener Struktur bestimmen; nicht blind
   das Default-Profil verwenden. Eigene Daten und andere Profile unterscheiden.
   Ermitteln, ob nur Entwürfe oder auch Einrichtung/Ausführung beauftragt sind.
2. **Inventarisieren, keine feste DB-Liste übernehmen.** Dateien, Datenbanktypen,
   bestehende Skripte/Jobs, Git-Regeln und Credential-Speicher prüfen. Inhaltliche
   Secrets weder anzeigen noch in Report, Git oder Chat übernehmen. Jeden Fund
   klassifizieren: Git / DB-Dump / Credentials / sonstiger Dateisnapshot /
   regenerierbar / außerhalb des Auftrags. Unsichere Funde offen ausweisen.
3. **Täglicher lokaler Git-Commit ist Pflicht.** [Git-Vorlage](templates/gitignore.hermes) als
   Ausgangspunkt für `<HERMES_HOME>/.gitignore` verwenden. Im frischen Ziel nach
   Prüfung kopieren; im bestehenden Ziel Regeln vergleichen und gezielt zusammenführen.
   Individuelle Regeln erhalten. Die Paketvorlage unverändert lassen. Bereits
   getrackte Geheimnisse und zu breit ausgeschlossene wichtige Dateien gesondert prüfen.
   Im später eingerichteten Cron täglich in diesem Repository committen, auch ohne
   Änderungen einen datierten Checkpoint erzeugen. Push separat abfragen; bei Ja
   muss der Benutzer das Remote-Ziel nennen. Schreibzugriff und unbeaufsichtigten
   Push prüfen, bei fehlendem Zugriff bei der Einrichtung helfen. Details: [Git/Cron](references/git-cron.md).
4. **Zwei eigene Backupskripte erzeugen.** Aus
   [DB-Vorlage](templates/db_dump.py.example) und
   [Credential-Vorlage](templates/credentials_backup.py.example) selbständige
   lokale Skripte mit geprüften Quellenlisten ableiten. Nicht das Paket oder
   einen pauschalen rekursiven Scan als nächtlichen Job starten. Quellen relativ
   zum gewählten Hermes-Home; Symlink-Ziele außerhalb bleiben ausgeschlossen.
   Keine externen Projekt- oder Serverpfade aus historischen Beispielen übernehmen.
5. **Hindsight-DB gesondert aufnehmen.** Falls Hindsight verwendet wird, anhand
   vorhandener Dokumentation die tatsächliche DB, Betriebsart, Zuständigkeit und
   den freigegebenen Sicherungsumfang feststellen; fehlende Angaben gezielt beim
   Benutzer erfragen. API-URL ist nicht DB-Adresse. Keine festen Hosts, Container,
   Datenbanknamen oder Zugangsdaten voraussetzen. Einen passenden DB-Backup-Schritt
   bzw. ein eigenes Skript ableiten; bei fehlendem DB-Zugriff die Lücke offen melden.
6. **Ablage und Betrieb beschreiben.** Je Lauf ein neues Verzeichnis
   `~/backups/hermes/YYYY-MM-DD_HHMMSS_ffffff/`; Mikrosekunden vermeiden Kollisionen.
   DB-Dumps erhalten ihre relativen Quellpfade, Credential-Archive bleiben separat.
   Rechte `0700`/`0600`, Manifest, Integritätskontrollen und eindeutiger
   Abschlussstatus gehören dazu. Die Backupschritte haben eigene Laufverzeichnisse,
   keinen behaupteten gemeinsamen Sicherungszeitpunkt.
   Einen täglichen deterministischen Orchestrator für alle Pflichtschritte erzeugen;
   Hermes-Cron mit `no_agent=true` und `script` einrichten, ohne LLM, Prompt oder
   agentenbasierten Fehler-Fallback. Auch Helfer, Git-Hooks und Filter LLM-frei prüfen.
7. **Entwurf vor Aktivierung abnehmen.** Quellenmatrix, Ausschlüsse, Skripte,
   tatsächliche Zielpfade, Zeitplan, Fehlerzustellung und Wiederherstellung zeigen.
   Bestehende Jobs erhalten; keine doppelte Automation. Aufbewahrungsdauer und
   Cronzeit ausdrücklich beim Benutzer abfragen, mit **30 Tagen** und
   **täglich 05:00 Uhr morgens in der lokalen Zeitzone** als Vorschlag. Ermittelte
   Zeitzone anzeigen; nicht still übernehmen. Erst bestätigte Werte verwenden.
   Den begrenzten Löschumfang erklären und vor Einbau der Rotation freigeben lassen.
8. **Nur bei Ausführungsauftrag verifizieren.** Erst dann Backup-Läufe und
   isolierte Restore-Proben ausführen. Inventar einschließlich ignorierter Nutzdaten
   gegen Commit-Baum und tatsächlich erzeugte Archive/Manifeste abgleichen.
   Zusätzliche benötigte Dateisnapshots verbindlich erzeugen und prüfen, nicht nur
   vorschlagen. Ungesicherte relevante oder unklassifizierte Daten blockieren die
   Gesamtabnahme. Neufunde ohne Sicherungsweg müssen auch spätere Läufe als
   unvollständig melden. Regenerierbarkeit muss begründet sein; Ignore-Regeln
   allein sind kein Ausschlussgrund. Den tatsächlichen LLM-freien Cron-Lauf und
   bei gewähltem Push die Übereinstimmung des Remote-Commits separat nachweisen.

## Ergebnisformat

- Quellenmatrix: relativer Pfad, Zweck/Typ, Sicherungsweg, Aufnahme/Ausschluss mit Grund.
- Zielangepasste `.gitignore`, LLM-freier täglicher Orchestrator mit Pflicht-Commit
  und optionalem geprüftem Push, DB-Skript, separates Credential-Skript, nötige
  weitere Dateisnapshots und bei Hindsight ein topologiespezifischer DB-Backup-Schritt.
- Kurze Befehlsliste für Lauf, Prüfung und isolierten Restore.
- Klarer Stand: nur vorbereitet / statisch geprüft / tatsächlich ausgeführt /
  Restore geprüft; verbleibende Lücken und Off-Host-Verantwortung.

## Fallstricke

- `.gitignore` ist kein Secret-Scanner und keine Sicherung ausgeschlossener Daten.
- Ein Live-SQLite-`cp` samt WAL/SHM oder SQL-Textdump ist kein Ersatz für einen
  konsistenten Snapshot; FTS-Indizes müssen erhalten bleiben.
- Beispielnamen sind Suchhinweise, keine Zusage über alte oder künftige Hermes-Versionen.
- Konfigurationsdateien können Credentials enthalten, auch wenn sie nicht `.env` heißen.
- Ein lokales Backup schützt nicht vor Hostverlust. Der optionale Git-Push deckt
  nur Git-Inhalte ab; DBs, Credentials und weitere Snapshots brauchen zusätzlich
  eine geschützte externe Kopie. Netzwerk-/Tunneländerungen bleiben gesondert freizugeben.

## Prüfung des Pakets

`python3 tests/check_static.py` prüft nur Text, YAML, Verweise, Vorlagenidentität
und Python-AST; kein Import und keine Ausführung der Backupvorlagen.
Python mit vorhandenem `ruamel.yaml` verwenden; das ist eine Testabhängigkeit,
keine Laufzeitabhängigkeit der Backupskripte. Statische Prüfung beweist keinen Restore.

## Paketdateien und Quellen

- [Nutzung und Installation](README.md)
- [Autorenregeln](AGENTS.md)
- [Vorlagenherkunft](references/template-origin.json)
- [Statischer Prüfer](tests/check_static.py)
- [Lizenz](LICENSE)
- [Hermes-Profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)
- [Hermes-Sessions](https://hermes-agent.nousresearch.com/docs/user-guide/sessions)
- [Hermes-Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
