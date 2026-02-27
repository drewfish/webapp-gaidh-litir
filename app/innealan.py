from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from typing import Any
import re
from fastapi import APIRouter, Request

from .dependencies import ClàranDep, RendererDep
from .seorsachan import Clàr

router = APIRouter()

SEÒRSACHAN_TAGHTA: dict[str, str] = {
    "boir.": "feminine noun",
    "bua.": "adjective",
    "co-ghn.": "adverb",
    "cst.": "question",
    "fir.": "masculine noun",
    "gn.": "verb",
    "m.-fh.": "partical",
    "nsg.": "conjuction",
    "roi. gin.": "preposition + genitive",
    "roi.": "preposition",
}


class Sìolan(ABC):
    @abstractmethod
    def maidsich(self, clàr: Clàr) -> bool: ...


@dataclass
class SìolanFacal(Sìolan):
    breacan: str
    roghainnean: int = 0

    def maidsich(self, clàr: Clàr) -> bool:
        maids = re.search(self.breacan, clàr["facal"], self.roghainnean)
        return maids is not None


@dataclass
class SìolanBeurla(Sìolan):
    breacan: str

    def maidsich(self, clàr: Clàr) -> bool:
        maids = False
        for beurla in clàr["Beurla"]:
            if self.breacan in beurla:
                maids = True
                break
        return maids


class SìolanLitricheanAnComas(Sìolan):
    litrichean: str

    def __init__(self, litrichean: str) -> None:
        self.litrichean = "".join(sorted(litrichean.replace(" ", "")))
        super().__init__()

    def maidsich(self, clàr: Clàr) -> bool:
        # This approach allows the searcher to find words with -multiples-
        # of the same letter, e.g. "nn" for words with at-least-two-n.
        eirmeas = self.litrichean
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
        return clàr["seòrsa"] in self.seòrsachan


@dataclass
class LorgFaclanIonchur:
    toiseach: str = ""
    gach_aite: str = ""
    deireadh: str = ""
    litrn_tha: str = ""
    litrn_chan: str = ""
    beurla: str = ""
    fad_coimheas: str = ""
    fad_teorr: int = 0
    seorsa: list[str] = field(default_factory=list)

    def bhon_fastapi(self, ionchur: Any) -> None:
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

    def gu_dict(self) -> dict[str, Any]:
        return asdict(self)


@router.get("/lorg-faclan")
@router.post("/lorg-faclan")
async def lorg_faclan(
    clàran: ClàranDep,
    request: Request,
    render: RendererDep,
) -> Any:
    ionchur = LorgFaclanIonchur()
    if request.query_params:
        ionchur.bhon_fastapi(request.query_params)
    fuirm = await request.form(max_files=0)
    if fuirm:
        ionchur.bhon_fastapi(fuirm)

    sìolanan: list[Sìolan] = []
    if ionchur.toiseach:
        sìolanan.append(SìolanFacal(breacan="^" + re.escape(ionchur.toiseach)))
    if ionchur.gach_aite:
        sìolanan.append(SìolanFacal(breacan=re.escape(ionchur.gach_aite)))
    if ionchur.deireadh:
        sìolanan.append(SìolanFacal(breacan=re.escape(ionchur.deireadh) + "$"))
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
        for clàr in clàran:
            # FUTURE -- support phrases perhaps
            if " " in clàr["facal"]:
                continue
            maids: bool = True
            for sìolan in sìolanan:
                if not sìolan.maidsich(clàr):
                    maids = False
                    break
            if maids:
                air_sgeul.append(clàr)

    return render(
        "inneal/lorg-faclan.html",
        clàran=air_sgeul,
        SEÒRSACHAN_TAGHTA=SEÒRSACHAN_TAGHTA,
        ionchur=ionchur.gu_dict(),
    )
