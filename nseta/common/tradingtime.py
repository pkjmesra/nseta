import pytz
from datetime import datetime, time

IST_TIMEZONE = 'Asia/Kolkata'

__all__ = ['IST_time', 'IST_date', 'IST_datetime', 'current_datetime_in_ist_trading_time_range', 'datetime_in_ist_trading_time_range', 'is_datetime_between', 'is_trading_day', 'trade_begin_datetime_ist', 'trade_end_datetime_ist']

def IST_time():
	tz = pytz.timezone(IST_TIMEZONE)
	delhi_now = datetime.now(tz)
	return datetime.strptime(delhi_now.strftime("%H:%M:%S"), "%H:%M:%S").time()

def IST_date():
	tz = pytz.timezone(IST_TIMEZONE)
	delhi_now = datetime.now(tz)
	return datetime.strptime(delhi_now.strftime("%d-%m-%Y"), "%d-%m-%Y").date()

def IST_datetime():
	tz = pytz.timezone(IST_TIMEZONE)
	delhi_now = datetime.now(tz)
	return delhi_now

def is_trading_day():
	delhi_now = IST_datetime()
	return delhi_now.weekday() <= 4

def current_datetime_in_ist_trading_time_range():
	system_time = IST_datetime()
	trading_begin_time = trade_begin_datetime_ist()
	trading_end_time = trade_end_datetime_ist()
	return is_datetime_between(trading_begin_time, trading_end_time, system_time) and is_trading_day()

def datetime_in_ist_trading_time_range(check_datetime):
	trading_begin_time = trade_begin_datetime_ist()
	trading_end_time = trade_end_datetime_ist()
	return is_datetime_between(trading_begin_time, trading_end_time, check_datetime) and is_trading_day()

def is_datetime_between(begin_datetime, end_datetime, check_datetime=None):
	# If check datetime is not given, default to current IST datetime
	check_datetime = check_datetime or IST_datetime()
	if begin_datetime < end_datetime:
		return check_datetime >= begin_datetime and check_datetime <= end_datetime
	else: # crosses midnight
		return check_datetime >= begin_datetime or check_datetime <= end_datetime
	
def trade_begin_datetime_ist():
	delhi_now = IST_datetime()
	tz = pytz.timezone(IST_TIMEZONE)
	begin_dt = datetime(delhi_now.year, delhi_now.month, delhi_now.day, 9, 15, tzinfo = tz)
	return begin_dt

def trade_end_datetime_ist():
	delhi_now = IST_datetime()
	tz = pytz.timezone(IST_TIMEZONE)
	end_dt = datetime(delhi_now.year, delhi_now.month, delhi_now.day, 15, 30, tzinfo = tz)
	return end_dt
