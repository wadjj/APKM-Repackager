"""Logic for filtering split APK files extracted from an APKM archive."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set


DPI_ORDER = [
    "ldpi",
    "mdpi",
    "tvdpi",
    "hdpi",
    "xhdpi",
    "xxhdpi",
    "xxxhdpi",
]


@dataclass
class SplitInfo:
    """Metadata extracted from a split APK filename."""

    path: Path
    qualifiers: Set[str]
    abis: Set[str]
    dpis: Set[str]
    languages: Set[str]

    @property
    def name(self) -> str:
        return self.path.name


def parse_split(path: Path) -> SplitInfo:
    name = path.name
    qualifiers = set()
    abis: Set[str] = set()
    dpis: Set[str] = set()
    languages: Set[str] = set()

    if name.startswith("config."):
        qualifier_block = name[len("config.") : name.rfind(".apk")]
        for qualifier in qualifier_block.split("."):
            qualifier = qualifier.lower()
            qualifiers.add(qualifier)
            if qualifier in {"armeabi_v7a", "arm64_v8a", "x86", "x86_64"}:
                abis.add(qualifier)
            elif qualifier in set(DPI_ORDER):
                dpis.add(qualifier)
            elif qualifier == "nores":
                # Some splits denote missing resources; treat as neutral.
                continue
            else:
                if len(qualifier) <= 5 and qualifier.replace("-", "").isalpha():
                    languages.add(qualifier)
    return SplitInfo(path=path, qualifiers=qualifiers, abis=abis, dpis=dpis, languages=languages)


def order_for_dpi(dpi: str) -> int:
    try:
        return DPI_ORDER.index(dpi)
    except ValueError:
        return len(DPI_ORDER)


def should_keep_split(
    split: SplitInfo,
    allowed_abis: Iterable[str],
    allowed_languages: Iterable[str],
    max_dpi: str,
) -> bool:
    allowed_abis_set = set(allowed_abis)
    allowed_languages_set = {lang.lower() for lang in allowed_languages}
    split_dpi_threshold = order_for_dpi(max_dpi)

    if split.abis and not (split.abis & allowed_abis_set):
        return False

    if split.languages and not (split.languages & allowed_languages_set):
        return False

    if split.dpis:
        max_split_dpi = max(order_for_dpi(dpi) for dpi in split.dpis)
        if max_split_dpi > split_dpi_threshold:
            return False

    return True


def filter_splits(
    split_paths: Iterable[Path],
    allowed_abis: Iterable[str],
    allowed_languages: Iterable[str],
    max_dpi: str,
) -> List[Path]:
    kept: List[Path] = []
    for path in split_paths:
        info = parse_split(path)
        if should_keep_split(info, allowed_abis, allowed_languages, max_dpi):
            kept.append(path)
    return kept
