import boto3
import configparser
import json
import urllib

debug = False

def lambda_handler(data, context):

    ### 0 - Parse config
    config = configparser.ConfigParser()
    config.read('wordbot.conf')
    if debug:
        print(config.sections())

    APP_TOKEN = config['slack'].appToken
    BOT_TOKEN = config['slack'].botToken
    POST_URL = config['slack'].postUrl

    S3_KEY = config['s3'].key
    S3_BUCKET = config['s3'].bucket

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
        return data['challenge']

    ### 5 - If the message contains the secret word,
    ###     respond with PWH gif
    else:
        ### 5a - Retrieve the secret word from S3
        client = boto3.client('s3')
        s3response = client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        word = json.loads(s3response.Body.read())['word']

        ### 5b - If the word is contained within the message,
        ###      construct and post response
        if word in event['text']:
            channel = event['channel']
            responseText = 'AAAAAAAAAA!!!!!'
            data = urllib.parse.urlencode(
                (
                    ("token", BOT_TOKEN),
                    ("channel", channel),
                    ("text", responseText)
                )
            )
            data = data.encode("ascii")

            request = urllib.request.Request(
                POST_URL,
                data=data,
                method="POST"
            )
            request.add_header(
                "Content-Type",
                "application/x-www-form-urlencoded"
            )

            urllib.request.urlopen(request).read()

    ### end
    return "200 OK"
