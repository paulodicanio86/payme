import smtplib
from payme import email_account

email = {
    'to': ['paul.schaack@gmail.com'],
    'subject': 'default subject',
    'text': 'default text'
}


def send_email(email=email, email_account=email_account):
    """
    Function to send an email.
    If you want to use Port 465 you have to create an SMTP_SSL object:

    server = smtp.lib.SMTP_SSL(email_account['server'], email_account['port'])
    server.login(email_account['user'], email_account['password'])
    """
    message = 'From: {FROM}\nTo: {TO}\nSubject: {SUBJECT}\n\n{TEXT}'
    message = message.format(FROM=email_account['from'], 
                             TO=', '.join(email['to']),
                             SUBJECT=email['subject'],
                             TEXT=email['text'])
    try:
        server = smtplib.SMTP(email_account['server'], email_account['port'])
        server.ehlo()
        server.starttls()
        server.login(email_account['user'], email_account['password'])
        server.sendmail(email_account['from'], email['to'], message)
        server.close()
        print('successfully sent the mail')
    except:
        print('failed to send mail')


def return_success_text(name_sender, name_account, account_number,
                        sort_code, amount, reference):
    text = '''
    Dear {name_sender},\n
    You have successfully paid {amount}, which will reach the account of {name_account}
    (Account number: {account_number}, Sort Code: {sort_code}, Reference: {reference})
    asap.\n
    Thank you for using our service.
    '''.
    text = text.format(name_sender=name_sender,
                       amount=amount,
                       name_account=name_account,
                       account_number=account_number,
                       sort_code=sort_code,
                       reference=reference)
    return text


def email_success(email_sender, name_sender, name_account, account_number,
                  sort_code, amount, reference):
    text = return_success_text(name_sender,
                               name_account,
                               account_number,
                               sort_code,
                               amount,
                               reference)
    email = {
        'to': [email_sender],
        'subject': 'Successfull payment',
        'text': text
        }
    send_email(email)
    



