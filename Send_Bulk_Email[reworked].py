# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import csv


csv_path = ""
sender_addr = ""
sender_pswd = ""
subj = ""
msg = ""
ch_attach = ""
at_filename = ""
at_filepath = ""
ch_image = ""
img_path = ""
html_msg = ""

def open_csv(path_csv):
    #read emails from CSV file
    print("Sending mail...")
    with open(path_csv, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            send_email(row[1])
    

def send_email(reciever_addr):
    
    if ch_image == 'y' or ch_image == 'Y' :
        html = html_msg + '<br><img src="cid:image1"><br>'
    else:
        html = html_msg
    
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subj
    msgRoot['From'] = sender_addr
    msgRoot['To'] = reciever_addr
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    
    # Encapsulate the plain and HTML versions of the message body in an
    # 'Alt' part, so message agents can decide which they want to display.
    msgAlt = MIMEMultipart('alternative')
    msgRoot.attach(msgAlt)

    #Attach plain text message    
    msgText = MIMEText(msg,'text')
    msgAlt.attach(msgText)
    
    #Attach html message
    msgText = MIMEText(html, 'html')
    msgAlt.attach(msgText)
    
    #Choice for embedded image
    if ch_image == 'y' or ch_image == 'Y' :
        fp = open(img_path, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        
        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
    
    
    #Choice for Attachment
    if ch_attach == 'y' or ch_attach == 'Y' :
        attachment = open(at_filepath, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % at_filename)
        msgRoot.attach(p)
        
    
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_addr, sender_pswd)
    s.sendmail(sender_addr, reciever_addr, msgRoot.as_string())
    s.quit()
    


def main():
    #Sender list from csv
    global csv_path
    csv_path = input("Enter the path to CSV File : ")
    
    
    #Login Details
    global sender_addr
    sender_addr = input("Enter the login email : ")
    global sender_pswd
    sender_pswd = input("Enter the login password : ")
    
    #Subject
    global subj
    subj = input("Enter Subject for email (else leave blank) : ")
    
    #Text Message
    global msg
    msg = input("Enter plain text message (else leave blank) : ")

    #HTML Message
    global html_msg
    html_msg = input("Enter plain HTML message (else leave blank) : ")
    
    #Choice for embedded image
    global ch_image
    ch_image = input("Do you want send embedded image (Enter 'y' or 'n' ) : ")
    if ch_image == 'y' or ch_image == 'Y' :
        global img_path
        img_path = input("Enter the path of embedded image with extension : ")
    
    #Choice for Attachment
    global ch_attach
    ch_attach = input("Do you want to send attachment (Enter 'y' or 'n' ) : ")
    if ch_attach == 'y' or ch_attach == 'Y' :
        global at_filename
        at_filename = input("Enter the filename for attachment : ")
        global at_filepath
        at_filepath = input("Enter the path for attachment with extension : ")
    
    open_csv(csv_path)
    print("Mails sent successfully")
    
if __name__== "__main__":
  main()
