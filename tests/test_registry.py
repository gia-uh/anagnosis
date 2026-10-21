import re
from pathlib import Path

from anagnosis.extractors import ALL

BIB = Path(__file__).parent.parent / "research" / "references.bib"


def test_every_feature_source_is_in_the_bibliography():
    keys = set(re.findall(r"@\w+\{([^,]+),", BIB.read_text()))
    cited = {k for e in ALL for f in e.features for k in f.source.split(";") if k != "anagnosis"}
    assert cited <= keys, cited - keys


def test_feature_names_are_unique():
    names = [f.name for e in ALL for f in e.features]
    assert len(names) == len(set(names))
