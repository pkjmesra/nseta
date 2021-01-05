import pytz
from datetime import datetime, time

IST_TIMEZONE = 'Asia/Kolkata'

__all__ = ['IST_time', 'current_time_in_ist_trading_time_range', 'is_time_between']

def IST_time():
	tz = pytz.timezone(IST_TIMEZONE)
	delhi_now = datetime.now(tz)
	return datetime.strptime(delhi_now.strftime("%H:%M:%S"), "%H:%M:%S").time()

def current_time_in_ist_trading_time_range():
	system_time = IST_time()
	trading_begin_time = time(9,15) # 09:15 AM IST
	trading_end_time = time(15,30) # 03:30 PM IST
	return is_time_between(trading_begin_time, trading_end_time, system_time)

def is_time_between(begin_time, end_time, check_time=None):
	# If check time is not given, default to current UTC time
	check_time = check_time or datetime.utcnow().time()
	if begin_time < end_time:
		return check_time >= begin_time and check_time <= end_time
	else: # crosses midnight
		return check_time >= begin_time or check_time <= end_time
