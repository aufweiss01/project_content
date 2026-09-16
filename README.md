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
├── .github/workflows/validate.yml  ← ruft C, D, E, F zu festen Versionen auf (Platzhalter)
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
modul_a.bat
```

Legt die Struktur relativ zum Speicherort der `.bat`-Datei an (nicht
relativ zum aktuellen Arbeitsverzeichnis der Eingabeaufforderung), bricht
ab, wenn der Zielordner `project_content` bereits existiert.

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

Aufruf (aktuell noch nicht in `validate.yml` verdrahtet, siehe
`OPEN_ISSUES.md`):

```cmd
python merge_names.py --a docs\reuse\project_names.ditamap --b <Pfad-zu-shared_names.ditamap-in-B>
```

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

**Retroaktive Nachprüfung durch C:** Die Konventionsprüfung
(DOCTYPE-Version 1.3, `xml:lang`) wurde bereits real gegen den aktuellen
Stand ausgeführt (15/15 Dateien fehlerfrei). Die vollständige
DTD-/Referenzprüfung (`validate_dita.py --root`) benötigt eine lokale
DITA-OT-Installation und steht noch aus – Befehl siehe `OPEN_ISSUES.md`.

**Benennungskonvention für neue Topics (entschieden, September 2026):**
Dateiname `[typ]_[nnnn]_[thema].dita`, `id`-Attribut `[typ]_[nnnn]`
(vierstellige, je Topic-Typ getrennt gezählte Nummer, 0001–9999).
`[thema]` muss nicht eindeutig sein - die Eindeutigkeit stellt allein
`[typ]_[nnnn]` sicher, und `[thema]` kann jederzeit umbenannt werden,
ohne die Nummer zu ändern. Die Vorlagedatei je Typ trägt die reservierte
Nummer `0000`. Beim Anlegen eines neuen Topics: Vorlage kopieren,
nächste freie Nummer des jeweiligen Typs vergeben, `[thema]` durch
einen sprechenden Kurztitel ersetzen (Dateiname und `id` gleichermaßen).

**Platzhalter-Notation:** Content-Platzhalter verwenden den ausformulierten
Satz „Platzhaltertext – durch echten Baustein ersetzen oder löschen."
Identifikator-Platzhalter (Dateiname-Bestandteil `[thema]`)
sind davon nicht betroffen.

**Prolog-Basisvorlage:** Alle Topics führen `audience` (leer),
`othermeta[status]` (Default `draft`) und `othermeta[lifecycle-stage]`
(leer) in `<metadata>`, in der Reihenfolge `audience` → `prodinfo` →
`othermeta`.
