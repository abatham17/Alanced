from django.core.mail import EmailMessage
import os

class Util:
    @staticmethod
    def send_email(data):
        email=EmailMessage(
            subject=data['email_subject'],
            body=data['body'],
            from_email="aparnac.wiz91@gmail.com",
            to=[data['to_email']]
        )
        email.content_subtype = 'html'
        email.send()