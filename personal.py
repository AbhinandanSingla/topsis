import smtplib
gmail_user = 'deepusingla0448@gmail.com'
gmail_password = 'sjmbidmwrjchprkd'

sent_from = gmail_user
to = ['kadiyans990@gmail.com']
subject = 'Lorem ipsum dolor sit amet'
body = 'consectetur adipiscing elit'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()
    print("Email sent successfully!")
except Exception as ex:
    print("Something went wrong….", ex)
