# project_content

Modul A aus dem modularisierten DITA-Dokumentenmanagement
(Konfigurationsprotokoll v19, Abschnitt 7). Enthält den eigentlichen,
produktspezifischen DITA-Content und muss eigenständig funktionieren –
auch ohne Modul B (`shared_content`) eingebunden zu haben.

## Wofür dieses Repo zuständig ist – und wofür nicht

- **Zuständig:** Produktspezifische DITA-Topics (`concepts`, `tasks`,
  `references`, `troubleshooting`), Keyspace-Kette (`project_content.ditamap`
  → `reusables.ditamap` → `project_names.ditamap` usw.), eigene
  Default-Werte für Metadaten (`metadata/valuelists.xml`) und Gestaltung
  (`publishing/design-values.xml`), produktspezifische Terminologie
  (`project_termbase.tbx`), `companyname`-Override-Merge
  (`merge_names.py`) bei eingebundenem B.
- **Nicht zuständig:** DITA-Content-DTD-Validierung (Modul C), Linkprüfung
  (D), Metadaten-Regelprüfung (E), Terminologieprüfung (F), PDF-/HTML-
  Publikation (G/H) – A ruft diese Module auf, implementiert ihre Logik
  aber nicht selbst.

## Struktur

```
project_content/
├── README.md                       ← diese Datei
├── OPEN_ISSUES.md                  ← echte offene Punkte, keine geloesten Design-Fragen
├── .gitignore
├── .github/
│   ├── CODEOWNERS                  ← Code Owner fuer Pull-Request-Freigaben (Kontoname von modul_a.bat eingesetzt)
│   └── workflows/
│       ├── validate.yml            ← ruft C, D, E, F auf (real ausgearbeitet, siehe unten)
│       └── branch_guard.yml        ← ruft den Waechter aus Modul J auf (nur PRs gegen main)
├── docs/
│   ├── project_content.ditamap     ← Hauptmap, bindet titlepage/imprint per topicref + reusables/relationship_table per mapref
│   ├── titlepage.dita               ← Datenquelle fuer DITA-OTs Titelseiten-Mechanismus (rendert keine eigene Seite)
│   ├── imprint.dita                 ← vollstaendige Impressum-Seite
│   ├── concepts/ tasks/ references/ troubleshooting/  ← Topics + Vorlagendatei je Typ
│   ├── reuse/                      ← Reuse-Container, Keyspace-Hub (reusables.ditamap), Names-Map
│   ├── links/                      ← externe/interne Links, Relationship-Table
│   ├── filters/standard.ditaval
│   └── images/
├── metadata/valuelists.xml         ← eigene Default-Werte fuer E
├── publishing/design-values.xml    ← eigene Default-Werte fuer G/H
├── project_termbase.tbx            ← eigene Terminologie fuer F
└── merge_names.py                  ← companyname-Override-Merge (siehe unten)
```

Vollständige Datei-für-Datei-Dokumentation mit Zweck, Pflegestelle und
lesenden Modulen: `modul_a_struktur.md` (außerhalb des Repos gepflegt).

## Einrichtung

```cmd
modul_a.bat [Kontoname] ["Handle1 Handle2 ..."]
```

Legt die Struktur relativ zum Speicherort der `.bat`-Datei an (nicht
relativ zum aktuellen Arbeitsverzeichnis der Eingabeaufforderung), bricht
ab, wenn der Zielordner `project_content` bereits existiert.

Das Skript braucht **zwei Werte**, die oft, aber nicht immer gleich sind.
Beide werden als Parameter übergeben oder beim Start abgefragt:

1. **Konto der Module** (Parameter 1): das GitHub-Konto, in dem die Module
   C bis J liegen. Der Name wird automatisch in die fünf `uses:`-Zeilen
   (`validate.yml`, `branch_guard.yml`) eingesetzt; die Vorlagen enthalten
   nur einen Platzhalter.
2. **Code Owner** (Parameter 2): ein oder mehrere GitHub-Handles, die
   Pull Requests freigeben dürfen. Mehrere durch Leerzeichen trennen und
   in Anführungszeichen setzen, z. B. `modul_a.bat mein-konto "mein-konto
   max-muster"`. Ohne Angabe (bzw. mit Enter bei der Abfrage) gilt das
   Konto aus Parameter 1. Alle Handles werden in `CODEOWNERS` für `*` und
   `/.github/` eingetragen.

Jeder Name bzw. Handle darf nur Buchstaben, Ziffern und Bindestrich
enthalten (ohne `@`), höchstens 39 Zeichen, kein Bindestrich am Anfang
oder Ende; bei ungültiger Eingabe bricht die `.bat` ab, bevor etwas
angelegt wird. **Code Owner brauchen Schreibrecht im Repo** – Handles ohne
Schreibrecht ignoriert GitHub. Teams (`@organisation/team`) nimmt die
`.bat` nicht entgegen und müssen von Hand in `CODEOWNERS` eingetragen
werden. Für das Einsetzen wird PowerShell benötigt (unter Windows
vorhanden).

