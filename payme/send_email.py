import smtplib

account = {
    'user': 'paul.schaack2@gmail.com',
    'password': '',
    'server': 'smtp.gmail.com',
    'port': 587,
    'from': 'paul.schaack2@gmail.com'
}

email = {
    'to': ['paul.schaack@gmail.com'],
    'subject': 'default subject',
    'text': 'default text'
}


def send_email(email=email, account=account):
    """
    Function to send an email.
    If you want to use Port 465 you have to create an SMTP_SSL object:

    server = smtp.lib.SMTP_SSL(account['server'], account['port'])
    server.login(account['user'], account['password'])
    """
    message = 'From: {FROM}\nTo: {TO}\nSubject: {SUBJECT}\n\n{TEXT}'
    message = message.format(FROM=account['from'], 
                             TO=', '.join(email['to']),
                             SUBJECT=email['subject'],
                             TEXT=email['text'])
    try:
        server = smtplib.SMTP(account['server'], account['port'])
        server.ehlo()
        server.starttls()
        server.login(account['user'], account['password'])
        server.sendmail(account['from'], email['to'], message)
        server.close()
        print 'successfully sent the mail'
    except:
        print 'failed to send mail'

