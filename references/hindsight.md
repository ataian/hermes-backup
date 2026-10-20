# Hindsight-DB: die einzige externe Ausnahme

Hindsight wird nicht bei jedem Benutzer gleich betrieben. Der Skill setzt
**keine festen** Hosts, Ports, Container, Compose-Projekte, Datenbanknamen,
DB-Rollen, Banks oder Speicherorte voraus. Falls kein Hindsight genutzt wird,
diesen Schritt als nicht zutreffend dokumentieren; nichts dafür installieren.

## Topologie und Zuständigkeit klären

1. Vorhandene Betriebsdokumentation und die nicht-sensitiven Metadaten der
   Hermes-Memory-Konfiguration heranziehen. Keine vollständigen Config-/Env-Dumps
   ausgeben. Die **API-URL** des Clients ist nicht automatisch die PostgreSQL-Adresse;
   `localhost` kann auf einen Tunnel zeigen.
2. Feststellen: eingebetteter/lokaler Dienst, Container/Compose, externer Server
   oder verwalteter Anbieter? Wo liegt die tatsächliche persistente DB, wer betreibt
   sie, welcher Datenbanktyp/-stand ist installiert, welcher Sicherungsweg besteht?
3. Wenn daraus keine belastbare Zuordnung folgt, beim Benutzer **nachfragen**:
   „Wo und wie läuft deine Hindsight-Datenbank, wer betreibt sie, und gibt es
   bereits ein DB-Backup?“ Nur fehlende Angaben fragen; keine Secrets im Chat sammeln.
4. Bei einer **gemeinsam** genutzten DB den erlaubten Umfang klären. Eine einzelne
   Bank-ID ist keine Erlaubnis für einen Dump aller Nutzer/Banks. Bei fehlender
   Zuständigkeit den Betreiber um ein autorisiertes Backup/Restore-Verfahren bitten.
5. Den konkreten Hindsight-DB-Backup-Schritt separat freigeben lassen. Diese Freigabe
   deckt weder Dienst-/Tunnelneustarts noch Netzwerk-/Authänderungen, Upgrades oder
   einen Restore in Produktion ab. Bestehende Zugriffswege verwenden; fehlender
   Zugang ist eine Rückfrage, kein Auftrag zum Aufbau neuer Infrastruktur.

## Passenden Backup-Schritt erzeugen

- Für eine bestätigte PostgreSQL-DB einen konsistenten logischen Dump mit dem
  passenden `pg_dump` erzeugen, üblicherweise Custom-Format (`--format=custom`).
  Client-/Server-Version, benötigte Extensions und Wiederherstellungsziel prüfen;
  möglichst zur Server-Hauptversion passende Werkzeuge verwenden.
- Verbindungsweg erst aus der tatsächlichen Installation ableiten: lokaler
  DB-Client, geprüfter Container-/Compose-Aufruf oder freigegebener Remotezugang.
  Keine automatisch vorgegebene Rolle `postgres`, kein erfundener Dienst `db`.
- Secretzugriff über den vorhandenen sicheren Mechanismus (z. B. geschützte
  Passfile oder im Container verfügbare Credentials); kein Passwort in Argumenten,
  Scripttext, Logs, Git oder Chat. Nicht durch `source .env` Shellcode ausführen.
- Ein eigenes lokales Hindsight-Backupskript beziehungsweise einen klaren Schritt
  im bestätigten Ablauf erzeugen. Vorgeschlagenes Ziel ist ebenfalls
  `~/backups/hermes/YYYY-MM-DD_HHMMSS_ffffff/`, darin `hindsight.dump`, Manifest und
  Abschlussmarker. Bei entfernten Dumps den sicheren Transfer zum Ziel mitprüfen;
  keine ungeschützten temporären Kopien auf dem DB-Host zurücklassen.
- Erst eine geschützte `.partial`-Datei anlegen; Exitstatus prüfen, dann
  `pg_restore --list` und SHA-256 kontrollieren. Erst danach endgültig benennen und
  den Satz vollständig markieren. Ein Teil-Dump ist kein Erfolg.
- Dumpumfang und Restore-Abhängigkeiten dokumentieren: Rollen/Ownership/ACLs,
  Extensions (z. B. Vektorerweiterung), DB-/Hindsight-Version. `pg_dump` sichert
  nicht automatisch Clusterrollen oder externe Dokument-/Objektspeicher.
  Solche Abhängigkeiten als offene Betreiberaufgabe melden; die einzige externe
  Sicherungsausnahme dieses Skills bleibt die Hindsight-DB, kein ganzes Dienstverzeichnis.
- Ohne DB-Zugriff, etwa bei verwaltetem Hindsight, das verfügbare Betreiberbackup
  klären. Ein Bank-/API-Export ist nicht automatisch ein DB-Backup: Umfang und
  Wiederherstellbarkeit getrennt benennen, Lücke nicht als erledigt markieren.
- Für andere tatsächlich nachgewiesene Backends das vom Betreiber dokumentierte
  konsistente Verfahren benutzen; nicht blind einen PostgreSQL-Befehl anwenden.

## Aufbewahrung, Cron und Restore

- Bestätigte Antworten zur Aufbewahrung und Cronzeit aus dem Hauptskill verwenden
  (Vorschläge: **30 Tage**, **täglich 05:00 Uhr lokale Zeit**); nicht ungefragt eine
  zweite abweichende Regel anlegen. Ein vorhandener Betreiberjob kann die DB bereits
  abdecken, wenn Umfang, Aufbewahrung und Restore-Nachweis zum Bedarf passen.
- Bei zulässiger Rotation nur eigene, zum verifizierten DB-Ziel gehörende vollständige
  Sätze nach neuem Erfolg rotieren; letzte gute Sicherung und fremde/unklare Sätze erhalten.
- `pg_restore --list` ist kein tatsächlicher **Restore**. Nach gesonderter Freigabe
  in eine isolierte Test-DB wiederherstellen, Datenumfang und benötigte Banks/
  Dokumente/Tags prüfen. Frische leere Banks sind legitim; keine pauschale
  „jede Bank muss Einträge haben“-Prüfung.
- Produktions-DB, Live-Clientkonfiguration und bestehende Tunnel unangetastet lassen.
  Funktionale Hindsight-Proben nur gegen das bestätigte Testziel; möglichen
  Modell-/API-Aufwand vorher klären. Wenn die Probe nicht möglich ist, genau diese
  offene Abnahme benennen.

## Referenzen für die spätere Zielprüfung

- [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [PostgreSQL pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [Hindsight-Dokumentation](https://hindsight.vectorize.io/)

Dieses Paket liefert bewusst keinen fest verdrahteten Hindsight-Aufruf. Erst die
ermittelte und freigegebene Topologie macht daraus ein ausführbares Backupskript.
