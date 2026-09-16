# Offene Punkte - Modul A (project_content)

- .github\workflows\validate.yml ruft C und D konkret auf, E und F
  optional ueber vars.USE_MODULE_E/vars.USE_MODULE_F (Abschnitt 6).
  Vor dem ersten echten Lauf: Platzhalter "^<org^>" in allen "uses:"-
  Zeilen durch den tatsaechlichen GitHub-Kontonamen von C-H ersetzen.
- Die Push-/Merge-Unterscheidung in validate.yml (pull_request- vs.
  push-Event auf develop, fuer D's --files-/--input-Modus) ist eine
  Auslegung des Planungs-Chats, noch nicht real gegen einen echten
  PR/Merge verifiziert - vor produktivem Branch-Schutz nachholen.
- Retroaktive Nachpruefung von A durch C (Konfigurationsprotokoll v21,
  Abschnitt 8): Konventionspruefung (DOCTYPE-Version 1.3, xml:lang) am
  05.09.2026 real mit validate_dita.py gegen den aktuellen Stand von A
  ausgefuehrt - 15/15 Dateien fehlerfrei. Die DTD-/Referenzpruefung
  (Mechanismus 1, benoetigt DITA-OT) sowie die transitive Pruefung
  (--root docs\project_content.ditamap) stehen noch aus - lokal
  nachholen: python validate_dita.py --input project_content
  --root project_content\docs\project_content.ditamap
- Uebersetzungsinhalte: bewusst kein Vorlagenordner in A angelegt. Loesung
  folgt ueber das perspektivische Modul L (content_translation,
  Konfigurationsprotokoll v21, Abschnitt 9), sobald dieses ausgearbeitet ist.
- Benennungskonvention fuer neue Topics: [typ]_[nnnn]_[thema].dita,
  id="[typ]_[nnnn]" (vierstellige Nummer je Topic-Typ, 0001-9999;
  0000 ist der Vorlagendatei vorbehalten). Die automatische Pruefung
  auf Muster-Einhaltung und doppelt vergebene Nummern (Erweiterung
  von Modul C) ist noch nicht umgesetzt - bis dahin manuell auf
  eindeutige Nummern achten, insbesondere bei parallelen Branches.
- merge_names.py (companyname-Override, Abschnitt 6) ist in validate.yml
  verdrahtet (B-Submodul-Check plus Aufruf vor Modul C).
