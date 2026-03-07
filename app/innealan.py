from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from typing import Any
import re
from fastapi import APIRouter, Request

from .eisimealachdan import FaclanDep, RendererDep
from .seorsachan import Clàr

router = APIRouter()

SEÒRSACHAN_AN_COMAS: dict[str, str] = {
    "boir.": "ainmear boireannta (feminine noun)",
    "bua.": "buadhair (adjective)",
    "co-ghn.": "co-ghnìomhair (adverb)",
    "cst.": "ceisteach (interrogative)",
    "fir.": "ainmear fireannta (masculine noun)",
    "gn.": "gnìomhair (verb)",
    "m.-fh.": "mion-fhacal (partical)",
    "nsg.": "naisgear (conjuction)",
    "roi. gin.": "roimhear le ginideach (preposition + genitive)",
    "roi.": "roimhear (preposition)",
}
FAD_COIMHEASAN: dict[str, str] = {
    "%3C": "lt",
    "%3C=": "le",
    "=": "eq",
    "%3E=": "ge",
    "%3E": "gt",
}


class Sìolan(ABC):
    @abstractmethod
    def maidsich(self, clàr: Clàr) -> bool: ...


@dataclass
class SìolanAnToiseach(Sìolan):
    breacan: str

    def maidsich(self, clàr: Clàr) -> bool:
        return clàr["facal"].startswith(self.breacan)


@dataclass
class SìolanÀiteSamBith(Sìolan):
    breacan: str

    def maidsich(self, clàr: Clàr) -> bool:
        return self.breacan in clàr["facal"]


@dataclass
class SìolanAnDeireadh(Sìolan):
    breacan: str

    def maidsich(self, clàr: Clàr) -> bool:
        return clàr["facal"].endswith(self.breacan)


class SìolanBeurla(Sìolan):
    faclan: list[str]

    def __init__(self, breacan: str) -> None:
        self.faclan = breacan.split(" ")

    def maidsich(self, clàr: Clàr) -> bool:
        for facal in self.faclan:
            maids = False
            for seòrsa in clàr["seòrsachan"]:
                for beurla in seòrsa["beurla"]:
                    if facal in beurla:
                        maids = True
            if not maids:
                return False
        return True


class SìolanLitricheanAnComas(Sìolan):
    litrichean: str

    def __init__(self, litrichean: str) -> None:
        self.litrichean = "".join(sorted(litrichean.replace(" ", "")))
        super().__init__()

    def maidsich(self, clàr: Clàr) -> bool:
        # This approach allows the searcher to find words with -multiples-
        # of the same letter, e.g. "nn" for words with at-least-two-n.
        eirmeas = self.litrichean
        if "litrichean" not in clàr:
            clàr["litrichean"] = "".join(sorted(clàr["facal"].replace(" ", "")))
        cuimse = clàr["litrichean"]
        if len(eirmeas) > len(cuimse):
            return False
        e = 0
        c = 0
        while True:
            if e >= len(eirmeas):
                return True
            if c >= len(cuimse):
                return False
            if eirmeas[e] == cuimse[c]:
                e += 1
                c += 1
                continue
            c += 1


class SìolanLitricheanÀComas(Sìolan):
    litrichean: set[str]

    def __init__(self, litrichean: str) -> None:
        self.litrichean = set(litrichean)
        super().__init__()

    def maidsich(self, clàr: Clàr) -> bool:
        for litir in self.litrichean:
            if litir in clàr["facal"]:
                return False
        return True


@dataclass
class SìolanFad(Sìolan):
    coimheas: str
    teòrr: int

    def maidsich(self, clàr: Clàr) -> bool:
        if not self.teòrr:
            return True
        fad = len(clàr["facal"])
        if self.coimheas == "eq":
            return fad == self.teòrr
        if self.coimheas == "lt":
            return fad < self.teòrr
        if self.coimheas == "le":
            return fad <= self.teòrr
        if self.coimheas == "gt":
            return fad > self.teòrr
        if self.coimheas == "ge":
            return fad >= self.teòrr
        # we shouldn't get here, likely somebody is hacking the HTML inputs
        return False


