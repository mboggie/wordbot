import boto3
import configparser
import json
import requests

debug = False
dryRun = False

def lambda_handler(data, context):
    if debug:
        print(json.dumps(data))

    ### 0 - Parse config
    config = configparser.ConfigParser()
    config.read('wordbot.conf')
    if debug:
        print(config.sections())

    # App Token == "Bot User Access Token" in the Slack console
    APP_TOKEN = config['slack']['appToken']
    RESPOND_URL = config['slack']['respondUrl']

    S3_KEY = config['s3']['key']
    S3_BUCKET = config['s3']['bucket']

    ### 1 - Get the slack event data
    eventToken = data['token']
    event = data['event']

    ### 2 - Validate event token
    ### TODO - Slack has changed the verification process significantly
    ### More info here on checking that this message is valid and not spam:
    ### https://api.slack.com/docs/verifying-requests-from-slack

    #if eventToken != APP_TOKEN:
    #    print ('*** message not posted from Slack... ignoring')
   
    ### 3 - If the message was posted by a bot, ignore it
    if 'bot_id' in event:
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
        word = json.loads(s3response['Body'].read())['word']
        if debug:
            print("word is %s\n" % word)

        ### 5b - If the word is contained within the message,
        ###      construct and post response

        ### TODO - need to validate that the event is a message FIRST before checking if 'text' is present
        ### this is throwing log errors
        if word.lower() in event['text'].lower():
            # get the channel we're going to reply into
            channel_id = event['channel']
            responseText = 'AAAAAAAAAA!!!!!'

            # We need to set HTTP headers on the POST request that:
            # 1. Confirm we are who we say we are (using the Authorization header)
            # 2. Tell Slack we're going to send JSON and not form-encoded data
            authstring = "Bearer " + APP_TOKEN
            headers = {'Authorization': authstring, 'Content-Type': 'application/json'}

            # the extra details in the response here allow us to post in the specific channel
            response = {'token': APP_TOKEN, 'channel': channel_id, 'text': responseText, 'mrkdwn': True}

            if not dryRun:
                requests.post(RESPOND_URL, json.dumps(response), headers=headers)
            print (response)

        else:
            if debug:
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
