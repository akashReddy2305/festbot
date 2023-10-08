import json
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
client = boto3.client('dynamodb')
def validate(slots):
    if not slots['fest']:
        print("Inside Empty Location")
        return {
            'isValid': False,
            'violatedSlot': 'fest'
        }
    if not slots['events']:
        print("Inside Empty Location")
        return {
            'isValid': False,
            'violatedSlot': 'events'
        }
    if not slots['rollno']:
        print("Inside Empty Location")
        return {
            'isValid': False,
            'violatedSlot': 'rollno'
        }
    if not slots['mail']:
        print("Inside Empty Location")
        return {
            'isValid': False,
            'violatedSlot': 'mail'
        }
    return { 'isValid':True }
def lambda_handler(event, context):
    # TODO implement
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print(event['invocationSource'])
    print(slots)
    print(intent)
    validation_result = validate(slots)
    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit':validation_result['violatedSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                        }
                    }
               }
        else:
            roll=slots['rollno']['value']['originalValue']
            mail=slots['mail']['value']['originalValue']
            print("Inside else")
            print(roll)
            response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                    },
                "intent": {
                    'name':intent,
                    'slots': slots
                    }
                }
            }
            data = client.get_item(
            TableName='studentDetails',
                Key={
                    'rollno': {
                      'S': roll
                    }
                }
            )
            print(data)
            attendance=data["Item"]["attendance"]['N']
            print('Fetched attendance')
            print(type(attendance))
            if attendance > '80' :
                print('attendance condition')
                fest=slots['fest']['value']['originalValue']
                events=slots['events']['value']['originalValue']
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'akashboomi120@gmail.com'
                smtp_password = 'cdncmpkdpiaoqqnb'
                smtp_tls = True
                # Set up the email message
                sender_email = 'akashboomi120@gmail.com'
                recipient_email = mail
                subject = 'Test Email'
                message_text = 'Congratulations!!, You have recieved permission to attend '+fest+' for the following events '+events
                # message_html = '<html><body><p>Congratulations!!, You have recieved permission to attend FEST</p></body></html>'
                message = MIMEMultipart('alternative')
                message['From'] = sender_email
                message['To'] = recipient_email
                message['Subject'] = subject
                message.attach(MIMEText(message_text, 'plain'))
                # message.attach(MIMEText(message_html, 'html'))
                # Connect to the SMTP server and send the email
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    if smtp_tls:
                        server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender_email, recipient_email, message.as_string())
    return response
