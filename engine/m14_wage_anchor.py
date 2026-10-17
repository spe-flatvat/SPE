from math import isfinite


def validate_anchors(anchors):
    if not isinstance(anchors, dict) or len(anchors) < 2:
        raise ValueError("At least two anchors required")

    for year, wage in anchors.items():
        if type(year) is not int:
            raise ValueError("Anchor year must be integer")
        if type(wage) not in (int, float):
            raise ValueError("Anchor wage must be numeric")
        if not isfinite(wage) or wage <= 0:
            raise ValueError("Anchor wage must be positive and finite")

    return sorted(anchors)


def wage_growth_rate(anchors, year):
    years = validate_anchors(anchors)

    if type(year) is not int:
        raise ValueError("Year must be integer")

    if not years[0] < year <= years[-1]:
        raise ValueError("Year outside growth interval")

    for start, end in zip(years, years[1:]):
        if start < year <= end:
            return (
                (anchors[end] / anchors[start])
                ** (1 / (end - start))
                - 1
            )

    raise ValueError("No matching anchor interval")


def interpolate_wage(anchors, year):
    years = validate_anchors(anchors)

    if type(year) is not int:
        raise ValueError("Year must be integer")

    if not years[0] <= year <= years[-1]:
        raise ValueError("Year outside anchor range")

    if year in anchors:
        return float(anchors[year])

    for start, end in zip(years, years[1:]):
        if start < year < end:
            growth = wage_growth_rate(anchors, year)
            return anchors[start] * (1 + growth) ** (year - start)

    raise ValueError("No matching anchor interval")
