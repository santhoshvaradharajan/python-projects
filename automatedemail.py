import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_addr = 'Enter your mail here'

data = pd.read_csv("abc.csv")
to_addr = data['email'].tolist()
name = data['name'].to_list()

l = len(name)

email = ""
password = ""

for i in range(l):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr[i]
    msg['subject'] = 'just to check'

    body = name[i] + 'enter your content here'

    msg.attach(MIMEText(body, 'plain'))

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(email, password)
    text = msg.as_string()
    mail.sendmail(from_addr,to_addr[i], text)
    msg.quit()