@dataclass
class SìolanSeòrsa(Sìolan):
    seòrsachan: list[str]

    def maidsich(self, clàr: Clàr) -> bool:
        for seòrsa in clàr["seòrsachan"]:
            if seòrsa["seòrsa"] in self.seòrsachan:
                return True
        return False


@dataclass
class LorgFaclanIonchur:
    toiseach: str = ""
    sam_bith: str = ""
    deireadh: str = ""
    litrn_tha: str = ""
    litrn_chan: str = ""
    beurla: str = ""
    fad_coimheas: str = ""
    fad_teorr: int = 0
    seorsa: list[str] = field(default_factory=list)

    def bhon_fastapi(self, ionchur: Any, sreang: bool = False) -> None:
        for f in fields(self):
            if f.type is str:
                luach = ionchur.get(f.name)
                if luach:
                    setattr(self, f.name, luach.strip())
            if f.type is int:
                luach = ionchur.get(f.name)
                if luach:
                    try:
                        luach_int = int(luach.strip())
                    except ValueError:
                        # we shouldn't get here, likely somebody is hacking
                        # the HTML inputs
                        continue
                    setattr(self, f.name, luach_int)
            if str(f.type) == "list[str]":
                luach = ionchur.getlist(f.name)
                if luach:
                    setattr(self, f.name, luach)
        if sreang:
            pàirtean = str(ionchur).split("?")[0].split("&")
            for pàirt in pàirtean:
                breacan = r"^fad(?P<coimheas>(%[0-9A-F][0-9A-F])?=?)(?P<teorr>\d+)"
                flags = re.IGNORECASE
                maids = re.search(breacan, pàirt, flags=flags)
                if maids:
                    coimheas = maids.group("coimheas")
                    self.fad_coimheas = FAD_COIMHEASAN.get(coimheas, "")
                    self.fad_teorr = int(maids.group("teorr"))

    def gu_dict(self) -> dict[str, Any]:
        return asdict(self)


@router.get("/lorg-faclan")
@router.post("/lorg-faclan")
async def lorg_faclan(
    faclan: FaclanDep,
    request: Request,
    render: RendererDep,
) -> Any:
    ionchur = LorgFaclanIonchur()
    if request.query_params:
        ionchur.bhon_fastapi(request.query_params, True)
    fuirm = await request.form(max_files=0)
    if fuirm:
        ionchur.bhon_fastapi(fuirm)

    sìolanan: list[Sìolan] = []
    if ionchur.toiseach:
        sìolanan.append(SìolanAnToiseach(breacan=ionchur.toiseach))
    if ionchur.sam_bith:
        sìolanan.append(SìolanÀiteSamBith(breacan=ionchur.sam_bith))
    if ionchur.deireadh:
        sìolanan.append(SìolanAnDeireadh(breacan=ionchur.deireadh))
    if ionchur.beurla:
        sìolanan.append(SìolanBeurla(breacan=ionchur.beurla))
    if ionchur.litrn_tha:
        sìolanan.append(SìolanLitricheanAnComas(litrichean=ionchur.litrn_tha))
    if ionchur.litrn_chan:
        sìolanan.append(SìolanLitricheanÀComas(litrichean=ionchur.litrn_chan))
    if ionchur.fad_teorr:
        sìolanan.append(
            SìolanFad(coimheas=ionchur.fad_coimheas, teòrr=ionchur.fad_teorr)
        )
    if ionchur.seorsa:
        sìolanan.append(SìolanSeòrsa(seòrsachan=ionchur.seorsa))
    air_sgeul: list[Clàr] = []
    if sìolanan:
        for clàr in faclan:
            maids: bool = True
            for sìolan in sìolanan:
                if not sìolan.maidsich(clàr):
                    maids = False
                    break
            if maids:
                air_sgeul.append(clàr)

    return render(
        "inneal/lorg-faclan.html",
        faclan=air_sgeul,
        SEÒRSACHAN_AN_COMAS=SEÒRSACHAN_AN_COMAS,
        ionchur=ionchur.gu_dict(),
    )
