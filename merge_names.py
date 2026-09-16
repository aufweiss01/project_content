#!/usr/bin/env python3
"""
merge_names.py - Modul A (document_content)

Fuehrt VOR C's --root-Pruefung UND vor dem G/H-Build EINMALIG einen Merge
von A's project_names.ditamap mit B's shared_names.ditamap durch und
ueberschreibt project_names.ditamap in-place - NUR im CI-Checkout, das
Ergebnis wird nie zurueck committet/gepusht.

Wichtig: EIN Merge-Lauf genuegt. project_names.ditamap ist bereits ueber
reusables.ditamap per mapref in project_content.ditamap eingehaengt - das
ist dieselbe Kette, die sowohl C's "dita -v -i docs/project_content.ditamap
--root" als auch G's/H's Build durchlaufen. Beide sehen das gemergte
Ergebnis danach automatisch ueber den normalen DITA-OT-mapref-Mechanismus -
kein separater Merge-Lauf oder eigener Dateipfad fuer C vs. G/H noetig.

Regel (Konfigurationsprotokoll v17, Abschnitt 6, companyname-Override):
A gewinnt bei ueberschneidenden keydef-keys. B liefert zusaetzlich alle
Keys, die es nur in B gibt. Funktioniert generisch fuer beliebige Keys
(nicht nur companyname) - MIT EINER BEKANNTEN GRENZE:

Bekannte Grenze: Wenn ein einzelnes <keydef keys="..."> mehrere Keys
traegt und diese Keys sich TEILWEISE zwischen A und B ueberschneiden
(z. B. A definiert keys="foo bar", B definiert keys="bar baz" - "bar"
ueberschneidet sich, "foo" nur A, "baz" nur B), werden nicht sauber
getrennte Keydefs erzeugt. Das eine Element wird komplett uebernommen
oder komplett verworfen, nie key-weise aufgesplittet. Das kann zu
doppelt definierten Keys im Ergebnis fuehren. Sauberes Aufloesen
braeuchte echtes Splitten der betroffenen keydef-Elemente in
Einzel-Key-Keydefs vor dem Merge - hier bewusst nicht umgesetzt, da im
aktuellen Bestand jedes keydef nur einen Key traegt. Mehrfach-Key-keydefs
mit Teil-Ueberschneidung vor Gebrauch manuell pruefen.

Wird von A's eigener validate.yml aufgerufen - NICHT von Modul C, das rein
pruefend bleibt und keine Build-Artefakte erzeugt. Die aufrufende Pipeline
entscheidet, ob B ueberhaupt eingebunden ist (Submodul-Ordner vorhanden);
dieses Skript selbst prueft das nicht und laeuft bedingungslos, wenn
aufgerufen.

Aufruf:
    python merge_names.py --a docs/reuse/project_names.ditamap \
                           --b <pfad-zu-shared_names.ditamap-in-B> \
                           [--out <ziel, Default: ueberschreibt --a>]

Exit-Code:
    0 - Merge erfolgreich (auch wenn keine Ueberschneidung vorhanden war)
    2 - Aufruffehler (Datei fehlt, nicht wohlgeformtes XML, kein <map>-Root)
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def lade_keydefs(pfad):
    """
    Liest alle direkten <keydef keys="..."> Kindelemente einer .ditamap.
    Gibt ein Dict key -> keydef-Element zurueck.
    """
    try:
        baum = ET.parse(pfad)
    except ET.ParseError as e:
        raise ValueError(f"{pfad} ist nicht wohlgeformtes XML: {e}")

    wurzel = baum.getroot()
    if wurzel.tag != "map":
        raise ValueError(f"Wurzelelement ist nicht <map>: {pfad}")

    keydefs = {}
    for element in wurzel.findall("keydef"):
        for key in element.get("keys", "").split():
            keydefs[key] = element
    return keydefs


def merge(a_pfad, b_pfad):
    """
    Merged die keydef-Elemente aus a_pfad und b_pfad. A gewinnt bei
    ueberschneidenden Keys. Gibt (finale_keydefs, log) zurueck, wobei log
    eine Liste von (key, quelle)-Tupeln fuer die Konsolenausgabe ist.

    Dedupliziert nach Element-IDENTITAET (id()), nicht nach Key: ein
    <keydef keys="foo bar"> traegt zwei Keys im selben Element - ohne
    diese Absicherung wuerde es einmal pro Key (also doppelt) in
    finale_keydefs landen. Siehe Modul-Docstring fuer die verbleibende
    Grenze bei TEILWEISER Key-Ueberschneidung innerhalb eines Elements.
    """
    a_keydefs = lade_keydefs(a_pfad)
    b_keydefs = lade_keydefs(b_pfad)

    log = []
    finale_keydefs = []
    gesehene_keys = set()
    uebernommene_elemente = set()

    for key, element in a_keydefs.items():
        gesehene_keys.add(key)
        log.append((key, "A"))
        if id(element) not in uebernommene_elemente:
            finale_keydefs.append(element)
            uebernommene_elemente.add(id(element))

    for key, element in b_keydefs.items():
        if key in gesehene_keys:
            log.append((key, "B (durch A ueberschrieben, verworfen)"))
            continue
        gesehene_keys.add(key)
        log.append((key, "B"))
        if id(element) not in uebernommene_elemente:
            finale_keydefs.append(element)
            uebernommene_elemente.add(id(element))

    return finale_keydefs, log


def schreibe_ergebnis(a_pfad, ziel_pfad, finale_keydefs):
    """
    Schreibt eine neue .ditamap mit demselben DOCTYPE/xml:lang wie A's
    Original und den gemergten keydef-Elementen als einzigem Inhalt.
    Setzt Einrueckung manuell, da ElementTree beim Verschieben von
    Elementen zwischen Baeumen die text-/tail-Whitespace-Attribute nicht
    automatisch angleicht.
    """
    baum = ET.parse(a_pfad)
    wurzel = baum.getroot()

    for element in list(wurzel.findall("keydef")):
        wurzel.remove(element)

    wurzel.text = "\n  "
    for i, element in enumerate(finale_keydefs):
        element.tail = "\n  " if i < len(finale_keydefs) - 1 else "\n"
        wurzel.append(element)

    ET.indent(baum, space="  ")

    with open(ziel_pfad, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA 1.3 Map//EN" "map.dtd">\n')
        baum.write(f, encoding="unicode")
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Modul A - Merge von project_names.ditamap mit B's shared_names.ditamap."
    )
    parser.add_argument("--a", required=True, help="Pfad zu A's project_names.ditamap")
    parser.add_argument("--b", required=True, help="Pfad zu B's shared_names.ditamap")
    parser.add_argument("--out", default=None, help="Zielpfad, Default: ueberschreibt --a")
    args = parser.parse_args()

    ziel = args.out or args.a

    try:
        finale_keydefs, log = merge(args.a, args.b)
    except (ValueError, FileNotFoundError) as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 2

    schreibe_ergebnis(args.a, ziel, finale_keydefs)

    print(f"Merge abgeschlossen: {ziel}")
    for key, quelle in log:
        print(f"  {key}: {quelle}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
