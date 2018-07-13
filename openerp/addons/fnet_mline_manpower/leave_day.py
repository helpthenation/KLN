from datetime import date, timedelta as td
import datetime

def leave_count(date_from, date_to):
    count = 0.00
    year_f, month_f, day_f = (int(x) for x in date_from.split('-'))
    year_t, month_t, day_t = (int(x) for x in date_to.split('-'))
    d1 = date(year_f, month_f, day_f)
    d2 = date(year_t, month_t, day_t)
    delta = d2 - d1
    for i in range(delta.days + 1):
        dd =  d1 + td(days=i)
        year, month, day = (int(x) for x in str(dd).split('-'))
        ans = datetime.date(year, month, day)
        if ans.strftime("%A") == 'Friday':
            count += 1
    return count
