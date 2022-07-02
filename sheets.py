import gspread


CREDENTIALS_PATH = './service_account.json' # Шлях до файлу,який можна дістати тут https://console.cloud.google.com/apis/credentials ,створивши новий Service Accounts


gc = gspread.service_account(filename=CREDENTIALS_PATH)
sheet = gc.open('jobbot') # Відкриваємо таблицю

work_sheet = sheet.get_worksheet(0)

def next_available_row(): # Знаходимо вільну колонку
    str_list = list(filter(None, work_sheet.col_values(1)))
    return len(str_list)+1

def insert_in_sheet(id: str,username:str,city:str,offer: str): # Заносимо всі значення в лінію
    work_sheet.update(f'A{next_available_row()}',id)
    work_sheet.update(f'B{next_available_row()-1}',username)
    work_sheet.update(f'C{next_available_row()-1}',city)
    work_sheet.update(f'D{next_available_row()-1}',offer)

def change_offer(id: str,offer: str): # Оновлюємо поле з вакансією користувача в таблиці
    cell = work_sheet.find(id,in_column=1)
    work_sheet.update_cell(cell.row,cell.col+3,offer)


def change_city(id: str,city: str): # Оновлюємо поле з містом користувача в таблиці
    cell = work_sheet.find(id,in_column=1)
    work_sheet.update_cell(cell.row,cell.col+2,city)







