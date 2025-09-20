import pendulum

def greet():
    now = pendulum.now()
    return f"Hello! The current time is {now.to_day_datetime_string()}"

def days_ahead(days: int):
    now = pendulum.now()
    future = now.add(days=days)
    return f"In {days} days it will be {future.to_day_datetime_string()}"

