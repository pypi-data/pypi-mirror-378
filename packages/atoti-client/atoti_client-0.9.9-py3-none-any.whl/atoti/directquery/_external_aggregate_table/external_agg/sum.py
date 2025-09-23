from __future__ import annotations

from ...._identification import ColumnIdentifier, ExternalColumnIdentifier, Identifiable
from .._external_measure import ExternalMeasure


def sum(  # noqa: A001
    granular_column: Identifiable[ColumnIdentifier],
    /,
    *,
    aggregate_column: Identifiable[ExternalColumnIdentifier],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="SUM",
        granular_columns=[granular_column],
        aggregate_columns=[aggregate_column],
    )
