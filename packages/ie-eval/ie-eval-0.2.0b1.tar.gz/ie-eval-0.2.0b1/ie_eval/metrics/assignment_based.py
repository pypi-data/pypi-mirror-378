"""Compute the ECER/EWER/Nerval metrics from a label/prediction dataset."""

import logging

from prettytable import PrettyTable

from ie_eval.metrics.cer import cerwer, oiecerewer
from ie_eval.metrics.nerval import nerval, oinerval

logger = logging.getLogger(__name__)


def compute_ecerewer(
    order_independent: bool = False,
    print_table: bool = True,
    *args,
    **kwargs,
) -> PrettyTable:
    """Compute reading-order-independent ECER and EWER metrics.

    Args:
        print_table (bool, optional): Whether to print the table. Defaults to True.
        order_independent (bool): Whether the metric should be order-independent.

    Returns:
        PrettyTable: The evaluation table formatted in Markdown.
    """
    table = (
        oiecerewer(*args, **kwargs) if order_independent else cerwer(*args, **kwargs)
    )

    if print_table:
        print(table)  # noqa: T201
    return table


def compute_nerval(
    order_independent: bool = False,
    print_table: bool = True,
    *args,
    **kwargs,
) -> PrettyTable:
    """Read BIO files and compute Precision, Recall and F1 globally or for each NER category.

    Args:
        print_table (bool, optional): Whether to print the table. Defaults to True.
        order_independent (bool): Whether the metric should be order-independent.

    Returns:
        A Markdown formatted table containing evaluation results.
    """
    table = oinerval(*args, **kwargs) if order_independent else nerval(*args, **kwargs)

    if print_table:
        print(table)  # noqa: T201
    return table
