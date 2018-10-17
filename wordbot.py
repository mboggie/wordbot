import json
from wordnik import *
import configparser
import requests
import boto3

debug = False
dryRun = False

def lambda_handler(event, context):

    ### 0 - parse config
    config = configparser.ConfigParser()
    config.read('wordbot.conf')
    if debug:
        print (config.sections())
    wordnikUrl = config['wordnik']['apiUrl']
    wordnikKey = config['wordnik']['apiKey']
    slackUrl = config['slack']['postUrl']

    ### 1 - connect to WordNik API
    wclient = swagger.ApiClient(wordnikKey, wordnikUrl)
    wordsApi = WordsApi.WordsApi(wclient)

    ### 2 - get the word of the day
    wod = wordsApi.getWordOfTheDay()
    if debug:
        print (wod.word)
        for definition in wod.definitions:
            print (definition.partOfSpeech)
            print (definition.text)

    ### 3 - save word for later retrieval / comparison by the listener 
    # Note: boto will be allowed/prevented from writing to s3 by the execution role
    # This will require IAM user configuration, which is documented in docs/notes.md
    s3file = config['s3']['key']
    s3bucket = config['s3']['bucket']
    wordobj = {"word":wod.word}
    awscli = boto3.client('s3')
    s3response = awscli.put_object(Bucket=s3bucket, Key=s3file, Body=json.dumps(wordobj))
    if debug:
        print (json.dumps(s3response))

    ### 4 - format the message for posting
    postText = "Hey, kids! Today's Secret Word is... %s\n\n" % wod.word.upper()
    urlWord = wod.word.replace(' ', '%20');
    postText += "*<http://wordnik.com/words/%s|%s>*\n" % (urlWord, wod.word)
    for idx, definition in enumerate(wod.definitions):
        postText += "%i: _(%s)_ %s\n" % (idx+1, definition.partOfSpeech, definition.text)
    postText += "\nRemember: if you hear the Secret Word, don't forget to SCREAM REAL LOUD!!!"""
    print (postText)

    ### 5 - post message to slack
    msg = {'text': postText, 'mrkdwn': True}
    if not dryRun:
        r = requests.post(slackUrl, json.dumps(msg))
        if debug:
            print (r.text)
    else:
        print ('*** dry run; not posting to Slack ***')


if __name__ == "__main__":
    # if running from the command line, set debug to true for verbose output
    debug = True
    lambda_handler('a', 'b')
