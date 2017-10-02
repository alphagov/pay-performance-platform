import pay_performance_platform as ppp
import argparse
from datetime import datetime, date, timedelta

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

parser = argparse.ArgumentParser(description='Backfill data in pay-performance-platform')
parser.add_argument('--context', required=True)
parser.add_argument('--start', required=True)
parser.add_argument('--end', required=True)

args = parser.parse_args()
print 'Backfilling with context ' + args.context + ' for dates ' + args.start + ' to ' + args.end

start = datetime.strptime(args.start + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
end = datetime.strptime(args.end + ' 23:59:59', "%Y-%m-%d %H:%M:%S")

for date in daterange(start, end):
	print 'Backfilling ' + date.isoformat()
	ppp.lambda_handler({'time': date.isoformat()}, args.context)

