"""Utils."""

from ie_eval import GLOBAL_STAT_NAME


def sort_categories(categories: list[list[str]]) -> list[list[str]]:
    """Sort a list of categories with their associated metrics.

    All categories are alphabetically sorted except for GLOBAL_STAT_NAME
    which is appended at the very end of the sorted list.

    Args:
        categories (list[list[str]]): List of categories with their metrics.

    Returns:
        list[list[str]]: A sorted version of the provided list of categories.
    """
    sorted_categories = sorted(categories)
    return sorted(
        sorted_categories,
        key=lambda e: (
            sorted_categories.index(e)
            if e[0] != GLOBAL_STAT_NAME
            else len(sorted_categories)
        ),
    )
