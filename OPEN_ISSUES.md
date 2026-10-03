# Offene Punkte - Modul A (project_content)

- Kontoname aufweiss01 wurde beim Anlegen in validate.yml, branch_guard.yml
  und CODEOWNERS eingesetzt. Bei einer Organisation pruefen, ob
  CODEOWNERS ein Team (@organisation/team) statt des Kontos nennen soll.
- Branch-Schutz und externe Partner einrichten (Entscheidungen
  28.09.2026) - GitHub-Einstellungen, keine Dateien. Reihenfolge und
  Details siehe README.md, Abschnitt "Branch-Schutz und externe Partner":
  a) Standardbranch develop; b) CODEOWNERS/validate.yml/branch_guard.yml
  per Pull Request gegen develop; c) einmal Pull Request develop nach
  main; d) danach in main-protect "validierung" und "branch-guard" als
  erforderliche Checks; e) Code-Owner-Freigabe, Bypass nur Repository
  admin fuer Pull Requests; f) Ruleset hotfix/* mit Restrict creations;
  g) Freigabe von Fork-Workflows fuer alle Externen; h) erst dann
  Partner einladen (Rolle Write).
- Offen, im Pilot zu verifizieren: Ist die Bypass-Rolle
  "Repository admin" bei einem Repo im persoenlichen Konto (keine
  Organisation) in den Rulesets waehlbar? Ergebnis an den
  Planungs-Chat melden.
- Private Nutzung mit externen Partnern setzt GitHub Team voraus - bei
  GitHub Free wirken Rulesets nur in oeffentlichen Repos.
- Uebersetzungsinhalte: bewusst kein Vorlagenordner in A angelegt. Loesung
  folgt ueber das perspektivische Modul L (content_translation,
  Konfigurationsprotokoll v22, Abschnitt 9), sobald dieses ausgearbeitet ist.
- G/H (Publish) sind ausdruecklich NICHT Teil von validate.yml
  (Abschnitt 6) - eigener Publish-Workflow noch nicht entworfen,
  Trigger-Mechanismus offen (Abschnitt 8).
