import argparse, sqlite3
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
DB = BASE_DIR / 'db.db'

def create_xlsx(path, headers, rows):
    try:
        from openpyxl import Workbook
    except ModuleNotFoundError:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook(); ws = wb.active; ws.append(headers)
    for row in rows: ws.append(row)
    wb.save(path)

def init(reset=False):
    if reset and DB.exists(): DB.unlink()
    (BASE_DIR/'excel').mkdir(exist_ok=True); (BASE_DIR/'content').mkdir(exist_ok=True); (BASE_DIR/'files').mkdir(exist_ok=True)
    with sqlite3.connect(DB) as conn:
        cur=conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS rates (id INTEGER, from_id INTEGER, text TEXT, rate INTEGER)')
        cur.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT, creator_id INTEGER, name TEXT, about TEXT, target_people TEXT, comment TEXT, price INTEGER, worker TEXT, category TEXT, status TEXT, regs TEXT, report TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT, type TEXT, money INTEGER, bufer_money INTEGER, all_money INTEGER, tasks_cnt INTEGER, rates REAL, rates_cnt INTEGER, sum_rates INTEGER, info TEXT, category TEXT, taken_tasks TEXT)')
        cur.execute("INSERT OR IGNORE INTO users (id, name, username, type, money, bufer_money, all_money, tasks_cnt, rates, rates_cnt, sum_rates, info, category, taken_tasks) VALUES (1001,'Test Customer','demo_customer','customer',15000,0,0,1,-1,0,0,'Demo company profile','-','')")
        cur.execute("INSERT OR IGNORE INTO users (id, name, username, type, money, bufer_money, all_money, tasks_cnt, rates, rates_cnt, sum_rates, info, category, taken_tasks) VALUES (1002,'Test Worker','demo_worker','worker',0,0,0,0,4.8,1,5,'Demo interviewer profile','edit_category_interviews|edit_category_testing','')")
        cur.execute("INSERT OR IGNORE INTO tasks VALUES ('DEMO001',1001,'Demo Interview Task','Interview 5 synthetic users about onboarding','SaaS users','Use the provided demo questionnaire',5000,'-','edit_category_interviews','free','', '')")
        cur.execute("INSERT OR IGNORE INTO rates VALUES (1002,1001,'Synthetic portfolio review',5)")
        conn.commit()
    create_xlsx(BASE_DIR/'files'/'Пример_Данных.xlsx', ['Name','Contact','Question 1'], [['Demo User','demo@example.com','Synthetic answer']])
if __name__ == '__main__':
    init(argparse.ArgumentParser().parse_known_args()[0].__dict__.get('reset', False) or '--reset' in __import__('sys').argv)
