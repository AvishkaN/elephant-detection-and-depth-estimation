import os
import smtplib
import base64
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import re
recipientList=['avpersonal7888@gmail.com']

def sendEmail(image_data_url, recipient=recipientList[0], subject='⚠️ DANGER ALERT: Elephant and Human Detected!'):
    try:
        # Load environment variables
        load_dotenv()
        my_email = os.getenv("FROM_EMAIL")
        password = os.getenv("FROM_EMAIL_PASSWORD")

        if not my_email or not password:
            raise ValueError("Email credentials not found in environment variables.")

        # Load the HTML template with proper encoding to avoid decoding errors
        with open("mail/email_template.html", "r", encoding="utf-8") as file:
            html_template = file.read()

        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = my_email
        msg['To'] = recipient
        msg['Subject'] = subject

        # Check if the image_data_url is base64-encoded
        if image_data_url.startswith('data:image'):
            # Extract the base64-encoded part of the image
            base64_str = re.search(r'base64,(.*)', image_data_url).group(1)
            img_data = base64.b64decode(base64_str)

            # Attach the image
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<image1>')
            img.add_header('Content-Disposition', 'inline', filename="image_from_base64.jpg")
            msg.attach(img)

            # Replace the placeholder with the Content-ID
            html_template = html_template.replace("{image_src}", "cid:image1")

        # Handle HTTP/HTTPS image URL
        elif image_data_url.startswith('http'):
            # No need to embed the image, just replace the src attribute with the URL
            html_template = html_template.replace("{image_src}", image_data_url)

        else:
            raise ValueError("Invalid image_data_url. It should be either a base64-encoded data URL or an HTTP/HTTPS URL.")

        # Attach the updated HTML body
        msg.attach(MIMEText(html_template, 'html'))

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=recipient, msg=msg.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
