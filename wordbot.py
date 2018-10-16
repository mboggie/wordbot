import json
from wordnik import *
import configparser
import requests

debug = False

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
            print (definition.text)

    ### 3 - save word for later retrieval / comparison by the listener [TBD]

    ### 4 - post message to slack
    msg = {}
    
    # this needs to be fleshed out a lot to have definitions, etc
    # check slack docs on message formatting here:
    # https://api.slack.com/docs/messages
    msg['text'] = wod.word

    # POST to webhook url 
    r = requests.post(slackUrl, json.dumps(msg))
    if debug:
        print (r.text) 

if __name__ == "__main__":
    # if running from the command line, set debug to true for verbose output
    debug = True
    lambda_handler('a', 'b')
