"""Compute CER and WER from a label/prediction dataset."""

import logging
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

import editdistance
from bio_parser import GLOBAL_STAT_NAME
from bio_parser.utils import load_dataset
from prettytable import MARKDOWN, PrettyTable

from ie_eval.metrics.utils import sort_categories
from ie_eval.scorer import (
    MicroAverageErrorRate,
    OiEcerEwer,
)
from ie_eval.table_formatter import (
    make_oi_ecer_ewer_prettytable,
)

logger = logging.getLogger(__name__)


def oiecerewer(
    label_dir: Path,
    prediction_dir: Path,
    by_category: bool = False,
    **kwargs,  # noqa: ARG001
) -> PrettyTable:
    """Compute reading-order-independent ECER and EWER metrics.

    Args:
        label_dir (Path): Path to the directory containing BIO label files.
        prediction_dir (Path): Path to the directory containing BIO prediction files.
        by_category (bool, optional): Whether to compute the metric globally or for each category. Defaults to False. (Not implemented yet)
        print_table (bool, optional): Whether to print the table. Defaults to True.

    Returns:
        PrettyTable: The evaluation table formatted in Markdown.
    """
    dataset = load_dataset(label_dir, prediction_dir)
    # Initialize scores
    ecer_total_score_err = MicroAverageErrorRate()
    ewer_total_score_err = MicroAverageErrorRate()

    # Iterate over the dataset
    for label, prediction in dataset:
        ecer_score = OiEcerEwer(
            labels=label.entities,
            predictions=prediction.entities,
            compute_ecer=True,
        )

        ewer_score = OiEcerEwer(
            labels=label.entities,
            predictions=prediction.entities,
            compute_ecer=False,
        )
        # Micro average
        ecer_total_score_err.update(GLOBAL_STAT_NAME, ecer_score)
        ewer_total_score_err.update(GLOBAL_STAT_NAME, ewer_score)

        # TODO: https://gitlab.teklia.com/ner/metrics/ie-eval/-/issues/12
        if by_category:
            continue

    # Format and display results
    table = make_oi_ecer_ewer_prettytable(
        ecer_total_score_err,
        ewer_total_score_err,
    )
    return table


class TextEval(NamedTuple):
    """Compute text errors between a label and prediction."""

    label: str
    """Label text."""
    prediction: str
    """Predicted text."""

    @property
    def char_errors(self) -> int:
        """Compute character errors between the label and prediction.

        Returns:
            Character errors.

        Examples:
            >>> TextEval("I really like cats", "I love cats").char_errors
            9
        """
        return editdistance.eval(
            format_string_for_cer(self.label),
            format_string_for_cer(self.prediction),
        )

    @property
    def word_errors(self) -> int:
        """Compute word errors between the label and prediction.

        Returns:
            Word errors.

        Examples:
            >>> TextEval("I really like cats", "I love cats").word_errors
            2
        """
        return editdistance.eval(
            format_string_for_wer(self.label),
            format_string_for_wer(self.prediction),
        )

    @property
    def char_totals(self) -> int:
        """Compute the max number of characters in the label or prediction.

        Returns:
            Number of characters.

        Examples:
            >>> TextEval("I really like cats", "I love cats").char_totals
            18
        """
        return max(
            len(format_string_for_cer(self.label)),
            len(format_string_for_cer(self.prediction)),
        )

    @property
    def word_totals(self) -> int:
        """Compute the max number of words in the label or prediction.

        Returns:
            Number of words.

        Examples:
            >>> TextEval("I really like cats", "I love cats").word_totals
            4
        """
        return max(
            len(format_string_for_wer(self.label)),
            len(format_string_for_wer(self.prediction)),
        )


