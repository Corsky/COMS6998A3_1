import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # TODO implement
    name = event['Records'][0]['s3']['object']['key']

    client = boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object': {'Bucket': "yz3831-hw3-b2", 'Name': name}},
                                    MaxLabels=10,
                                    MinConfidence=75)
    label = []
    for l in response['Labels']:
        label.append(l['Name'])

    host = "search-photos-epjzjahluh5w2kh6a4ymqo3i4u.us-east-1.es.amazonaws.com"
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,
                       session_token=credentials.token)

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    doc = {
        'objectKey': name,
        'bucket': "yz3831-hw3-b2",
        'createTimestamp': event['Records'][0]['eventTime'],
        'labels': label,
    }
    response = es.index(index="photos", body=doc)
    return {
        'statusCode': 200,
        'doc': doc,
        'resp': response,
    }
