#!/usr/bin/env python3
"""Read-only package checks: never import or execute the dump template."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    'AGENTS.md', 'README.md', 'SKILL.md', 'LICENSE',
    'references/strategie.md', 'references/db-dumper.md', 'references/git-cron.md',
    'references/template-origin.json', 'templates/gitignore.hermes',
    'templates/db_dump.py.example', 'templates/credentials_backup.py.example',
    'references/credentials.md', 'references/hindsight.md', 'tests/check_static.py',
}


def check_workflow_contract(body, strategy, git_cron):
    requirements = {
        'daily commit': (body, 'Täglicher lokaler Git-Commit ist Pflicht'),
        'no LLM': (body, '`no_agent=true`'),
        'remote choice': (git_cron, 'Soll das tägliche Git-Backup zusätzlich auf ein Remote gepusht werden?'),
        'target supplied': (git_cron, 'Benutzer muss die konkrete Remote-URL angeben'),
        'write verification': (git_cron, 'Ein erfolgreicher `git ls-remote` beweist nur Lesezugriff'),
        'remote help': (git_cron, 'Bei fehlendem Ziel oder Zugriff bei der Einrichtung helfen'),
        'unattended verification': (git_cron, 'unter der tatsächlichen Cron-Identität und -Umgebung'),
        'empty daily checkpoint': (git_cron, '`git commit --allow-empty`'),
        'coverage gate': (strategy, 'Keine erfolgreiche Gesamtabnahme bei ungesicherten relevanten Daten'),
        'coverage evidence': (strategy, 'Inventar gegen tatsächlich erzeugte Sicherungsartefakte abgleichen'),
        'new data gate': (strategy, 'Neue oder unbekannte Dateien ohne Zuordnung blockieren den Gesamterfolg'),
    }
    for label, (text, clause) in requirements.items():
        assert clause in text, f'Missing workflow requirement: {label}'
    for obsolete in ('Kein blindes `git add -A`, automatischer Commit oder Push.',
                     'Dieser Skill richtet keinen Remotezugriff ein.'):
        assert obsolete not in body + strategy + git_cron, f'Contradictory rule: {obsolete}'
    return requirements


def check(root):
    files = {str(p.relative_to(root)) for p in root.rglob('*')
             if p.is_file() and '.git' not in p.relative_to(root).parts}
    assert REQUIRED <= files, f'Missing package files: {sorted(REQUIRED - files)}'
    for p in root.rglob('*'):
        if '.git' in p.relative_to(root).parts:
            continue
        assert not p.is_symlink(), f'Symlink in package: {p}'
    text = (root / 'SKILL.md').read_text()
    assert text.startswith('---\n')
    front, body = text[4:].split('\n---\n', 1)
    from ruamel.yaml import YAML
    meta = YAML(typ='safe').load(front)
    assert isinstance(meta, dict)
    assert meta['name'] == 'hermes-backup'
    assert meta['description'].startswith('Use when ')
    assert len(meta['description']) <= 60
    assert meta['description'].endswith('.')
    assert meta['platforms'] == ['linux', 'macos']
    assert meta['version'] == '0.1.0'
    assert meta['license'] == 'MIT'
    assert body.strip()
    for phrase in (
        'Bestand vor Vorlage', 'keine feste DB-Liste',
        '~/backups/hermes/', 'generic-main-agent',
        'Keine Ausführung bei Paketerstellung',
        'Cronzeit ausdrücklich beim Benutzer abfragen', '30 Tagen', '05:00',
        'Erst bestätigte Werte verwenden', 'Hindsight-DB gesondert aufnehmen',
    ):
        assert phrase in body, f'Missing operative skill clause: {phrase}'
    strategy = (root / 'references/strategie.md').read_text()
    git_cron = (root / 'references/git-cron.md').read_text()
    requirements = check_workflow_contract(body, strategy, git_cron)
    # Text-only negative checks: remove operative clauses, not just headings.
    for label, (text, clause) in requirements.items():
        mutated = [part.replace(clause, '', 1) if part == text else part
                   for part in (body, strategy, git_cron)]
        try:
            check_workflow_contract(*mutated)
        except AssertionError as exc:
            assert str(exc) == f'Missing workflow requirement: {label}'
        else:
            raise AssertionError(f'Undetected removed requirement: {label}')
    for phrase in ('nicht rückwirkend', 'Credentials', 'Off-Host', 'Hindsight',
                   'frischen', 'gewachsenen', 'SQLite format 3', 'Freigabe'):
        assert phrase in strategy, f'Missing strategy clause: {phrase}'
    origin = json.loads((root / 'references/template-origin.json').read_text())
    template = root / origin['template']
    assert template == root / 'templates/gitignore.hermes'
    assert hashlib.sha256(template.read_bytes()).hexdigest() == origin['sha256']
    source = (root / 'templates/db_dump.py.example').read_text()
    tree = ast.parse(source, filename='db_dump.py.example')
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert {'main', 'snapshot', 'check_sqlite', 'select_sources'} <= functions
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert any(isinstance(c.func, ast.Attribute) and c.func.attr == 'backup' for c in calls)
    for c in calls:
        if isinstance(c.func, ast.Attribute):
            assert c.func.attr not in {'iterdump', 'rmtree', 'system'}, c.func.attr
        if isinstance(c.func, ast.Name):
            assert c.func.id not in {'eval', 'exec', '__import__'}, c.func.id
    strings = [n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    for value in ('--db', '--home', '--out-base', 'PRAGMA integrity_check',
                  'COMPLETE.json', 'INCOMPLETE.json', '%Y-%m-%d_%H%M%S_%f'):
        assert value in strings, f'Missing template contract: {value}'
    assert any('?mode=ro' in value for value in strings)
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) and
                   any(a.name in {'subprocess', 'requests'} for a in n.names)
                   for n in ast.walk(tree))
    creds = (root / 'templates/credentials_backup.py.example').read_text()
    creds_tree = ast.parse(creds, filename='credentials_backup.py.example')
    creds_strings = [n.value for n in ast.walk(creds_tree)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    for value in ('--file', '--home', '--out-base', 'credentials.tar.gz',
                  'COMPLETE.json', 'INCOMPLETE.json', '%Y-%m-%d_%H%M%S_%f'):
        assert value in creds_strings, f'Missing credential contract: {value}'
    for call in (n for n in ast.walk(creds_tree) if isinstance(n, ast.Call)):
        if isinstance(call.func, ast.Attribute):
            assert call.func.attr not in {'extractall', 'rmtree', 'system'}, call.func.attr
    credential_doc = (root / 'references/credentials.md').read_text()
    for phrase in ('.env', 'auth.json', 'hindsight/config.json', 'keine Verschlüsselung'):
        assert phrase in credential_doc, f'Missing credential guidance: {phrase}'
    hindsight = (root / 'references/hindsight.md').read_text()
    for phrase in ('API-URL', 'nachfragen', 'pg_dump', 'pg_restore', 'gemeinsam',
                   'keine festen', 'Freigabe', 'Restore'):
        assert phrase in hindsight, f'Missing Hindsight guidance: {phrase}'
    readme = (root / 'README.md').read_text()
    assert 'hermes skills install ataian/hermes-backup/' in readme
    assert 'git@github.com:ataian/hermes-backup.git' in readme
    assert 'Max übernimmt den Push' in readme
    for path in sorted(root.rglob('*.md')):
        content = path.read_text()
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if '://' in target or target.startswith('#'):
                continue
            destination = (path.parent / target.split('#')[0]).resolve()
            assert destination.is_relative_to(root), f'Escaping link: {path}: {target}'
            assert destination.exists(), f'Broken link: {path}: {target}'
    for path in sorted(root.rglob('*.py')):
        ast.parse(path.read_text(), filename=str(path))
    return len(files)


if __name__ == '__main__':
    try:
        total = check(ROOT)
    except (AssertionError, ValueError, KeyError, ImportError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
    print(f'PASS: {total} package files; YAML, links, template identity, AST and workflow contracts.')
    print('PASS: removed-clause negative checks for each workflow requirement.')
    print('No template imports, backup execution, database reads or runtime acceptance.')
