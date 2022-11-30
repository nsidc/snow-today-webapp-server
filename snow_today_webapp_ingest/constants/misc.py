from datetime import date


def _water_year_day_1() -> date:
    """Calculate day 1 of the current water year.

    Day 1 of the current water year _may not_ lie within the current calendar year.

    Water year is 1-indexed. Day 1 is October 1st.
    """
    today = date.today()
    this_year_wyd1 = date(today.year, 10, 1)

    # The "water year" is not necessarily synced up with the calendar year:
    if today >= this_year_wyd1:
        return this_year_wyd1

    return date(
        today.year - 1,
        this_year_wyd1.month,
        this_year_wyd1.day,
    )


WATER_YEAR_DAY1 = _water_year_day_1()

# NOTE: Incremented to achieve 1-indexed result to align with MATLAB convention
CURRENT_DOWY = (date.today() - WATER_YEAR_DAY1).days + 1
