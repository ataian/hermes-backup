# Separates Credential-Backup

Credentials erhalten ein eigenes Skript, getrennt von Git und SQLite-Dumps.
Die [Vorlage](../templates/credentials_backup.py.example) archiviert ausschließlich
explizit ausgewählte Dateien innerhalb des gewählten Hermes-Homes.

## Bestandsprüfung

- Suchhinweise: `.env`, weitere tatsächlich verwendete Env-Dateien, `auth.json`,
  Auth-Pools, `credentials.json`, OAuth-/MCP-Tokens und sensitive Plugin-Konfigurationen.
- `hindsight/config.json` kann API-Schlüssel enthalten und muss ausdrücklich auf
  Credential-Relevanz geprüft werden; sie ist nicht allein wegen `.json` normale
  versionierbare Konfiguration. Das gilt auch für entsprechende Profilpfade.
- Andere Profile nur nach geklärtem Umfang; Muster helfen beim Inventar, nicht als
  unbeschränkte nächtliche Quellenliste. Caches, Lockdateien und alte Tokenkopien
  nicht blind einsammeln; notwendige Restore-Dateien begründet auswählen.
- Nur Pfade, Typen und Rechte berichten. Keine geheimen Werte lesen/anzeigen lassen,
  keine Secrets in Prompts, Git, Skill, Logs oder README. Zum freigegebenen Archivieren
  muss das Skript Inhalte lesen, aber es gibt sie nicht aus.
- Externe `.ssh`, Mail-Konfigurationen, Projekt-`.env` und fremde Benutzerverzeichnisse
  bleiben ausgeschlossen. Die externe Hindsight-DB wird separat gesichert, nicht
  durch eine Erweiterung dieses Credential-Skripts auf beliebige externe Dateien.
- Symlinks zu externen Dateien als Lücke melden, nicht verfolgen. Sensitive
  SQLite-Tokenstores über den konsistenten DB-Dumper sichern, nicht roh tar-archivieren.

## Eigenes Skript erzeugen

1. Die tatsächlich benötigten regulären Dateien als relative Pfade auflisten.
   `.env` darf auf einer frischen Installation fehlen; nicht erfinden. Nur bestätigte
   vorhandene Dateien aufnehmen. Späteres Fehlen eines ausgewählten Pfads ist ein Fehler.
2. Vorlage nach dem vereinbarten Ziel ableiten; `--home` und wiederholte `--file`
   für die geprüfte Liste einsetzen. Neue Credential-Speicher erfordern erneute
   Bestandsprüfung. Leere Quellenlisten erzeugen keinen falschen Erfolg.
3. Vorgeschlagenes Backupziel `~/backups/hermes/`, je Lauf neues Verzeichnis
   `YYYY-MM-DD_HHMMSS_ffffff`, darin `credentials.tar.gz`, Manifest und Abschlussstatus.
4. Alle Verzeichnisse `0700`, alle Dateien `0600`; eigenes, nicht fremd beschreibbares
   Ziel ohne Symlinks. Bereits vorhandene ungeeignete Rechte nicht still ändern.
5. Archivmitglieder ausschließlich relative, ausgewählte reguläre Dateien;
   keine Hardlinks, Geräte oder Symlinks. Pro Datei denselben eingelesenen Inhalt
   archivieren und hashen; Änderungen während des Lesens führen zum Abbruch.
6. Gzip bis zum Ende prüfen, Mitgliedermenge und Größen/Hashes aus dem zurückgelesenen
   Archiv vergleichen. Keine `extractall`-Operation und kein Vergleich gegen frisch
   erneuerte Live-Tokens. `COMPLETE.json` erst nach Gesamterfolg.
7. Aufbewahrung und Cronzeit aus den ausdrücklich bestätigten Antworten übernehmen
   (Vorschläge: 30 Tage und täglich 05:00 lokale Zeit). Vorlage enthält keine Rotation;
   die freigegebene begrenzte Rotation erst im Zielskript ergänzen.

Beispiel nur für eine Zielinstanz mit bestätigter `.env` und `auth.json`, erst nach
Einrichtungs-/Ausführungsfreigabe:

```bash
python3 "$HERMES_HOME/scripts/hermes-credentials-backup.py" --home "$HERMES_HOME" --out-base "$HOME/backups/hermes" --file .env --file auth.json
```

Vorher tatsächliches `$HERMES_HOME` bestimmen; im Cron absolute Interpreter-/Skript-
und Quellpfade verwenden. Erfolg bleibt still, Fehler auf stderr mit Exit ungleich null.
Archiv/Manifest sind vertraulich und gehören nicht in dieses öffentliche Repository.

## Sicherheit und Restore

- `tar.gz` bietet **keine Verschlüsselung**. Restriktive Rechte sind kein Schutz
  vor Hostadministratoren oder Datenträgerverlust. Vor externem Transport passende
  Verschlüsselung und getrennt verfügbare Wiederherstellungsschlüssel vereinbaren.
- Manifeste enthalten Metadaten/Hashes, keine Werte; dennoch vertraulich behandeln.
- Leere Dateien sind technisch zulässig, werden mit Größe null ausgewiesen und
  bei der fachlichen Abnahme geprüft. Nicht jeder leere Konfigurationsplatzhalter
  ist defekt, aber eine unerwartet leere Token-Datei ist ein Befund.
- Vorlage begrenzt einzelne Dateien auf 16 MiB. Größere Speicher gezielt bewerten,
  statt die Grenze still zu ignorieren. Keine Aussage über anwendungsübergreifende
  atomare Konsistenz; zusammengehörige Dateien können eine koordinierte Sicherung brauchen.
- Die Vorlage setzt eigene vertrauenswürdige Verzeichnisse ohne feindliche
  konkurrierende Pfadwechsel voraus. Sie ist keine Sandbox für fremde Dateibäume.
- Späterer Restore zuerst in einen neuen geschützten Prüfbereich, Pfade und
  Mitgliedertypen validieren, mit `0600`/`0700` wiederherstellen und Hashes gegen das
  Manifest prüfen. Niemals probeweise Live-Tokens oder `.env` überschreiben.
- Ein echter Restore und eine Funktionsprüfung bleiben eigene Abnahmeschritte.
  Die hier beschriebene Archivprüfung ist kein bereits bestandener Laufzeittest.