**Bereits angelegtes Repo (z. B. Pilot):** `modul_a.bat` nicht im
bestehenden Repo ausführen. Stattdessen in einem leeren Ordner neu
erzeugen (gleiche Werte für Konto und Code Owner) und nur die geänderten Dateien in den
lokalen Klon des bestehenden Repos kopieren – `.github/workflows/validate.yml`,
`.github/workflows/branch_guard.yml`, `.github/CODEOWNERS`, `README.md`,
`OPEN_ISSUES.md` –, auf einem eigenen Branch per `git diff` prüfen und
per Pull Request gegen `develop` einbringen. Nicht den ganzen Ordner
kopieren: Inhalte unter `docs/` würden sonst mit den Vorlagen
überschrieben.

## companyname-Override (`merge_names.py`)

`companyname` ist ein regulärer DITA-`<keydef>` in `project_names.ditamap`
– kein eigenes Dateiformat wie `valuelists.xml`/`design-values.xml`.
Ist B als Submodul eingebunden, überschreibt `merge_names.py` vor dem
Aufruf von C (`--root`) und dem G/H-Build `project_names.ditamap`
**in-place im CI-Checkout** mit dem gemergten Ergebnis aus A's und B's
Keys (A gewinnt bei Überschneidung). Da `project_names.ditamap` bereits
über `reusables.ditamap` in die Keyspace-Kette eingehängt ist, sehen C's
`--root`-Lauf und G/H's Build das Ergebnis automatisch – **ein** Merge-
Lauf genügt, kein separater Pfad je Modul. Das Ergebnis wird nie zurück
committet/gepusht. Bekannte Grenze: Bei Mehrfach-Key-`keydef`s mit
*teilweiser* Key-Überschneidung zwischen A und B wird nicht sauber
aufgesplittet (siehe Docstring in `merge_names.py`).

Aufruf in `validate.yml` verdrahtet (per B-Submodul-Erkennung, `if`-Bedingung).
Manueller Testaufruf:

```cmd
python merge_names.py --a docs\reuse\project_names.ditamap --b <Pfad-zu-shared_names.ditamap-in-B>
```

## CI/CD-Pipeline (`validate.yml`)

Trigger: `pull_request` auf `develop` und `main` (inkrementelle Prüfung
vor dem Merge) und `push` auf `develop` (vollständiger Scan nach dem
Merge). Die beiden `develop`-Trigger sind im Pilot real verifiziert; der
Trigger für Pull Requests gegen `main` ist neu (28.09.2026) – dort ist
der Job `validierung` erforderlicher Check. Ruft `merge_names.py`
(bedingt), Modul C (`--root`, immer voller Lauf), Modul D
(`--files`/`--input` je nach Event) sowie optional Module E/F auf.
Den Kontonamen in den vier `uses:`-Zeilen setzt `modul_a.bat` ein
(siehe „Einrichtung“). G/H
(Publish) sind ausdrücklich **nicht** Teil dieser Datei – eigener
Publish-Workflow, noch nicht entworfen.

## Branch-Schutz und externe Partner

Externe Partner arbeiten mit der Rolle **Write** direkt in diesem Repo.
Geschützt wird über zwei Mechanismen: Rulesets mit Code-Owner-Freigabe
(GitHub-Einstellungen, keine Dateien) und den Wächter aus Modul J
(`partner_collaboration`), der Pull Requests nach `main` nur von
`develop` oder `hotfix/*` und nur aus diesem Repo zulässt (keine Forks).

**Zugehörige Dateien:**

- `.github/CODEOWNERS` – Code Owner für alle Dateien (`*`) und eigens für
  `/.github/`. Von `modul_a.bat` mit den angegebenen Code-Owner-Handles
  erzeugt (nicht mit dem Konto der Module, sofern abweichend); alle
  Code Owner brauchen Schreibrecht im Repo. Bei Organisationen ggf. von
  Hand auf ein Team (`@organisation/team`) umstellen.
  GitHub liest immer die Fassung auf dem **Zielbranch** des Pull
  Requests – die Datei muss daher auf `develop` **und** `main` liegen.
- `.github/workflows/branch_guard.yml` – dünne Aufruferdatei, Trigger
  `pull_request_target` gegen `main`, Job `branch-guard` (Name des
  erforderlichen Checks). Kontoname in der `uses:`-Zeile von
  `modul_a.bat` eingesetzt. Kein Checkout von Pull-Request-Code (Sicherheit bei
  `pull_request_target`). Erlaubte Quellbranches: Standardwert aus
  Modul J (`develop,hotfix/*`).

**Einrichtung durch den Administrator – Reihenfolge einhalten:**

1. **Standardbranch** auf `develop` stellen (Settings > General >
   Default branch).
2. `CODEOWNERS`, `validate.yml` und `branch_guard.yml` per Pull Request
   gegen `develop` einbringen.
