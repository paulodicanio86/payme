import smtplib

import email_texts
from payme import email_account, company, company_email

default_email = {
    'to': [company_email],
    'subject': 'default subject',
    'text': 'default text'
}

def create_email(email=default_email, email_account=email_account):
    """
    Function to send an email.
    If you want to use Port 465 you have to create an SMTP_SSL object:

    server = smtplib.SMTP_SSL(email_account['server'], email_account['port'])
    server.login(email_account['user'], email_account['password'])
    """
    message = 'From: {FROM}\nTo: {TO}\nSubject: {SUBJECT}\n\n{TEXT}'
    message = message.format(FROM=email_account['from'], 
                             TO=', '.join(email['to']),
                             SUBJECT=email['subject'],
                             TEXT=email['text'])
    try:
        server = smtplib.SMTP_SSL(email_account['server'], email_account['port']) #gmail only requires .SMTP(
        #server.ehlo() #gmail requires this
        #server.starttls() #gmail requires this
        server.login(email_account['user'], email_account['password'])
        server.sendmail(email_account['from'], email['to'], message)
        server.close()
        print('successfully sent the mail')
    except:
        print('failed to send mail')


def send_email(to, title, function_text, payment):
    return_text = getattr(email_texts, function_text)
    text = return_text(**payment)
    email = {
        'to': [to],
        'subject': title,
        'text': text
        }
    create_email(email)
    

def send_emails(success, payment):
    '''
    function to send emails, depending on success/failure of payment
    '''
    if success:
        # send email to me
        title_fn = getattr(email_texts, 'return_payment_details_title')
        title = title_fn(**payment)
        send_email(company_email,
                   title,
                   'return_payment_details',
                   payment)
        
        title = '[' + company + '] Successful Payment'
        # send email to sender to notify success
        if payment['email_sender'] != '':
            send_email(payment['email_sender'],
                       title,
                       'return_text_success_sender',
                       payment)

        # send email to receiver to notify success
        if payment['email_receiver'] != '':
            send_email(payment['email_receiver'],
                       title,
                       'return_text_success_receiver',
                       payment)
    else:
        # send email to me
        send_email(company_email,
                   '[failed_payment]',
                   'return_payment_details',
                   payment)
        title = '[' + company + '] Unsuccessful Payment'

        # send email to sender to notify failure
        if payment['email_sender'] != '':
            send_email(payment['email_sender'],
                       title,
                       'return_text_failure_sender',
                       payment)
