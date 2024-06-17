import os
import time
import sqlite3
import logging
from services import getmachines, curstate

def curstate_task():
    try:
        delete_curstate()
        result = getmachines()        
        if result:
            machines = result.get('machines', [])
            for machine in machines:
                get_curstate(machine.get('guid'))
    except Exception as e:
        logging.error(f"Ошибка в get_curstate: {e}")

def get_curstate(guid):
    try:
        # Получаем текущее состояние машины и обновляем запись в базе данных
        result = curstate(guid=guid)
        if result:
            data = {
                "machine": guid,
                "state": result.get('state'),
                "vendscount": result.get('vendscount', 0),
                "vendscost": result.get('vendscost', 0) / 10 ** result.get('decimal', 2),
                "empty_cells": len([cell for cell in result.get('products', []) if cell.get('level', 0) == 0]) if result.get('coffee') == False else 0
            }
            update_curstate(guid=guid, data=data)
    except Exception as e:
        logging.error(f"Ошибка в get_curstate: {e}")

def update_curstate(guid, data):
    conn = None
    try:
        # Обновляем текущее состояние машины в базе данных
        conn = sqlite3.connect('unicum.db')
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM curstate WHERE guid = ?", (guid,))
        machine = cursor.fetchone()

        if not machine:
            # Если записи не существует, создаем новую
            cursor.execute("INSERT INTO curstate (guid) VALUES (?)", (guid,))
            conn.commit()

        # Обновляем данные о состоянии машины
        cursor.execute("UPDATE curstate SET state = ?, vendscount = ?, vendscost = ?, empty_cells = ?, update_datetime = datetime('now', 'localtime') WHERE guid = ?", (data.get('state'), data.get('vendscount'), data.get('vendscost'), data.get('empty_cells'), guid))
        conn.commit()
    except Exception as e:
        logging.error(f"Ошибка в update_curstate: {e}")
    finally:
        if conn:
            conn.close()

def delete_curstate():
    conn = None
    try:
        # Удаляем устаревшие записи о состоянии машин из базы данных
        conn = sqlite3.connect('unicum.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM curstate WHERE update_datetime < datetime('now', '-24 hours')")
        conn.commit()
    except Exception as e:
        logging.error(f"Ошибка в delete_curstate: {e}")
    finally:
        if conn:
            conn.close()

def select_all_curstate():
    conn = None
    try:        
        # Выполняем запрос всех записей из таблицы curstate
        conn = sqlite3.connect('unicum.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()        
        cursor.execute("SELECT * FROM curstate") 
        rows = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for row in rows:
            result.append({
                'guid': row['guid'],
                'state': row['state'],
                'vendscount': row['vendscount'],
                'vendscost': row['vendscost'],
                'empty_cells': row['empty_cells'],
                'update_datetime': row['update_datetime']
            })
        return result
    except Exception as e:
        logging.error(f"Ошибка в select_all_curstate: {e}")
        return []
    finally:
        if conn:
            conn.close()