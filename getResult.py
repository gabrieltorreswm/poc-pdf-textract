
import os
import json
import time
import boto3

s3_client = boto3.client('s3')
textract_client = boto3.client('textract')


def handler(event, context):
    job_id = event['job_id']

    print(job_id)
    results = getJobResults(job_id)
    event['job_status'] = results['JobStatus']
    event['job_update_timestamp'] = time.time()

    if event['job_status'] != "SUCCEEDED":
        # Include the results unless the job is still in progress
        # Useful for investigating failures
        if event['job_status'] != "IN_PROGRESS":
            event['results'] = results
        return event

    # Job succeeded - retrieve the results
    input_bucket = event['bucket_name']
    input_object = event['object_name']

    output_bucket = input_bucket
    output_prefix = 'output/'

    output_object_base = os.path.join(output_prefix, os.path.basename(input_object))

    event['output_bucket'] = output_bucket
    event['raw_results'] = []
    page_counter = 0
    blocks = []

    while True:
        page_counter += 1
        print(len(blocks))
        output_object = f"{output_object_base}.raw.{page_counter:02d}.json"
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_object,
            Body=json.dumps(results),
            ServerSideEncryption='AES256',
            ContentType='application/json',
        )
        event['raw_results'].append(output_object)
        print(f"Result {page_counter:02} saved to: s3://{output_bucket}/{output_object}")

        if 'Blocks' in results:
            blocks.extend(results['Blocks'])

        if 'NextToken' not in results:
            break

        print(f"NextToken: {results['NextToken']}")
        results = getJobResults(job_id, next_token=results['NextToken'])


    print(len(blocks))
    # Save merged 'Blocks' into a separate file for ease of use
    output_object = f"{output_object_base}.blocks.json"
    s3_client.put_object(
        Bucket=output_bucket,
        Key=output_object,
        Body=json.dumps({'Blocks': blocks}),
        ServerSideEncryption='AES256',
        ContentType='application/json',
    )
    print(f"Blocks file saved to: s3://{output_bucket}/{output_object}")
    event['blocks'] = output_object

    return event

def getJobResults(job_id, next_token = None):
    kwargs = {}
    if next_token:
        kwargs['NextToken'] = next_token

    print("kwargs")
    print(kwargs)
    response = textract_client.get_document_analysis(JobId=job_id, **kwargs)

    return response
