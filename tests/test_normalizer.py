from src.io.normalizer import normalize_multi_value, normalize_token, split_multi_value


def test_split_multi_value() -> None:
    assert split_multi_value("Python| SQL |Azure") == ["Python", "SQL", "Azure"]


def test_alias_normalization() -> None:
    assert normalize_token("K8s") == "kubernetes"
    assert normalize_token(" Node ") == "node.js"


def test_normalize_multi_value_handles_blank() -> None:
    assert normalize_multi_value("") == []
    assert normalize_multi_value(None) == []
