import json

import pytest

from anagnosis.corpora import LicenseError, load

YAML = """\
name: tiny
source: https://example.org/tiny
license: {license}
citation: Tiny corpus, 2026.
lang: en
label:
  type: ordinal
  levels: [grade1, grade2, grade3]
  ages: [6.5, 7.5, 8.5]
"""


def write(tmp_path, license="CC-BY-4.0", records=None):
    d = tmp_path / "tiny"
    d.mkdir()
    (d / "corpus.yaml").write_text(YAML.format(license=license))
    records = records or [{"id": "a", "text": "The dog ran.", "label": "grade1"},
                          {"id": "b", "text": "It was a long day.", "label": "grade3", "group": "s1"}]
    (d / "texts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    return d


def test_loads_metadata_and_records(tmp_path):
    c = load(write(tmp_path))
    assert (c.name, c.lang, c.label_type, c.levels) == ("tiny", "en", "ordinal", ["grade1", "grade2", "grade3"])
    assert [d.id for d in c.docs] == ["a", "b"]
    assert [d.level for d in c.docs] == [0, 2]
    assert c.docs[1].group == "s1" and c.docs[0].group is None


def test_ages_follow_levels(tmp_path):
    c = load(write(tmp_path))
    assert c.age_of(2) == 8.5


@pytest.mark.parametrize("lic", ["CC-BY-4.0", "CC-BY-3.0", "CC0-1.0", "public-domain"])
def test_open_licenses_pass(tmp_path, lic):
    assert load(write(tmp_path, lic)).license == lic


@pytest.mark.parametrize("lic", ["CC-BY-NC-4.0", "CC-BY-SA-4.0", "CC-BY-NC-SA-4.0", "unknown"])
def test_other_licenses_are_refused(tmp_path, lic):
    with pytest.raises(LicenseError):
        load(write(tmp_path, lic))


def test_label_outside_the_scale_is_an_error(tmp_path):
    with pytest.raises(ValueError, match="grade9"):
        load(write(tmp_path, records=[{"id": "a", "text": "x", "label": "grade9"}]))
