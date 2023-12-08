from pytz import utc, timezone

def datetimefilter(value, format='%B %d, %Y %I:%M %p'):
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = utc.localize(value)
    eastern = timezone('US/Eastern')
    value = value.astimezone(eastern)
    return value.strftime(format)

def utility_functions():
    def get_full_day_names(recurring_days):
        day_names = {'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'}
        return ', '.join(day_names[day] for day in recurring_days.split(',') if day)  # Add check for empty strings here

    def get_full_accessibility_names(accessibility_keys):
        accessibility_names = {
            'wheelchair': 'Wheelchair',
            'visual': 'Visual impairment',
            'hearing': 'Hearing impairment',
            'service_dog': 'Service dog friendly',
            'quiet': 'Quiet ride',
            'step_free': 'Step-free access',
        }
        return ', '.join(accessibility_names[key] for key in accessibility_keys.split(',') if key)  # Add check for empty strings here

    return dict(get_full_day_names=get_full_day_names, get_full_accessibility_names=get_full_accessibility_names)