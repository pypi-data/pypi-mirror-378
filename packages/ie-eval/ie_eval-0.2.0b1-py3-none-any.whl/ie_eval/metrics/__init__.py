from pathlib import Path

from bio_parser.utils import load_dataset
from prettytable import PrettyTable

from ie_eval.metrics.assignment_based import (
    compute_ecerewer,
    compute_nerval,
)
from ie_eval.metrics.bag_of_entities import WordType, compute_bag_of_anything
from ie_eval.table_formatter import make_summary_table


def compute_all_metrics(
    label_dir: Path,
    prediction_dir: Path,
    nerval_threshold: float = 30.0,
    by_category: bool = False,
) -> PrettyTable:
    """Compute all metrics.

    Args:
        label_dir (Path): Path to the label directory.
        prediction_dir (Path): Path to the prediction directory.
        by_category (bool, optional): Whether to compute the metric globally or for each category. Defaults to False.

    Returns:
        PrettyTable: Summary table.
    """
    dataset = load_dataset(label_dir=label_dir, prediction_dir=prediction_dir)
    bow_table = compute_bag_of_anything(
        dataset,
        by_category,
        WordType.word,
        print_table=False,
    )
    botw_table = compute_bag_of_anything(
        dataset,
        by_category,
        WordType.tagged_word,
        print_table=False,
    )
    boe_table = compute_bag_of_anything(
        dataset,
        by_category,
        WordType.entity,
        print_table=False,
    )
    kwargs = {
        "label_dir": label_dir,
        "prediction_dir": prediction_dir,
        "by_category": by_category,
        "print_table": False,
    }
    oi_ecer_ewer_table = compute_ecerewer(order_independent=True, **kwargs)
    ecer_ewer_table = compute_ecerewer(order_independent=False, **kwargs)

    nerval_oi_table = compute_nerval(
        nerval_threshold=nerval_threshold,
        order_independent=True,
        **kwargs,
    )
    nerval_table = compute_nerval(
        nerval_threshold=nerval_threshold,
        order_independent=False,
        **kwargs,
    )

    table = make_summary_table(
        bow_table=bow_table,
        botw_table=botw_table,
        boe_table=boe_table,
        oi_ecer_ewer_table=oi_ecer_ewer_table,
        ecer_ewer_table=ecer_ewer_table,
        nerval_oi_table=nerval_oi_table,
        nerval_table=nerval_table,
    )
    print(table)  # noqa: T201
    return table
