from datetime import datetime, timezone, timedelta
import pytz

tz = pytz.timezone('Asia/Ho_Chi_Minh')


def str_to_dt(istr):
	dt = datetime.strptime(istr, '%y-%m-%d')
	return dt


def str_to_ts(istr):
	dt = datetime.strptime(istr, '%Y-%m-%d')
	timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
	return timestamp


def dt_to_ts(dt):
	return dt.replace(tzinfo=tz).timestamp()


def current_quarter_and_year():
	n = datetime.now()
	quarter = (n.month-1) // 3 + 1

	return quarter, n.year


def current_day():
	n = datetime.now()
	return datetime(year=n.year, month=n.month, day=n.day)


def latest_working_day():
	cr_d = current_day()

	while cr_d.weekday() >= 5:
		cr_d = cr_d - timedelta(days=1)
	return cr_d

def prev_quarter(year, quarter):
	if quarter == 1:
		return year-1, 4
	return year, quarter-1


def convert_quarter_to_end_date(year, quarter):
	day = 1
	if quarter == 1:
		month = 4
	elif quarter == 2:
		month = 7
	elif quarter == 3:
		month = 10
	elif quarter == 4:
		month = 1
		year += 1
	return datetime(year=year, month=month, day=day)