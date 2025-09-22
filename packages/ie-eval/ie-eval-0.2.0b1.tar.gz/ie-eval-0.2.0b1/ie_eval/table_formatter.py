"""PrettyTable formatters."""

import json

from prettytable import MARKDOWN, PrettyTable

from ie_eval import GLOBAL_STAT_NAME
from ie_eval.scorer import MicroAverageErrorRate, MicroAverageFScore


def make_summary_table(
    bow_table: PrettyTable,
    botw_table: PrettyTable,
    boe_table: PrettyTable,
    oi_ecer_ewer_table: PrettyTable,
    ecer_ewer_table: PrettyTable,
    nerval_oi_table: PrettyTable,
    nerval_table: PrettyTable,
) -> PrettyTable:
    """Format and display a summary table from all available metrics.

    Args:
        bow_table (PrettyTable): Bag-of-word table.
        botw_table (PrettyTable): Bag-of-tagged-word table.
        boe_table (PrettyTable): Bag-of-entity table.
        oi_ecer_ewer_table (PrettyTable): ECER/EWER OI table.
        ecer_ewer_table (PrettyTable): ECER/EWER table.
        nerval_oi_table (PrettyTable): Nerval OI table.
        nerval_table (PrettyTable): Nerval table.

    Returns:
        The summary evaluation table formatted in Markdown.
    """
    summary_table = PrettyTable()
    summary_table.set_style(MARKDOWN)
    summary_table.field_names = [
        "Category",
        "BoW-F1 (%)",
        "BoTW-F1 (%)",
        "BoE-F1 (%)",
        "ECER (%)",
        "EWER (%)",
        "ECER OI (%)",
        "EWER OI (%)",
        "Nerval-F1 (OI) (%)",
        "Nerval-F1 (%)",
        "N documents",
    ]
    summary_table.align["Category"] = "l"
    summary_table.align["N documents"] = "r"
    for i in range(1, len(json.loads(bow_table.get_json_string()))):
        summary_table.add_row(
            [
                json.loads(bow_table.get_json_string())[i]["Category"],
                json.loads(bow_table.get_json_string())[i]["F1 (%)"],
                json.loads(botw_table.get_json_string())[i]["F1 (%)"],
                json.loads(boe_table.get_json_string())[i]["F1 (%)"],
                json.loads(oi_ecer_ewer_table.get_json_string())[i]["ECER (%)"],
                json.loads(oi_ecer_ewer_table.get_json_string())[i]["EWER (%)"],
                json.loads(ecer_ewer_table.get_json_string())[i]["ECER (%)"],
                json.loads(ecer_ewer_table.get_json_string())[i]["EWER (%)"],
                json.loads(nerval_oi_table.get_json_string())[i]["F1 (%)"],
                json.loads(nerval_table.get_json_string())[i]["F1 (%)"],
                json.loads(bow_table.get_json_string())[i]["N documents"],
            ],
        )
    return summary_table


def make_bag_of_entities_prettytable(
    errors: MicroAverageErrorRate,
    detections: MicroAverageFScore,
) -> PrettyTable:
    """Format and display Bag-of-Word results using PrettyTable.

    Args:
        errors (MicroAverageErrorRate): Total error rates (bWER).
        detections (MicroAverageFScore): Total recognition rates (Precision, Recall, F1).

    Returns:
        The evaluation table formatted in Markdown.
    """
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = [
        "Category",
        "bWER (%)",
        "Precision (%)",
        "Recall (%)",
        "F1 (%)",
        "N words",
        "N documents",
    ]
    table.align["Category"] = "l"
    table.align["N words"] = "r"
    table.align["N documents"] = "r"
    for tag in errors.categories:
        table.add_row(
            [
                tag,
                f"{errors.error_rate[tag]:.2f}",
                f"{detections.precision[tag]:.2f}",
                f"{detections.recall[tag]:.2f}",
                f"{detections.f1[tag]:.2f}",
                errors.label_word_count[tag],
                errors.count[tag],
            ],
        )
    return table


def make_oi_ecer_ewer_prettytable(
    ecer_total_score_err: MicroAverageErrorRate,
    ewer_total_score_err: MicroAverageErrorRate,
) -> PrettyTable:
    """Format and display order independent ECER/EWER results using PrettyTable."""
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = [
        "Category",
        "ECER (%)",
        "EWER (%)",
        "N entities",
        "N documents",
    ]
    table.align["Category"] = "l"
    table.align["N entities"] = "r"
    table.align["N documents"] = "r"
    for tag in ecer_total_score_err.categories:
        table.add_row(
            [
                tag,
                f"{ecer_total_score_err.error_rate[tag]:.2f}",
                f"{ewer_total_score_err.error_rate[tag]:.2f}",
                ecer_total_score_err.label_word_count[tag],
                ecer_total_score_err.count[tag],
            ],
        )
    return table


def make_oi_nerval_prettytable(
    detections: MicroAverageFScore,
) -> PrettyTable:
    """Format and display order independent Nerval results using PrettyTable."""
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = [
        "Category",
        "Precision (%)",
        "Recall (%)",
        "F1 (%)",
        "N entities",
        "N documents",
    ]
    table.align["Category"] = "l"
    table.align["N entities"] = "r"
    table.align["N documents"] = "r"
    for tag in detections.categories:
        table.add_row(
            [
                tag,
                f"{detections.precision[tag]:.2f}",
                f"{detections.recall[tag]:.2f}",
                f"{detections.f1[tag]:.2f}",
                detections.label_word_count[tag],
                detections.count[tag],
            ],
        )
    return table


def make_nerval_pretty_table(rows: list[list]) -> PrettyTable:
    """Format into a pretty table.

    Args:
        rows (list[list]): Rows of the table

    Returns:
        PrettyTable: Formatted table.
    """
    table = PrettyTable()
    table.field_names = ["Category", "Precision (%)", "Recall (%)", "F1 (%)", "Support"]
    table.set_style(MARKDOWN)
    # First column should be left aligned still
    table.align["Category"] = "l"

    def _special_sort(row: list[str]) -> str:
        if row[0] == GLOBAL_STAT_NAME:
            # Place the line for all entities at the very top
            return ""
        return row[0]

    rows.sort(key=_special_sort)
    # Place ALL_ENTITIES row at the end
    rows.append(rows.pop(0))

    table.add_rows(rows)
    return table
