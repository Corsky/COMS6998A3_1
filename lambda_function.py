import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('lex-runtime')
    str = event["queryStringParameters"]["q"]
    xs = str.split("%20")
    str = ""
    for x in xs:
        str = str + " " + x
    str = str[1:]
    response = client.post_text(
        botName='Search',
        botAlias='aaa',
        userId='test',
        inputText="hello"
    )

    response = client.post_text(
        botName='Search',
        botAlias='aaa',
        userId='test',
        inputText=str
    )

    host = "search-photos-epjzjahluh5w2kh6a4ymqo3i4u.us-east-1.es.amazonaws.com"
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    query = {
        "size": 5000,
        'q': response['message']
    }

    headers = {"Content-Type": "application/json"}
    index = 'photos'
    url = 'https://' + host + '/' + index + '/_search'
    r = requests.get(url, auth=awsauth, headers=headers, params=query).json()
    records = r['hits']['hits']
    result = set()
    for r in records:
        result.add(r['_source']['objectKey'])
    result = list(result)
    return {
        'statusCode': "200",
        'headers': {
            'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'list': result
        })
    }
