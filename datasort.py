from ast import Try
from io import StringIO
import boto3
import json 
import time
import json 

session = boto3.Session(
    aws_access_key_id="---",
    aws_secret_access_key="---"
)

s3_resources = boto3.resource("s3")
s3_client = boto3.client('s3')
textract = session.client('textract')


def handler(event, context):
    print(event)

    job_id = event["job_id"]

    print(job_id)

    content_object = s3_resources.Object(event['bucket_name'], event['blocks']).get()
    file_content =  content_object['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    tables_df = get_df_results(json_content['Blocks'])

    print("tables_df")
    print(tables_df)
    
    return event


def putObjectS3(Key , output_bucket , object):
     s3_client.put_object(
        Bucket = output_bucket,
        Key=Key,
        Body = json.dumps({'result' : object}),
        ServerSideEncryption='AES256',
        ContentType='application/json',
    )

def get_textract_results(job_id):
    response = textract.get_document_analysis(JobId=job_id)
    pages = [response]

    while "NextToken" in response:
        time.sleep(0.25)

        response = textract.get_document_analysis(
            JobId=job_id, NextToken=response["NextToken"]
        )

        pages.append(response)

    return pages

def get_df_results(blocks):

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index +1)
        csv += '\n\n'

    return csv

def generate_table_csv(table_result, blocks_map, table_index):

    rows = get_rows_columns_map(table_result, blocks_map)

    table_id = 'Table_' + str(table_index)
    
    # get cells.
    csv = 'Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():
        
        for col_index, text in cols.items():
            csv += '{}'.format(text) + ","
        csv += '\n'
        
    csv += '\n\n\n'
    return csv
 


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text    