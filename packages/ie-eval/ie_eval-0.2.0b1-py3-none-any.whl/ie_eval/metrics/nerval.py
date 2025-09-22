"""Compute Precision, Recall and F1 from a label/prediction dataset."""

from collections import Counter, defaultdict
from operator import itemgetter
from pathlib import Path

from bio_parser import GLOBAL_STAT_NAME
from bio_parser.parse.document import Document
from bio_parser.utils import load_dataset
from nerval.evaluate import evaluate
from prettytable import PrettyTable

from ie_eval.metrics.utils import sort_categories
from ie_eval.scorer import MicroAverageFScore, OiNerval
from ie_eval.table_formatter import make_nerval_pretty_table, make_oi_nerval_prettytable

METRICS = ["predicted", "matched", "Support"]
NERVAL_GLOBAL_STAT = "ALL"


def _format_document(document: Document) -> dict:
    return {
        # Support cases where the string is empty (edlib will crash.)
        "words": document.text or "∅",
        "labels": document.char_labels or ["O"],
        "entity_count": {
            NERVAL_GLOBAL_STAT: len(document.entities),
            **Counter(map(itemgetter(0), document.entities)),
        },
    }


def compute_precision(matched: int, predicted: int) -> float:
    """Compute precision."""
    if predicted == 0:
        return 100 if matched == 0 else 0
    return 100 * matched / predicted


def compute_recall(matched: int, support: int) -> float:
    """Compute recall."""
    if support == 0:
        return 100 if matched == 0 else 0
    return 100 * matched / support


def compute_f1(precision: float, recall: float) -> float:
    """Compute F1 score."""
    if precision + recall == 0:
        return 0
    return 2 * precision * recall / (precision + recall)


def nerval(
    label_dir: Path,
    prediction_dir: Path,
    nerval_threshold: float,
    by_category: bool = False,
) -> PrettyTable:
    """Read BIO files and compute Precision, Recall and F1 globally or for each NER category.

    Args:
        label_dir (Path): Path to the reference BIO file.
        prediction_dir (Path): Path to the prediction BIO file.
        nerval_threshold (float): Character Error Rate threshold used to match entities.
        by_category (bool): Whether to display Precision/Recall/F1 by category.

    Returns:
        A Markdown formatted table containing evaluation results.
    """
    # Load the dataset
    dataset = load_dataset(label_dir, prediction_dir)

    # Iterate over the dataset
    scores = defaultdict(lambda: defaultdict(int))
    for label, prediction in dataset:
        # if label.bio_repr == "":
        #     continue
        cor_score = evaluate(
            _format_document(label),
            _format_document(prediction),
            nerval_threshold,
        )
        for entity, results in cor_score.items():
            # Nerval uses a different global statistic than us
            if entity == NERVAL_GLOBAL_STAT:
                entity = GLOBAL_STAT_NAME

            for metric in METRICS:
                scores[entity][metric] += results[metric] or 0

    results = []
    for entity, score in scores.items():
        if entity != GLOBAL_STAT_NAME and not by_category:
            continue
        precision = compute_precision(score["matched"], score["predicted"])
        recall = compute_recall(score["matched"], score["Support"])
        results.append(
            [
                entity,
                round(precision, 2),
                round(recall, 2),
                round(compute_f1(precision, recall), 2),
                score["Support"],
            ],
        )

    return make_nerval_pretty_table(
        rows=sort_categories(results),
    )


def oinerval(
    label_dir: Path,
    prediction_dir: Path,
    nerval_threshold: float = 30.0,
    by_category: bool = False,
) -> PrettyTable:
    """Compute reading-order-independent Nerval Precision, Recall and F1 scores.

    Args:
        label_dir (Path): Path to the directory containing BIO label files.
        prediction_dir (Path): Path to the directory containing BIO prediction files.
        nerval_threshold (float, default = 30.0): Threshold for the amount of character error that is tolerable during the computation (values in the range [0.0, 100.0]])
        by_category (bool, optional): Whether to compute the metric globally or for each category. Defaults to False. (Not implemented yet)
        print_table (bool, optional): Whether to print the table. Defaults to True.

    Returns:
        PrettyTable: The evaluation table formatted in Markdown.
    """
    dataset = load_dataset(label_dir, prediction_dir)
    # Initialize scores
    total_score_f1 = MicroAverageFScore()

    # Iterate over the dataset
    for label, prediction in dataset:
        score = OiNerval(
            labels=label.entities,
            predictions=prediction.entities,
            nerval_threshold=nerval_threshold,
        )

        # Micro average
        total_score_f1.update(GLOBAL_STAT_NAME, score)

        # TODO: https://gitlab.teklia.com/ner/metrics/ie-eval/-/issues/12
        if not by_category:
            continue

    # Format and display results
    table = make_oi_nerval_prettytable(
        total_score_f1,
    )
    return table
