import time
import boto3
from flask import current_app # Flask utility that returns the current runing flask app

#  Function for a time stamp
def utc_now_ts():
    return int(time.time())
    
    
def email(to_email, subject, body_html, body_text):
    # DON'T RUN THIS IF CONDUCTING A TEST
    if current_app.config.get('TESTING'):
        return False
    
    # instantiat a boto3 SES client
    client = boto3.client('ses')
    return client.send_email(
        # email from
        Source='peefer1966@gmail.com',
        # email recipient
            Destination={
                'ToAddresses': [
                    to_email,
                ]
            },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                },                
            }
        }
    )