3. Einmal Pull Request `develop` → `main`, damit die Dateien auch auf
   `main` liegen. Der Wächter läuft bei diesem ersten Pull Request noch
   nicht – `pull_request_target` liest die Workflow-Datei vom Zielbranch,
   und dort liegt sie erst nach diesem Merge.
4. Erst danach in `main-protect` die Checks `validierung` und
   `branch-guard` als erforderlich eintragen – sie stehen erst nach einem
   ersten Lauf zur Auswahl.
5. `develop-protect` und `main-protect`: Code-Owner-Freigabe verlangen,
   1 Freigabe. Bypass nur für die Rolle „Repository admin", Modus „nur
   für Pull Requests" (nötig, weil GitHub Autoren ihre eigenen Pull
   Requests nicht freigeben lässt). Bei einem Repo im persönlichen Konto
   prüfen, ob diese Rolle wählbar ist (siehe `OPEN_ISSUES.md`).
6. Eigenes Ruleset für `hotfix/*` mit „Restrict creations" – Bypass wie
   oben, damit nur der Administrator Hotfix-Branches anlegt.
7. Settings > Actions > General: Workflows aus Fork-Pull-Requests nur
   nach Freigabe ausführen, Einstellung sinngemäß „Require approval for
   all outside collaborators" (Bezeichnung kann je nach GitHub-Stand
   abweichen, z. B. „external contributors").
8. Erst danach Partner einladen (Settings > Collaborators, Rolle
   **Write**). In einem öffentlichen Repo **keinen** `SUBMODULE_PAT`
   hinterlegen – `validate.yml` nutzt dann automatisch den
   `github.token`.

**Hotfix-Ablauf:** Der Administrator legt `hotfix/…` von `main` aus an,
Pull Request `hotfix/…` → `main`, danach von Hand Pull Request `main` →
`develop`, damit die Korrektur auch in `develop` ankommt. Eine
Automatik für die Rückführung ist bewusst zurückgestellt.

**Voraussetzung für private Repos:** Bei GitHub Free wirken Rulesets nur
in öffentlichen Repos. Private Nutzung mit externen Partnern setzt
GitHub Team voraus.

## Wichtige praktische Hinweise

**A muss ohne B funktionieren.** Deshalb führt A eigene, vollständige
Default-Werte in `metadata/valuelists.xml` (status/translation-status,
1:1 aus dem Modul-E-Vorschlag übernommen) und `publishing/design-values.xml`
(`heading-color` = `#1A3E5C`, Vorschlag Modul-G-Chat, von H übernommen).

**Titelseite/Impressum:** `titlepage.dita` liefert nur die Daten für
DITA-OT's eingebauten Titelseiten-Mechanismus (rendert selbst keine
Seite), `imprint.dita` ist eine vollständige eigene Seite. Beide über
`topicref` in `project_content.ditamap` eingebunden, Adress-/Firmendaten
über die neuen Keys in `project_names.ditamap` (`businessunit`, `docdate`,
`legalname`, `street`, `housenumber`, `postalcode`, `city`,
`addressaddition`, `website`, `email`) – `doc-type`/`doc-id` bewusst keine
eigenen Keys, G liest sie automatisch aus `project_content.ditamap`.
**Die Absatzreihenfolge in `imprint.dita` ist seit dem generischen
Impressum-Rendering bindend für die Ausgabereihenfolge** (nicht mehr nur
kosmetisch) – `website`/`email` stehen direkt nach `address-addition`,
vor `doc-date`.

**Retroaktive Nachprüfung durch C:** Erledigt. Konventionsprüfung
(DOCTYPE-Version 1.3, `xml:lang`) und vollständige DTD-/Referenzprüfung
(`--root`) liefen im Pilot real durch (`dita_validation` v1.0.1).

**Platzhalter-Notation:** Content-Platzhalter verwenden den ausformulierten
Satz „Platzhaltertext – durch echten Baustein ersetzen oder löschen."
Identifikator-Platzhalter (Dateiname `[thema]`, `id`-Attribut `[typ]_0000`)
sind davon nicht betroffen.

**Topic-Benennungskonvention:** `[typ]_[nnnn]_[thema].dita`, `id`-Attribut
`[typ]_[nnnn]` (vierstellige, je Typ getrennt gezählte Nummer). Vorlagedateien
tragen die reservierte Nummer `0000`. `[thema]` muss nicht eindeutig sein und
kann jederzeit umbenannt werden, ohne Nummer/`id` zu ändern. Reuse-Container
(`c_reuse.dita` usw.) sind von der Nummerierung ausgenommen.

**Prolog-Basisvorlage:** Alle Topics führen `audience` (leer),
`othermeta[status]` (Default `draft`) und `othermeta[lifecycle-stage]`
(leer) in `<metadata>`, in der Reihenfolge `audience` → `prodinfo` →
`othermeta`.