class TotalScore:
    """Compute total evaluation scores."""

    def __init__(self):
        """Initialize errors and counts.

        Examples:
            >>> score = TotalScore()
        """
        self.char_errors = defaultdict(int)
        self.word_errors = defaultdict(int)
        self.char_totals = defaultdict(int)
        self.word_totals = defaultdict(int)
        self.count = defaultdict(int)

    def update(self, key, score: TextEval):
        """Update the score with the current evaluation for a given key.

        Args:
            key (str): Category to update.
            score (TextEval): Current score.

        Examples:
            >>> score.update("total", TextEval("I really like cats", "I like cats"))
            >>> score.update("animal", TextEval("cats", "cats"))
            >>> score.char_errors
            defaultdict(<class 'int'>, {'total': 7, 'animal': 0})
            >>> score.word_errors
            defaultdict(<class 'int'>, {'total': 1, 'animal': 0})
            >>> score.char_totals
            defaultdict(<class 'int'>, {'total': 18, 'animal': 4})
            >>> score.word_totals
            defaultdict(<class 'int'>, {'total': 4, 'animal': 1})
            >>> score.count
            defaultdict(<class 'int'>, {'total': 1, 'animal': 1})
        """
        self.char_errors[key] += score.char_errors
        self.word_errors[key] += score.word_errors
        self.char_totals[key] += score.char_totals
        self.word_totals[key] += score.word_totals
        self.count[key] += 1

    @property
    def categories(self) -> list[str]:
        """List of semantic categories for which scores are computed.

        Returns:
            The list of categories.

        Examples:
            >>> score.categories
            ['total', 'animal']
        """
        return list(self.count.keys())

    @property
    def cer(self) -> dict[str, float]:
        """Compute the Character Error Rate (%).

        Returns:
            The Character Error Rate.

        Examples:
            >>> score.cer
            {'total': 38.9, 'animal': 0.0}
        """
        return {
            key: round(100 * self.char_errors[key] / self.char_totals[key], 2)
            for key in self.categories
        }

    @property
    def wer(self) -> dict[str, float]:
        """Compute the Word Error Rate (%).

        Returns:
            The Word Error Rate.

        Examples:
            >>> score.wer
            {'total': 25.0, 'animal': 0.0}
        """
        return {
            key: round(100 * self.word_errors[key] / self.word_totals[key], 2)
            for key in self.categories
        }


def format_string_for_wer(text: str) -> list[str]:
    """Format string for WER computation.

    Args:
        text (str): The text to format.

    Returns:
        A list of words formatted for WER computation.

    Examples:
        >>> format_string_for_wer(text="this is a string to evaluate")
        ['this', 'is', 'a', 'string', 'to', 'evaluate']
        >>> format_string_for_wer(text="this is    another string to   evaluate")
        ['this', 'is', 'another', 'string', 'to', 'evaluate']
    """
    return text.strip().split()


def format_string_for_cer(text: str) -> str:
    """Format string for CER computation.

    Args:
        text (str): The text to format.

    Returns:
        The formatted text for CER computation.

    Examples:
        >>> format_string_for_cer(text="this is a string to evaluate")
        'this is a string to evaluate'
        >>> format_string_for_cer(text="this is    another string to   evaluate")
        'this is another string to evaluate'
    """
    return " ".join(text.strip().split())


def make_prettytable(score: TotalScore) -> PrettyTable:
    """Format and display results using PrettyTable.

    Args:
        score (TotalScore): Total scores.

    Returns:
        The evaluation table formatted in Markdown.
    """
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = ["Category", "ECER (%)", "EWER (%)", "Support"]
    table.align["Category"] = "l"
    table.align["Support"] = "r"

    rows = []
    for tag in score.categories:
        rows.append(
            [
                tag,
                f"{score.cer[tag]:.2f}",
                f"{score.wer[tag]:.2f}",
                score.count[tag],
            ],
        )

    table.add_rows(sort_categories(rows))
    return table


def merge_entities(entities: list[tuple[str, str]]) -> dict[str, str]:
    """Iterate over entities and merge text for each entity type.

    Args:
        entities (list[tuple[str, str]]): A list of entities.

    Returns:
        A dictionary with entity types as keys and the corresponding text as values.
    """
    entity_text = defaultdict(list)
    for tag, text in entities:
        entity_text[tag].append(text)
    return {k: " ".join(v) for k, v in entity_text.items()}


def cerwer(
    label_dir: Path,
    prediction_dir: Path,
    by_category: bool = False,
) -> PrettyTable:
    """Read BIO files and compute Character and Word Error Rates globally or for each NER category.

    Args:
        label_dir (Path): Path to the reference BIO file.
        prediction_dir (Path): Path to the prediction BIO file.
        by_category (bool): Whether to display CER/WER by category.

    Returns:
        A Markdown formatted table containing evaluation results.
    """
    # Initialize scores
    score = TotalScore()
    # Load the dataset
    dataset = load_dataset(label_dir, prediction_dir)
    # Iterate over the dataset
    for label, prediction in dataset:
        # Compute global CER and WER
        score.update(GLOBAL_STAT_NAME, TextEval(label.text, prediction.text))

        # Compute CER and WER by category
        if not by_category:
            continue
        label_text = merge_entities(label.entities)
        pred_text = merge_entities(prediction.entities)
        for tag in label_text:
            score.update(
                tag,
                TextEval(
                    label_text[tag],
                    pred_text.get(tag, ""),
                ),
            )

    # Format and display results
    return make_prettytable(score)
