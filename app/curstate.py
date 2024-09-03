import os
import time
import sqlite3
import logging
from services import getmachines, curstate

def curstate_task():
    try:
        print('Обновлняем')
        delete_curstate()
        result = getmachines()        
        if result:
            machines = result.get('machines', [])
            for machine in machines:
                coins = {
                    "coin_1": 0,
                    "coin_2": 0,
                    "coin_5": 0,
                    "coin_10": 0
                }

                if machine.get('device') is not None and machine.get('device').get('changer') is not None:
                    try:
                        tubes = machine.get('device', {}).get('changer', {}).get('tubes', [])
                        for tube in tubes:
                            coin_value = int(float(tube['value']))
                            key = f'coin_{coin_value}'
                            coins[key] = coins[key] + tube['count']
                    except Exception as e:
                        logging.error(f"Ошибка в curstate_task {machine.get('guid')}: {e}")
                get_curstate(machine.get('guid'), coins)
    except Exception as e:
        logging.error(f"Ошибка в curstate_task: {e}")

def get_curstate(guid, coins):
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
            update_curstate(guid=guid, data=data, coins=coins)
    except Exception as e:
        logging.error(f"Ошибка в get_curstate: {e}")

def update_curstate(guid, data, coins):
    conn = None
    try:
        # Обновляем текущее состояние машины в базе данных
        conn = sqlite3.connect('unicum.db', timeout=10)
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM curstate WHERE guid = ?", (guid,))
        machine = cursor.fetchone()

        if not machine:
            # Если записи не существует, создаем новую
            cursor.execute("INSERT INTO curstate (guid) VALUES (?)", (guid,))
            conn.commit()
        # Обновляем данные о состоянии машины
        cursor.execute("UPDATE curstate SET state = ?, vendscount = ?, vendscost = ?, empty_cells = ?, update_datetime = datetime('now', 'localtime'), coin_1 = ?, coin_2 = ?, coin_5 = ?, coin_10 = ? WHERE guid = ?", 
                       (data.get('state'), data.get('vendscount'), data.get('vendscost'), data.get('empty_cells'),
                        coins.get('coin_1'), coins.get('coin_2'), coins.get('coin_5'), coins.get('coin_10'),
                        guid))
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
        conn = sqlite3.connect('unicum.db', timeout=10)
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
        conn = sqlite3.connect('unicum.db', timeout=10)
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

def select_all_tubes():
    conn = None
    try:        
        # Выполняем запрос всех записей из таблицы curstate
        conn = sqlite3.connect('unicum.db', timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()        
        cursor.execute("SELECT * FROM curstate") 
        rows = cursor.fetchall()
        
        # Преобразуем результаты в список словарей
        result = []
        for row in rows:
            result.append({
                'guid': row['guid'],
                'vendscount': row['vendscount'],
                'update_datetime': row['update_datetime'],
                'coin_1': row['coin_1'],
                'coin_2': row['coin_2'],
                'coin_5': row['coin_5'],
                'coin_10': row['coin_10']
            })
        return result
    except Exception as e:
        logging.error(f"Ошибка в select_all_curstate: {e}")
        return []
    finally:
        if conn:
            conn.close()