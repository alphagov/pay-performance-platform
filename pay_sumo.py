import time
import sumologic

from datetime import datetime
from datetime import timedelta

LIMIT = 42
TIME_ZONE = 'UTC'
DELAY = 5
SUCCESS_STATUS = 'DONE GATHERING RESULTS'
CANCELLED_STATUS = 'CANCELLED'
URL = 'https://api.eu.sumologic.com/api/v1/'
QUERY_FILE = 'query.sumoql'
QUERY = '''
(_sourceCategory=prod service=docker container=connector)
| parse "provider_type=*," as provider_type
| where provider_type="live"
| parse "operation_type=*," as operation_type
| where operation_type="Capture"
| parse "charge_external_id=*," as charge_external_id
| parse "amount=*," as amount
| amount/100 as amount
| sum(amount) as sumAmount, count_distinct(charge_external_id) as paymentVolume, avg(amount) as avgAmount
| format("%.0f", sumAmount) as totalAmountPaid
| format("%d", paymentVolume) as payments
| format("%.0f", avgAmount) as averageAmountPaid
| fields totalAmountPaid, payments, averageamountpaid
'''


class PaySumoResult:
    def __init__(self, search_job_record):
        self.search_job_record = search_job_record

    def total_amount_paid(self):
        return self.search_job_record['records'][0]['map']['totalamountpaid']

    def payment_volume(self):
        return self.search_job_record['records'][0]['map']['payments']

    def average_amount_paid(self):
        return self.search_job_record['records'][0]['map']['averageamountpaid']


def unix_time_millis(dt):
    epoch = datetime(1970, 1, 1).date()
    return int((dt - epoch).total_seconds() * 1000)


def query_transaction_value_and_volume(sumo_access_id, sumo_access_key, presented_date_time):
    sumo = sumologic.SumoLogic(sumo_access_id, sumo_access_key, URL)

    date = presented_date_time.date()
    from_time = unix_time_millis(date)
    to_time = unix_time_millis(date + timedelta(days=1))

    search_job = sumo.search_job(QUERY, from_time, to_time, TIME_ZONE)

    status = sumo.search_job_status(search_job)
    while status['state'] != SUCCESS_STATUS:
        if status['state'] == CANCELLED_STATUS:
            break
        time.sleep(DELAY)
        status = sumo.search_job_status(search_job)

    print status['state']

    if status['state'] == SUCCESS_STATUS:
        count = status['recordCount']
        limit = count if count < LIMIT and count != 0 else LIMIT # compensate bad limit check
        records = sumo.search_job_records(search_job, limit=limit)
        print records
        return PaySumoResult(records)
