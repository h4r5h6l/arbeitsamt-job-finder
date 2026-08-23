"""Typed models for search results and job details.

Field names mirror the LIVE API responses:

- Search (`/pc/v6/jobs`): top-level ``ergebnisliste``, each item uses
  ``referenznummer`` / ``stellenangebotsTitel`` / ``firma``.
- Details (`/pc/v4/jobdetails/{base64(refnr)}`): includes
  ``stellenangebotsBeschreibung``.

The bundesAPI OpenAPI spec documents different names (``stellenangebote``,
``refnr``, ``stitel``...). The ``_pick`` helper accepts both naming schemes
so the models stay correct regardless of drift.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


def _pick(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first non-None value found for any of ``keys`` in ``d``."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


@dataclass
class Adresse:
    plz: Optional[str] = None
    ort: Optional[str] = None
    region: Optional[str] = None
    land: Optional[str] = None

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "Adresse":
        return cls(
            plz=str(_pick(d, "plz", default="") or ""),
            ort=_pick(d, "ort"),
            region=_pick(d, "region"),
            land=_pick(d, "land"),
        )


@dataclass
class Stellenlokation:
    adresse: Optional[Adresse] = None
    breite: Optional[float] = None  # latitude
    laenge: Optional[float] = None  # longitude

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "Stellenlokation":
        koord = _pick(d, "koordinaten") or {}
        if isinstance(koord, dict):
            return cls(
                adresse=Adresse.from_api(d["adresse"]) if d.get("adresse") else None,
                breite=_pick(d, "breite", default=koord.get("lat")),
                laenge=_pick(d, "laenge", default=koord.get("lon")),
            )
        return cls(
            adresse=Adresse.from_api(d["adresse"]) if d.get("adresse") else None,
            breite=_pick(d, "breite"),
            laenge=_pick(d, "laenge"),
        )
@dataclass
class JobSearchResult:
    referenznummer: Optional[str] = None
    titel: Optional[str] = None
    beruf: Optional[str] = None
    arbeitgeber: Optional[str] = None
    stellenangebotsart: Optional[str] = None
    externe_url: Optional[str] = None
    homeoffice_moeglich: Optional[bool] = None
    vollzeit: Optional[bool] = None
    teilzeit_flexibel: Optional[bool] = None
    eintrittsdatum: Optional[str] = None
    veroeffentlicht_am: Optional[str] = None
    lokationen: list[Stellenlokation] = field(default_factory=list)
    entfernung_km: Optional[int] = None
    alle_berufe: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "JobSearchResult":
        zeitraum = _pick(d, "eintrittszeitraum") or {}
        return cls(
            referenznummer=_pick(d, "referenznummer", "refnr"),
            titel=_pick(d, "stellenangebotsTitel", "titel", "beruf"),
            beruf=_pick(d, "hauptberuf", "beruf"),
            arbeitgeber=_pick(d, "firma", "arbeitgeber"),
            stellenangebotsart=_pick(d, "stellenangebotsart", "angebotsart"),
            externe_url=_pick(d, "externeURL", "externeUrl"),
            homeoffice_moeglich=d.get("homeofficemoeglich"),
            vollzeit=d.get("arbeitszeitVollzeit"),
            teilzeit_flexibel=d.get("arbeitszeitTeilzeitFlexibel"),
            eintrittsdatum=zeitraum.get("von") or d.get("eintrittsdatum"),
            veroeffentlicht_am=_pick(
                d, "datumErsteVeroeffentlichung", "aktuelleVeroeffentlichungsdatum"
            ),
            lokationen=[
                Stellenlokation.from_api(loc)
                for loc in (_pick(d, "stellenlokationen", "arbeitsorte") or [])
            ],
            entfernung_km=d.get("entfernung"),
            alle_berufe=list(d.get("alleBerufe") or []),
            raw=d,
        )


@dataclass
class JobDetails:
    referenznummer: Optional[str] = None
    titel: Optional[str] = None
    arbeitgeber: Optional[str] = None
    beschreibung: Optional[str] = None
    verguetung: Optional[str] = None
    vertragsdauer: Optional[str] = None
    homeoffice_moeglich: Optional[bool] = None
    vollzeit: Optional[bool] = None
    eintrittsdatum: Optional[str] = None
    arbeitgeber_kundennummer_hash: Optional[str] = None
    ist_geringfuegig: Optional[bool] = None
    quereinstieg_geeignet: Optional[bool] = None
    lokationen: list[Stellenlokation] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "JobDetails":
        zeitraum = _pick(d, "eintrittszeitraum") or {}
        return cls(
            referenznummer=_pick(d, "referenznummer", "refnr"),
            titel=_pick(d, "stellenangebotsTitel", "titel"),
            arbeitgeber=_pick(d, "firma", "arbeitgeber"),
            beschreibung=_pick(d, "stellenangebotsBeschreibung", "stellenbeschreibung"),
            verguetung=_pick(d, "verguetungsangabe", "verguetung"),
            vertragsdauer=d.get("vertragsdauer"),
            homeoffice_moeglich=d.get("homeofficemoeglich"),
            vollzeit=d.get("arbeitszeitVollzeit"),
            eintrittsdatum=zeitraum.get("von") or d.get("eintrittsdatum"),
            arbeitgeber_kundennummer_hash=_pick(
                d, "arbeitgeberKundennummerHash", "kundennummerHash"
            ),
            ist_geringfuegig=d.get("istGeringfuegigeBeschaeftigung"),
            quereinstieg_geeignet=d.get("quereinstiegGeeignet"),
            lokationen=[
                Stellenlokation.from_api(loc)
                for loc in (_pick(d, "stellenlokationen", "arbeitsorte") or [])
            ],
            raw=d,
        )


@dataclass
class JobSearchResponse:
    results: list[JobSearchResult]
    max_ergebnisse: int = 0
    page: int = 1
    size: int = 0
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "JobSearchResponse":
        items = _pick(d, "ergebnisliste", "stellenangebote", default=[]) or []
        return cls(
            results=[JobSearchResult.from_api(i) for i in items],
            max_ergebnisse=int(d.get("maxErgebnisse") or 0),
            page=int(d.get("page") or 1),
            size=int(d.get("size") or 0),
            raw=d,
        )