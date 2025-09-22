import pytest
from ie_eval.metrics.nerval import nerval

from tests.od import FIXTURES


@pytest.mark.parametrize("by_category", [True, False])
def test_compute_nerval(by_category):
    table = nerval(
        label_dir=FIXTURES / "labels",
        prediction_dir=FIXTURES / "predictions",
        nerval_threshold=30,
        by_category=by_category,
    )

    # Check the printed Markdown table
    suffix = "_by_category" if by_category else ""
    assert table.get_string() == (FIXTURES / f"nerval{suffix}.md").read_text()
