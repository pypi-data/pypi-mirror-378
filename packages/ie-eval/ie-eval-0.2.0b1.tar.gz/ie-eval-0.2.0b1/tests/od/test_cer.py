"""Computing CER/WER."""

import pytest
from bio_parser import GLOBAL_STAT_NAME
from ie_eval.metrics.cer import (
    TextEval,
    TotalScore,
    cerwer,
    format_string_for_cer,
    format_string_for_wer,
    make_prettytable,
    merge_entities,
)
from prettytable import PrettyTable

from tests.od import FIXTURES


@pytest.mark.parametrize(
    ("text", "expected_formatted_text"),
    [
        (
            "I took a train from Bordeaux to Nantes",
            "I took a train from Bordeaux to Nantes",
        ),
        (
            " I took a train from Bordeaux to Nantes ",
            "I took a train from Bordeaux to Nantes",
        ),
        (
            " I took a train from     Bordeaux to Nantes  ",
            "I took a train from Bordeaux to Nantes",
        ),
    ],
)
def test_format_string_for_cer(text, expected_formatted_text):
    assert format_string_for_cer(text) == expected_formatted_text


@pytest.mark.parametrize(
    ("text", "expected_formatted_text"),
    [
        (
            "I took a train from Bordeaux to Nantes",
            ["I", "took", "a", "train", "from", "Bordeaux", "to", "Nantes"],
        ),
        (
            " I took     a train from Bordeaux    to Nantes   ",
            ["I", "took", "a", "train", "from", "Bordeaux", "to", "Nantes"],
        ),
    ],
)
def test_format_string_for_wer(text, expected_formatted_text):
    assert format_string_for_wer(text) == expected_formatted_text


@pytest.mark.parametrize(
    (
        "label",
        "prediction",
        "expected_char_errors",
        "expected_word_errors",
        "expected_total_chars",
        "expected_total_words",
    ),
    [
        (
            "I took a train from Bordeaux to Nantes",
            " I took     a train from Bordeaux    to Nantes   ",
            0,
            0,
            38,
            8,
        ),
        (
            "I took a train from Bordeaux to Nantes",
            "I took the plane from Bordeaux to Nantes",
            7,
            2,
            40,
            8,
        ),
        (
            "I took a train from Bordeaux to Nantes",
            "I like trains",
            28,
            7,
            38,
            8,
        ),
    ],
)
def test_text_eval(
    label,
    prediction,
    expected_char_errors,
    expected_word_errors,
    expected_total_chars,
    expected_total_words,
):
    score = TextEval(label, prediction)
    assert score.char_errors == expected_char_errors
    assert score.word_errors == expected_word_errors
    assert score.char_totals == expected_total_chars
    assert score.word_totals == expected_total_words


@pytest.mark.parametrize(
    (
        "errors_chars",
        "errors_words",
        "total_chars",
        "total_words",
        "total_counts",
        "expected_table",
    ),
    [
        (
            {"per": 13, "date": 0, GLOBAL_STAT_NAME: 17},
            {"per": 2, "date": 0, GLOBAL_STAT_NAME: 14},
            {"per": 123, "date": 100, GLOBAL_STAT_NAME: 250},
            {"per": 10, "date": 19, GLOBAL_STAT_NAME: 78},
            {"per": 20, "date": 13, GLOBAL_STAT_NAME: 50},
            """| Category | ECER (%) | EWER (%) | Support |
|:---------|:--------:|:--------:|--------:|
| date     |   0.00   |   0.00   |      13 |
| per      |  10.57   |  20.00   |      20 |
| total    |   6.80   |  17.95   |      50 |""",
        ),
    ],
)
def test_make_pretty_table(
    errors_chars,
    errors_words,
    total_chars,
    total_words,
    total_counts,
    expected_table,
):
    scores = TotalScore()
    scores.char_errors = errors_chars
    scores.word_errors = errors_words
    scores.char_totals = total_chars
    scores.word_totals = total_words
    scores.count = total_counts
    table = make_prettytable(scores)
    assert isinstance(table, PrettyTable)
    assert table.field_names == [
        "Category",
        "ECER (%)",
        "EWER (%)",
        "Support",
    ]
    assert table.get_string() == expected_table


@pytest.mark.parametrize(
    ("entities", "expected_dict"),
    [
        (
            [("per", "Marie"), ("date", "December"), ("event", "Christmas")],
            {"per": "Marie", "date": "December", "event": "Christmas"},
        ),
        (
            [
                ("org", "Church"),
                ("per", "Christ"),
                ("event", "Lord's Supper"),
                ("per", "James"),
                ("work_of_art", "Bible"),
            ],
            {
                "org": "Church",
                "per": "Christ James",
                "event": "Lord's Supper",
                "work_of_art": "Bible",
            },
        ),
        (
            [("per", "Anne"), ("per", "Marie"), ("per", "Louise")],
            {"per": "Anne Marie Louise"},
        ),
    ],
)
def test_merge_entities(entities, expected_dict):
    assert merge_entities(entities) == expected_dict


@pytest.mark.parametrize(
    ("label_dir", "prediction_dir", "by_category", "expected_table"),
    [
        (
            FIXTURES / "labels",
            FIXTURES / "predictions",
            True,
            """| Category    | ECER (%) | EWER (%) | Support |
|:------------|:--------:|:--------:|--------:|
| date        |   0.00   |   0.00   |       1 |
| event       |  100.00  |  100.00  |       1 |
| ordinal     |  100.00  |  100.00  |       1 |
| org         |  45.45   |  50.00   |       1 |
| per         |  32.14   |  33.33   |       2 |
| work_of_art |  100.00  |  100.00  |       1 |
| total       |   3.53   |  11.79   |       3 |""",
        ),
        (
            FIXTURES / "labels",
            FIXTURES / "predictions",
            False,
            """| Category | ECER (%) | EWER (%) | Support |
|:---------|:--------:|:--------:|--------:|
| total    |   3.53   |  11.79   |       3 |""",
        ),
    ],
)
def test_compute_cer_wer(label_dir, prediction_dir, by_category, expected_table):
    table = cerwer(label_dir, prediction_dir, by_category)
    assert table.get_string() == expected_table
