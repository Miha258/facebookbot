from flask import Flask, request
from cities import *
from offers import OFFERS
from messages import *
from flask_sqlalchemy import SQLAlchemy #Модуль для роботи з базою данних в Flask
from sheets import *

app = Flask(__name__)

#Вибір режиму - від цього залежить,яке посилання буде використовуватися програмою,ставте значення "dev" для підключення до локальної бази

ENV = 'prod'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if ENV == 'prod':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bpwxdfgpeklknf:8c154745d20a0bf2e175d86a8a51a3aaa87be45ec4252dd8cc07786fec2c85a8@ec2-52-206-182-219.compute-1.amazonaws.com:5432/d16vk3d9353g47'
elif ENV == 'dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:postgres:admin@localhost/jobbot'


db = SQLAlchemy(app)

VERIFY_TOKEN = 'EAAICQKDCdmIBAHUtJA75etr01'

# Клас для маніпуляції базою данних
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String,nullable=False)
    city = db.Column(db.String(50),nullable=False)
    offer = db.Column(db.String,nullable=False)

    def __init__(self,id,username,city,offer):
        self.id = id
        self.username = username
        self.city = city
        self.offer = offer

    def check_if_exists(self):
        exists = db.session.query(db.exists().where(Users.id == self.id)).scalar()
        if exists:
            return True
        return False

# Створення таблиці в базі данних із стовбцями: id,username,city,offer
db.create_all()



@app.route('/', methods=['GET', 'POST'])
def receive_message():
    print('REQUEST URL: ' + request.url)
    # Перевіряємо токен (для посилання зворотного виклику)
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # Обробляємо повідомлення користувача
    else:
        output = request.get_json() # Конвертуємо в json
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id'] # Дістаємо id автора повідомлення
                    username = requests.get(f'https://graph.facebook.com/{recipient_id}?access_token={ACCESS_TOKEN}').json() # Дістаємо ім'я й прізвище автора повідомлення
                    if message['message'].get('text'): # Якщо повідомлення є текстовим
                        if 'first_name' in username: # Перевірка,чи ім'я автора не є None
                            username = username['first_name'] + ' ' + username['last_name']
                            response_sent_text = get_message(message['message'].get('text').capitalize(),recipient_id,username) # Виклик функції, яка обирає відповідь на повідомлення
                        else: #Якщо ім'я = None
                            response_sent_text = get_message(message['message'].get('text').capitalize(),recipient_id) # Виклик функції, яка обирає відповідь на повідомлення(без username,так як тут воно = None)
                        if response_sent_text:
                            send_message(recipient_id, response_sent_text)  
    return "Message Processed"  


# Функція для валідації токену
def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# Функція для відповіді на повідомлення
def get_message(message_content: str,recipient_id: str,username: str = None):
    # Кнопка "Список міст"
    cities_list_reply = {
        "content_type":"text",
        "title":"Список міст",
        "payload":"Список міст",
    }

    if message_content == 'Почати':
        send_quick_reply(recipient_id,'В якому місті, ви шукаєте роботу?',cities_list_reply)
    
    # Якщо текст = "Список міст",то виводимо цей список з файлу cities.py"
    elif message_content == 'Список міст': #Робимио із списку суцільний текст
        return ",".join(get_cities_list())
    
    # Якщо користувач надіслав повідомлення,текст якого міститься в списку "CITIES" 
    elif message_content in CITIES:
        data = {recipient_id: message_content}
        set_selected_city(data) # Заносим вибране місто користувачем місто у cities.pickle (запамятовуємо його)
        buttons = [] # Кнопки вибору вакансії
        message = 'Виберіть вакансію:\n'
        for i,offer in enumerate(OFFERS,1): # Ділимо список на значення і індекс,починаємо відлак з 1
            message += f'{i}. {offer} \n'
            buttons.append({
                "content_type":"text",
                "title": i,
                "payload": i
            }) # Додаємо нову кноаку у список
        send_quick_reply(recipient_id,message,*buttons) # Надсилаємо повідомлення з кнопками
        
    else:
        # Кнопка "Почати"
        start_reply = {
            "content_type":"text",
            "title":"Почати",
            "payload":"Почати",
        }
        # Якщо текст повідомлення є цифрою
        if message_content.isnumeric():
            index = int(message_content) # Конвертуєм контент у число
            if len(OFFERS) < index or 1 > index: # Якщо користувач ввів невірний номер вакансії
                send_quick_reply(recipient_id,"Невірне число",start_reply,cities_list_reply)
            elif len(OFFERS) >= index: # Якщо індекс правильний
                selected_offer = OFFERS[index-1]
                selected_city = get_selected_city(recipient_id)
                if selected_city: # Якщо вибране місто не None
                    user = Users(recipient_id,username,selected_city,selected_offer) # Екземпляр класу User,для керування базою данних
                    if user.check_if_exists(): # Перевірка,чи користувач занасений у базу данних, якщо так,то оновлюєм його вибір (місто і вакансію)
                        user = Users.query.filter_by(id=recipient_id).first() # Знаходимо його у базі данних
                        user.offer = selected_offer # Вибрану вакансію користувачем, заносимо у стовбець offer
                        change_offer(recipient_id,selected_offer) # Вибрану вакансію користувачем, заносимо у колонку offer в Google Sheets
                        change_city(recipient_id,selected_city) # Вибране місто користувачем,яке ми раніше зьереги у файлі cities.pickle,заносимо у колонку city в Google Sheets
                        user.city = selected_city
                        db.session.commit() # Підтверджуєм зміни у базі данних (обов'язково)
                        return 'Вибрану пропозицію оновлено'
                    else: # Якщо користувач відсутній у базі данних то заносимо його в Google Sheets і в базу данних
                        insert_in_sheet(recipient_id,username,selected_city,selected_offer)
                        db.session.add(user) # Додаємо нового користувача у базу данних
                        db.session.commit() # Підтверджуєм зміни у базі данних (обов'язково)
                        return 'Вас добавлено у список'
                else:
                    send_quick_reply(recipient_id,'Оберіть місто, в якому шукаєте роботу',cities_list_reply) # Якщо вибране місто відсутнє у файлі cities.pickle або воно є None (після кожного вибору файл cities.pickle очищається),то надсилаємо це повідомлення
        else:
            send_quick_reply(recipient_id,"Почніть роботу бота",start_reply,cities_list_reply) # Якщо повідомлення не пройшло ні одну з вище перечиленних перевірок,то надсилаємо це повідомлення
        




if __name__ == "__main__":
    app.run()





