# pay-performance-platform
The GOV.UK Pay performance platform metric publisher

## What is it?

[pay-performance-platform](https://github.com/alphagov/pay-performance-platform) is
a Python script which populates GOV.UK Pay's public [performance dashboard](https://www.gov.uk/performance/govuk-pay).

The script can be run independently with

```
python pay-performance_platform.py
```

or as part of a scheduled Lambda function, or by AWS Config.

## Environment Variables

| Varible | Default | Purpose |
|---------|---------|---------|
|DATASET\_BEARER\_TOKEN |  | Bearer token required by GOV.UK's performance platform dataset. |
|SUMO\_ACCESS\_ID |  | Logging providers access id. |
|SUMO\_ACCESS\_KEY |  | Logging providers access key. |
|ENCRYPTED | false | Determines whether Env Vars are AWS [encrypted](http://docs.aws.amazon.com/lambda/latest/dg/env_variables.html#env_encrypt). 
  and whether the code needs to decrypt them using Boto3. |


