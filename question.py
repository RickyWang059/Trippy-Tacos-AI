import pandas as pd
from sqlalchemy import create_engine
import pymysql

# 資料庫配置
DATABASE_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Rwiacnkgy52559!!',
    'database': 'FAQ',
    'port': 3306
}

# 讀取 FAQ 資料
faq = pd.read_csv('faq.csv', encoding="utf-8")

def initialize_database():
    # 連接 MySQL
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        port=DATABASE_CONFIG['port']
    )
    cursor = connection.cursor()

    # 創建資料庫
    cursor.execute("CREATE DATABASE IF NOT EXISTS FAQ")
    print("資料庫建立成功")

    # 使用資料庫
    cursor.execute("USE FAQ")

    # 創建資料表
    cursor.execute('''CREATE TABLE IF NOT EXISTS faq (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        type TEXT,
                        question TEXT,
                        answer TEXT
                      )
                   ''')
    print("資料表已建立成功")

    # 檢查表格是否為空
    cursor.execute("SELECT COUNT(*) FROM faq")
    result = cursor.fetchone()
    if result[0] == 0:
        engine = create_engine(f'mysql+pymysql://{DATABASE_CONFIG["user"]}:{DATABASE_CONFIG["password"]}@{DATABASE_CONFIG["host"]}:{DATABASE_CONFIG["port"]}/{DATABASE_CONFIG["database"]}')
        faq.to_sql('faq', engine, if_exists='append', index=False)
        print("資料已成功儲存至資料庫")
    else:
        print("資料庫中已存在資料")

    connection.close()
    print("MySQL 連接已關閉")

def update_database():
    engine = create_engine(f'mysql+pymysql://{DATABASE_CONFIG["user"]}:{DATABASE_CONFIG["password"]}@{DATABASE_CONFIG["host"]}:{DATABASE_CONFIG["port"]}/{DATABASE_CONFIG["database"]}')
    faq.to_sql('faq', engine, if_exists='replace', index=False)
    print("資料已成功更新至資料庫")

def fetch_all_faq(faq_type=None):
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database'],
        port=DATABASE_CONFIG['port']
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    if faq_type:
        # 根據指定的 FAQ 類型篩選
        cursor.execute("SELECT question, answer FROM faq WHERE type = %s", (faq_type,))
    else:
        # 若未指定類型，則返回所有 FAQ
        cursor.execute("SELECT question, answer FROM faq")
        
    faq_list = cursor.fetchall()
    
    connection.close()
    return faq_list
