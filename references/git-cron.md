# Pflicht: täglicher Git-Commit, optionaler Push, Cron ohne LLM

Diese Anleitung gilt für die später ausdrücklich beauftragte Zielinstallation.
Bei Paketarbeit nur Dateien bearbeiten und statisch prüfen, nichts einrichten,
committen, pushen oder als Backup ausführen.

## Lokales Repository vorbereiten

1. Das bestätigte Hermes-Home ist der Repository-Root, normalerweise `.hermes/`.
   Mit `git rev-parse --show-toplevel` den tatsächlichen Root prüfen. Ein Elternrepo,
   fremdes Worktree oder verschachteltes Repo nicht versehentlich mitbearbeiten.
   Falls dort noch kein Repo besteht, im freigegebenen Setup genau dort initialisieren.
2. Bestehende Branches, Remotes, Index und Historie erhalten. Commit-Identität aus
   vorhandener Konfiguration übernehmen oder erfragen und nur repo-lokal setzen.
   Die angepasste `.gitignore` mit dem tatsächlichen Bestand abgleichen.
3. Getrackte DBs/Credentials und Secrets in vorhandener Historie prüfen. `.gitignore`
   entfernt sie nicht rückwirkend; vor Automation bereinigen lassen, ohne ungefragten
   History-Rewrite. Bei geplanter Übertragung die gesamte zu pushende Historie prüfen,
   nicht nur den neuesten Diff. Keine Werte oder vollständigen Secret-Diffs ausgeben.
4. Den Git-Schritt als deterministisches Skript erzeugen: freigegebene Dateiauswahl,
   Ausschlussregeln, Secret-Prüfung und Fehlerbehandlung sind Code, kein nächtlicher
   Agentenauftrag. Neue unklassifizierte Dateien führen zur Abdeckungswarnung und
   blockieren den Gesamterfolg, statt ungeprüft ins Git zu gelangen.

## Vertrag des täglichen Git-Schritts

- Immer im bestätigten Hermes-Repository arbeiten. Überlappende Backup-Läufe mit
  einer eigenen Sperre verhindern. Vorhandene Merge-/Rebase-Konflikte, ein unerwarteter
  Branch oder fremde vorgemerkte Änderungen sind Fehler; Index/Arbeitsbaum nicht mit
  `reset`, `stash`, `checkout` oder Löschen passend machen. Fremde Indexeinträge weder
  mitcommitten noch überschreiben. Andere Git-Schreiber während des Schritts vermeiden.
- Ausschließlich die freigegebene Git-Dateimenge stagen, einschließlich bestätigter
  Änderungen/Löschungen. Ignore-Regeln und sensible Pfade auch gegen den Index prüfen;
  kein ungeprüftes `git add -A` auf den gesamten Baum. Nicht sensitive Inhalte in
  eigentlich normalen Konfigurationsdateien übersehen.
- Täglich einen neuen lokalen Sicherungsstand erzeugen: `git commit --allow-empty`
  mit Zeitstempel in der Nachricht. So entsteht auch ohne Dateiveränderung der
  ausdrücklich gewünschte tägliche Commit. Exitstatus, neuen HEAD, Parent und den
  tatsächlich committeten Baum prüfen; nur die genehmigte Auswahl darf sich ändern.
  Keinen Commitfehler als „es gab wohl nichts zu tun“ wegfangen.
- Nested Repos/Submodule sind in Git gegebenenfalls nur Referenzen: ein Gitlink
  sichert nicht deren Arbeitsdateien oder uncommittete Änderungen. Benötigte Inhalte
  innerhalb des freigegebenen Hermes-Homes zusätzlich in den Dateisnapshot aufnehmen.
- Ohne Push-Auswahl endet dieser Git-Schritt lokal. Bei gewähltem Push nach dem
  lokalen Commit ausschließlich den bestätigten Branch an das bestätigte Ziel senden;
  weder alle Branches/Tags noch `--mirror` oder `--force`. Bei abweichender Remote-
  Historie stoppen und helfen; kein automatischer Pull/Merge/Rebase im Backupjob.
- Push-Fehler lassen den lokalen Commit bestehen, melden aber den Remote-Schritt
  als fehlgeschlagen. Beim nächsten Lauf ausstehende freigegebene Commits mitnehmen.
  DB-/Credential-/Dateisicherungen unabhängig weiter versuchen; Gesamtfehler sammeln.
- Der Git-Verlauf wird nicht durch die bestätigte Tages-Retention umgeschrieben.
  Diese betrifft ausschließlich freigegebene Snapshot-Sätze, keine alten Commits.

## Optionales Remote bei Einrichtung klären

**Frage:** „Soll das tägliche Git-Backup zusätzlich auf ein Remote gepusht werden?“

- Bei Nein: lokaler Commit bleibt Pflicht, kein Push und keine Remote-Einrichtung.
- Bei Ja: Benutzer muss die konkrete Remote-URL angeben, außerdem Zielbranch und
  gewünschtes vorhandenes Remote bestätigen. Kein Ziel aus diesem öffentlichen
  Skill-Repository ableiten. Für persönliche Backups ein privates Repo empfehlen;
  Sichtbarkeit prüfen und vor einer öffentlichen Übertragung ausdrücklich klären.
  Andere konfigurierte Remotes nicht still umbiegen.
