import random
from flask import Flask, request
from pymessenger.bot import Bot
from cities import CITIES
import requests

app = Flask(__name__)       # Initializing our Flask application
ACCESS_TOKEN = 'EAAICQKDCdmIBAHUtJA75etr01iQG5lH4DhtOMNOfKd6Ssbn6nNlZCliaoxVx08Vtj37wx9w6tQVf78pF4qATFl37eSPgChGx8VCZBVcvZA8PElyjpUwnJWibGcM1GZATVsWUrUEY3QkGrkqNf2CZBOUTnRnEBJBPxJNNh8EQ1xQ2mjz3YV0ia'
VERIFY_TOKEN = 'EAAICQKDCdmIBAHUtJA75etr01'
bot = Bot(ACCESS_TOKEN)


@app.route('/', methods=['GET', 'POST'])
def receive_message():
    print('REQUEST URL: ' + request.url)
    if request.method == 'GET':
        # Before allowing people to message your bot Facebook has implemented a verify token
        # that confirms all requests that your bot receives came from Facebook.
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # If the request was not GET, it  must be POST and we can just proceed with sending a message
    # back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message(message['message'].get('text').capitalize())
                        if response_sent_text:
                            send_message(recipient_id, response_sent_text)
                    # if user send us a GIF, photo, video or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
    return "Message Processed"  


def verify_fb_token(token_sent):
    # take token sent by Facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def get_message(message_content: str = None):
    print(message_content)
    if message_content == 'Почати':
        return 'В якому місті, ви шукаєте роботу?'
    elif message_content in CITIES:
        return '**Якісь пропозиції...**'
    else:
        res = set_get_started()
        print(res)

def set_get_started():
    request_endpoint = '{0}/me/messenger_profile?access_token={1}'.format(bot.graph_url,ACCESS_TOKEN)
    response = requests.post(
        request_endpoint,
        params = bot.auth_args,
        json = { 
            "get_started":  {
                "payload":  "Почати"
            }
        }
    )
    result = response.json()
    return result

# Uses PyMessenger to send response to the user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


# Add description here about this if statement.
if __name__ == "__main__":
    app.run()





