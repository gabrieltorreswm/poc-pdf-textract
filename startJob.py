#!/usr/bin/env python3

import boto3
import json
import time

s3 = boto3.client("s3")
textract_client = boto3.client('textract')

def handler(event, context):
    print("event")
    print(event)
    if event['source'] != 'aws.s3':
        raise ValueError("ERROR: Unexpected event type")

    bucket_name = event['detail']['bucket']['name']
    object_name = event['detail']['object']['key']

    print(f"StartJob: s3://{bucket_name}/{object_name}")

    job_id = _startJob(bucket_name, object_name)
    print(f"JobId: {job_id}")

    return {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "job_id": job_id,
        "job_start_timestamp": time.time()
    }    


def _startJob(bucket_name, object_name):
    response = textract_client.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_name,
            }
        },
        FeatureTypes=['TABLES','FORMS'],
    )

    return response["JobId"]
