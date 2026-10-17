"""Gini coefficient anchor validation and linear interpolation.

M17 model assumption:
    Gini coefficients between supplied anchors are interpolated
    linearly. This interpolation rule is an M17 modeling choice,
    not an explicitly prescribed v6 interpolation formula.

Scope:
    The resulting annual Gini coefficients are output indicators.
    They do not feed back into GDP, tax, population, or wage
    transition calculations.

Anchor values must be supplied by the scenario.
    This module does not prescribe policy-specific Gini targets.
"""

from math import isfinite


def validate_gini_anchors(anchors):
    if not isinstance(anchors, dict) or len(anchors) < 2:
        raise ValueError("At least two Gini anchors required")

    for year, gini in anchors.items():
        if type(year) is not int:
            raise ValueError("Gini anchor year must be integer")

        if type(gini) not in (int, float):
            raise ValueError("Gini anchor must be numeric")

        if not isfinite(gini) or not 0 <= gini <= 1:
            raise ValueError("Gini anchor must be within [0, 1]")

    return sorted(anchors)


def interpolate_gini(anchors, year):
    years = validate_gini_anchors(anchors)

    if type(year) is not int:
        raise ValueError("Year must be integer")

    if not years[0] <= year <= years[-1]:
        raise ValueError("Year outside Gini anchor range")

    if year in anchors:
        return float(anchors[year])

    for start, end in zip(years, years[1:]):
        if start < year < end:
            fraction = (year - start) / (end - start)

            return (
                anchors[start]
                + (anchors[end] - anchors[start]) * fraction
            )

    raise ValueError("No matching Gini anchor interval")
