import time
import boto3

#  Function for a time stamp
def utc_now_ts():
    return int(time.time())
    
    
def email(to_email, subject, body_html, body_text):
    # instantiat a boto3 ses client
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