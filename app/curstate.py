import os
import time
import sqlite3
import json
from services import getmachines, curstate

def thread_curstate():
    # Поток для обработки текущего состояния машин
    while os.environ['CURSTATE'] == '1':
        # Получаем следующую машину из очереди или обновляем текущую
        machine = get_next_machine()
        row_count = machine.get('row_count')
        if row_count == 0:
            # Если очередь пуста, удаляем устаревшие записи и ждем
            delete_curstate()
            time.sleep(60)            
        else:
            # Получаем текущее состояние машины и обновляем запись
            get_curstate(machine.get('guid'))

def get_next_machine():
    try:
        # Получаем следующую машину из очереди или добавляем новые
        conn = sqlite3.connect('app/unicum.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM curstate_queue")
        row_count = cursor.fetchone()[0]
        unicum_guid = ''
        if row_count == 0:        
            # Если очередь пуста, получаем новые машины и добавляем в очередь
            result = getmachines()
            if result:
                machines = result.get('machines', [])
                for machine in machines:
                    cursor.execute("INSERT INTO curstate_queue (unicum_guid) VALUES (?)", (machine.get('guid'),))            
        else:
            # Если очередь не пуста, получаем следующую машину из очереди
            cursor.execute("SELECT unicum_guid FROM curstate_queue LIMIT 1")
            unicum_guid = cursor.fetchone()[0]
            cursor.execute("DELETE FROM curstate_queue WHERE unicum_guid = ?", (unicum_guid,))
        conn.commit()
        return { "guid": unicum_guid, "row_count": row_count }
    except Exception as e:
        print(f"Ошибка в get_next_machine: {e}")
        return None
    finally:
        conn.close()

def get_curstate(guid):
    try:
        # Получаем текущее состояние машины и обновляем запись в базе данных
        result = curstate(guid=guid)
        if result:
            data = {
                "machine": guid,
                "state": result.get('state'),
                "vendscount": result.get('vendscount', 0),
                "empty_cells": len([cell for cell in result.get('products', []) if cell.get('level', 0) == 0]) if result.get('coffee') == False else 0
            }
            update_curstate(guid=guid, data=data)
    except Exception as e:
        print(f"Ошибка в get_curstate: {e}")

def update_curstate(guid, data):
    try:
        # Обновляем текущее состояние машины в базе данных
        conn = sqlite3.connect('app/unicum.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM curstate WHERE guid = ?", (guid,))
        machine = cursor.fetchone()

        if not machine:
            # Если записи не существует, создаем новую
            cursor.execute("INSERT INTO curstate (guid) VALUES (?)", (guid,))
            conn.commit()

        # Обновляем данные о состоянии машины
        cursor.execute("UPDATE curstate SET state = ?, vendscount = ?, empty_cells = ?, update_datetime = datetime('now', 'localtime') WHERE guid = ?", (data.get('state'), data.get('vendscount'), data.get('empty_cells'), guid))
        conn.commit()
    except Exception as e:
        print(f"Ошибка в update_curstate: {e}")
    finally:
        conn.close()

def delete_curstate():
    try:
        # Удаляем устаревшие записи о состоянии машин из базы данных
        conn = sqlite3.connect('app/unicum.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM curstate WHERE update_datetime < datetime('now', '-24 hours')")
        conn.commit()
    except Exception as e:
        print(f"Ошибка в delete_curstate: {e}")
    finally:
        conn.close()

def select_all_curstate():
    try:        
        # Выполняем запрос всех записей из таблицы curstate
        conn = sqlite3.connect('app/unicum.db')
        cursor = conn.cursor()        
        cursor.execute("SELECT * FROM curstate") 
        rows = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for row in rows:
            result.append({
                'guid': row[0],
                'state': row[1],
                'vendscount': row[2],
                'empty_cells': row[3],
                'update_datetime': row[4]
            })
        
        return result
    except Exception as e:
        print(f"Ошибка в select_all_curstate: {e}")
        return None
    finally:
        conn.close()