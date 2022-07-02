import requests
from pymessenger.bot import Bot


ACCESS_TOKEN = 'EAAICQKDCdmIBAHUtJA75etr01iQG5lH4DhtOMNOfKd6Ssbn6nNlZCliaoxVx08Vtj37wx9w6tQVf78pF4qATFl37eSPgChGx8VCZBVcvZA8PElyjpUwnJWibGcM1GZATVsWUrUEY3QkGrkqNf2CZBOUTnRnEBJBPxJNNh8EQ1xQ2mjz3YV0ia'
bot = Bot(ACCESS_TOKEN,api_version=14.0)


def send_quick_reply(recipient_id: str,text: str,*replies: str) -> dict:
    request_endpoint = '{0}/me/messages'.format(bot.graph_url)
    data = {
        "recipient":{
            "id": recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": text,
            "quick_replies": list(replies)
        }
    }
    r = requests.post(f'{request_endpoint}?access_token={ACCESS_TOKEN}',params=bot.auth_args,json=data)
    return r.json()
    

def send_message(recipient_id, response) -> str:
    bot.send_text_message(recipient_id, response)
    return "success"