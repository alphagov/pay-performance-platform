import pay_performance_platform as ppp
import argparse
from datetime import datetime, date, timedelta

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

parser = argparse.ArgumentParser(description='Backfill data in pay-performance-platform')
parser.add_argument('--context', required=True, help="Either 'test' to send data to test endpoint, or 'payments' to send to real endpoint")
parser.add_argument('--start', required=True, help='Inclusive start date in format Y-m-d')
parser.add_argument('--end', required=True, help='Inclusive end date in format Y-m-d')

args = parser.parse_args()

if args.context not in ['test', 'payments']:
	raise Exception('context must be either "test" or "payments"')

print 'Backfilling with context ' + args.context + ' for dates ' + args.start + ' to ' + args.end

start = datetime.strptime(args.start + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
end = datetime.strptime(args.end + ' 23:59:59', "%Y-%m-%d %H:%M:%S")

for date in daterange(start, end):
	print 'Backfilling ' + date.isoformat()
	ppp.lambda_handler({'time': date.isoformat()}, args.context)
