from datetime import date

def calculate_daily_progress(day_number: int) -> float:
    """
    Calculate the incremental daily progress percentage for the challenge.
    Day 1: 1%, Day 2: 2%, ..., Day 100: 100%
    """
    if 1 <= day_number <= 100:
        return float(day_number)
    return 0.0

def is_goal_date_today(goal_date) -> bool:
    """
    Check if the given goal date is today.
    """
    return goal_date == date.today()

def validate_sleep_hours(hours: float) -> bool:
    """
    Validate sleep hours input within reasonable limits (e.g., 0-24).
    """
    return 0 <= hours <= 24
