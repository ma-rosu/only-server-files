import boto3
import os
import time

class SNSAgent:
    def __init__(self, message_title: str, message_body_prefix: str):
        self.aws_region = os.getenv('AWS_REGION', 'eu-central-1')
        self.sns_client = boto3.client('sns', region_name=self.aws_region)
        self.message_title = message_title
        self.message_body_prefix = message_body_prefix
        self.send_sms()

    def _get_phone_number_from_file(self, filename: str = 'number.txt') -> str | None:
        try:
            with open(filename, 'r') as f:
                phone_number = f.readline().strip()
                if not phone_number:
                    print(f"Error: File '{filename}' is empty or does not contain a valid phone number.")
                    return None
                return phone_number
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found. Please create '{filename}' with the phone number on the first line.")
            return None
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            return None

    def send_sms(self):
        phone_number = self._get_phone_number_from_file()

        if not phone_number:
            print("Could not get phone number. SMS not sent.")
            return None

        if not phone_number.startswith('+'):
            print("Warning: Phone number should start with '+'.")

        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{self.message_title} - {self.message_body_prefix} {current_time}\nCheck the camera on the EyeCheck."

        params = {
            'PhoneNumber': phone_number,
            'Message': full_message,
            'MessageAttributes': {
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        }
        
        try:
            response = self.sns_client.publish(**params)
            message_id = response['MessageId']
            print(f"SMS sent successfully! Message ID: {message_id}")
            return message_id
        except Exception as e:
            print(f"Error sending SMS: {e}")
            print(f"Please check: 1. IAM permissions for the attached EC2 role. 2. SNS SMS spending limit. 3. Phone number (international prefix and if it's in sandbox).")
            return None
