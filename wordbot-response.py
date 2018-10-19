import boto3
import configparser
import json
import requests

debug = False
dryRun = False

def lambda_handler(data, context):

    ### 0 - Parse config
    config = configparser.ConfigParser()
    config.read('wordbot.conf')
    if debug:
        print(config.sections())

    APP_TOKEN = config['slack']['appToken']
    POST_URL = config['slack']['postUrl']

    S3_KEY = config['s3']['key']
    S3_BUCKET = config['s3']['bucket']

    ### 1 - Get the slack event data
    eventToken = data['token']
    event = data['event']

    ### 2 - Validate event token
    if eventToken != APP_TOKEN:
        print ('*** message not posted from Slack... ignoring')

    ### 3 - If the message was posted by a bot, ignore it
    elif 'bot_id' in event:
        print ('*** message posted by bot... ignoring')

    ### 4 - If the message is a "challenge", respond accordingly
    elif 'challenge' in data:
        print ('*** challenge accepted:', data['challenge'])
        return data['challenge']

    ### 5 - If the message contains the secret word,
    ###     respond with PWH gif
    else:
        ### 5a - Retrieve the secret word from S3
        client = boto3.client('s3')
        s3response = client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        word = json.loads(s3response['Body'].read())['word']

        ### 5b - If the word is contained within the message,
        ###      construct and post response
        if word.lower() in event['text'].lower():
            responseText = 'AAAAAAAAAA!!!!!'
            response = {'text': responseText, 'mrkdwn': True}
            if not dryRun:
                requests.post(POST_URL, json.dumps(response))
            print (response)

        else:
            print ("*** word not in message... ignoring")

    ### end
    return "200 OK"

if __name__ == "__main__":
    debug = True

    testData = {
        'token': '0c51a8a8afc3d190f55fd848200d5842',
        'event': {
            'text': 'this is a Paleotechnical test'
            }
        }
    lambda_handler(testData, None)
