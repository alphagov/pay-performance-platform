import base64
import logging
import os
import boto3
import requests
import pay_sumo

from base64 import b64decode
from datetime import timedelta
from datetime import tzinfo
from iso8601utils import parsers

logging.basicConfig(level=logging.INFO)

URL = 'https://www.performance.service.gov.uk/data/govuk-pay/payments'


class SimpleUtc(tzinfo):
    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def generate_id(timestamp, service, period, dataType):
    # 2016-11-13T00:00:00+00:00.day.govuk-pay.value
    # _timestamp, period, service dataType
    formatted_id = '{0}.{1}.{2}.{3}'.format(
        timestamp, period, service, dataType
        )
    encoded_id = base64.b64encode(unicode(formatted_id, 'utf-8'))
    return encoded_id


def generate_payload(
        timestamp, service, period, transaction_value,
        count, average_transaction_value
):
    return [
            {
                '_id': generate_id(timestamp, service, period, 'transaction'),
                'type': 'transaction',
                'period': period,
                'service': service,
                '_timestamp': timestamp,
                'count': int(count)
            },
            {
                '_id': generate_id(timestamp, service, period, 'value'),
                'type': 'value',
                'period': period,
                'service': service,
                '_timestamp': timestamp,
                'count': int(transaction_value)
            },
            {
                '_id': generate_id(timestamp, service, period, 'average-value'),
                'type': 'average-value',
                'period': period,
                'service': service,
                '_timestamp': timestamp,
                'count': int(average_transaction_value)
            }]


def lambda_handler(event, context):

    dataset_bearer_token = os.getenv('DATASET_BEARER_TOKEN', '')
    sumo_access_id = os.getenv('SUMO_ACCESS_ID', '')
    sumo_access_key = os.getenv('SUMO_ACCESS_KEY', '')
    env_vars_are_encrypted = os.getenv('ENCRYPTED', 'false')

    if env_vars_are_encrypted == 'true':
        dataset_bearer_token = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(dataset_bearer_token))['Plaintext']
        sumo_access_id = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(sumo_access_id))['Plaintext']
        sumo_access_key = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(sumo_access_key))['Plaintext']

    headers = {
                'Authorization': 'Bearer {0}'.format(dataset_bearer_token),
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

    trigger_time_of_cloudwatch_event = event['time']
    current_day_time = parsers.datetime(trigger_time_of_cloudwatch_event)
    sumo = pay_sumo.query_transaction_value_and_volume(
        sumo_access_id, sumo_access_key, current_day_time)

    midnight_iso_date = current_day_time.replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=SimpleUtc()).isoformat()

    payload = generate_payload(
        midnight_iso_date,
        'govuk-pay',
        'day',
        sumo.total_amount_paid(),
        sumo.payment_volume(),
        sumo.average_amount_paid())

    print payload
    resp = requests.post(URL, json=payload, headers=headers)

    if resp.status_code != 200:
        # This means something went wrong.
        print '{0}'.format(resp.status_code)

    print resp.json()


if __name__ == '__main__':
    lambda_handler({'time': '2017-05-08T16:53:06Z'}, "test")