- Ein erfolgreicher `git ls-remote` beweist nur Lesezugriff, nicht Push-Berechtigung.
  `git push --dry-run` auf den vorgesehenen Branch dient als Vorprüfung, beweist
  aber nicht alle serverseitigen Hooks/Branchregeln. Innerhalb der bestätigten
  Push-Einrichtung den ersten echten Backup-Commit pushen und danach den exakten
  Remote-Branch erneut lesen: seine Commit-ID muss dem lokalen Sicherungscommit
  entsprechen. Ohne diesen Nachweis Push nicht als betriebsbereit abnehmen.
- Unbeaufsichtigte Anmeldung unter der tatsächlichen Cron-Identität und -Umgebung
  prüfen: kein interaktiver Passwortdialog, kein nur im Desktop verfügbarer SSH-Agent,
  keine ablaufende Sitzung als einzige Grundlage. Endliche Netzwerk-Timeouts und
  eindeutige Fehlermeldungen vorsehen; Tokenwerte nicht in Logs schreiben.
- Bei fehlendem Ziel oder Zugriff bei der Einrichtung helfen: Nichtexistenz,
  falsche URL, fehlende Schreibrechte, Authentifizierung und Branchschutz unterscheiden.
  Das private Zielrepo oder passende Schreibberechtigungen im genehmigten Umfang
  einrichten bzw. den zuständigen Benutzer durch die Anbieteroberfläche begleiten.
  Vorhandene sichere SSH-/Credential-Mechanismen bevorzugen. Neue Keys, Anbieter-
  Änderungen oder Infrastruktur brauchen die jeweils notwendige Freigabe.
- Passwörter/Tokens nie im Chat, in Remote-URLs, Skripttext oder Git speichern.
  Sichere lokale Anmeldung/Credential-Verwaltung verwenden; keine globalen
  Git-/SSH-Änderungen oder Abschwächung des Host-Key-Checks als Abkürzung.
- Kann der Push noch nicht eingerichtet werden, lokalen Backupbetrieb erhalten,
  Remote-Status als offen/fehlgeschlagen melden und den konkreten nächsten Schritt
  nennen. Nicht still von „Push gewünscht“ auf „nur lokal vollständig“ zurückfallen.

## Einen LLM-freien täglichen Ablauf einrichten

1. Aufbewahrung und Cronzeit abfragen (Vorschläge: 30 Tage, täglich 05:00 lokale
   Zeitzone). Bestätigte Antworten und Push-Auswahl außerhalb sensitiver Ausgaben
   in der Zielkonfiguration festhalten. Bestehende Jobs integrieren, nicht duplizieren.
2. Einen deterministischen Orchestrator unter `<HERMES_HOME>/scripts/` erzeugen,
   der Git-Commit, optionalen Push, SQLite, Credentials, nötige zusätzliche
   Dateisnapshots und gegebenenfalls Hindsight aufruft. Teilergebnisse unabhängig
   erfassen, Abschlussbericht nur bei allen verpflichtenden Schritten erfolgreich.
3. Hermes-Cron ausdrücklich mit **`no_agent=true`** und **`script`** auf den
   Orchestrator/Wrapper einrichten. Kein Prompt, kein Skill-Aufruf, kein Modell und
   kein Agent als Fehler-Fallback. `script` bezeichnet die Skriptdatei unter dem
   aufgelösten Hermes-Home, nicht eine frei zusammengesetzte Kommandozeile.
   Aktuelle Syntax in der [Cron-Dokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
   gegen die installierte Version prüfen.
4. Alle transitiven Aufrufe ebenfalls LLM-frei halten: keine `hermes chat`-, Codex-,
   Agenten- oder Modellaufrufe in Helfern, Git-Hooks, Filtern oder Fehlerbehandlung.
   Vorhandene Hooks/Filter prüfen; notwendige Anpassungen gezielt abstimmen, nicht
   unbekannte Hooks ungeprüft starten oder global Sicherheitsprüfungen abschalten.
5. Absolute Interpreter-/Skriptpfade, festes Arbeitsverzeichnis, geeignete Timeouts,
   Sperre, geschützte Logs und sichere Credential-Verfügbarkeit verwenden. Kein
   Prompting im Lauf. Bei Erfolg still; Fehler deterministisch und secretfrei melden.
   Native Fehlerzustellung/Exitstatus tatsächlich testen, nicht nur konfigurieren.
6. Nach Einrichtung den gespeicherten Job lesen: Zeitplan, Zeitzone, `no_agent=true`,
   Skriptpfad und Zustellziel prüfen. Einen tatsächlichen freigegebenen Scheduler-
   Lauf abnehmen: neuer lokaler Commit, bei Push-Auswahl Remote-ID gleich lokal,
   vollständige Snapshots, Abdeckungsbericht und fehlende Agent-/Modellaufrufe im
   ausgeführten Pfad. Ein direkter Shelltest allein belegt nicht die Cron-Umgebung.

Ein Git-Push sichert nur den Git-Inhalt. Ausgeschlossene DBs, Credentials und
Dateisnapshots brauchen weiterhin die eigene geschützte externe Kopie; diese
zusätzliche Off-Host-Spiegelung wird hier nicht automatisch eingerichtet.
