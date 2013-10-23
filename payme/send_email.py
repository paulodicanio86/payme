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
    # Prepare message
    message = 'From: {FROM}\nTo: {TO}\nSubject: {SUBJECT}\n\n{TEXT}'
    message = message.format(FROM=account['from'], 
                             TO=', '.join(email['to']),
                             SUBJECT=email['subject'],
                             TEXT=email['text'])
    try:
        #server = smtplib.SMTP(SERVER) 
        server = smtplib.SMTP(account['server'], account['port']) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(account['user'], account['password'])
        server.sendmail(account['from'], email['to'], message)
        #server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print 'failed to send mail'

