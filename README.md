# Wordbot
Comes in two parts:
1. Daily script run to retrieve a word from the Wordnik API, post a message to Slack, and save that to a persistent store 
2. Script that listens to Slack activity, and posts when a user uses that day's secret word (todo)

## Requirements
To run, first add your Wordnik API key and your Slack post URL to a `wordbot.conf` file. This file will be used by the script to authenticate to these services and to post messages. Note that `wordbot.conf` is excluded from the git repository, to avoid exposing API keys or other secrets.
The script can be run locally or via a cron or other scheduled function. It currently does not rely on any external AWS services, though that is likely to change when we begin persisting the WoD to a storage function.

## To do
* Save the word of the day to a place the script can retrieve it (S3 will likely be easiest)
* Build the responder portion (likely a large project)