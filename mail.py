import os
import smtplib
import base64
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import re


import requests


def sendEmailRequest(image_data_url, recipient,person, subject,distance):
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

        successMsgToBe(person,distance)



    except Exception as e:
        print(f"An error occurred: {e}")



def successMsgToBe(obj,distance):
    # URL of the API endpoint
    url = "http://localhost:5100/api/sended-notifications"

    # Payload with data to send
    payload = {
        "name": obj['name'],
        "email": obj['email'],
        "company": obj['company'],
        "distance": distance
    }

    # Sending a POST request to the server with the payload as JSON
    response = requests.post(url, json=payload)

    # Handling the response
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.status_code, response.text)




def sendEmail(image_data_url, subject,distance):

    url = "http://localhost:5100/api/notify-users?limit=10&page=1&column=0&order=desc"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        responseConverted=response.json()
        if(responseConverted['status']):
            for person in responseConverted['data']['records']:
                print(person['email'])
                sendEmailRequest(image_data_url,person['email'],person,subject,distance)




    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server. Make sure it’s running on the specified port.")
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


