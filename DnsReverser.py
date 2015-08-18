__author__ = 'Saman'
from mysql.connector import MySQLConnection
from config import read_db_config
from config import config_section_map
from colorama import Fore
from colorama import init
import datetime
from time import sleep
from Bing import reverse_dns

init()


def db_select(query):
    db_reconnect_status = 0
    while db_reconnect_status == 0:
        try:
            global conn
            query_result_exec = conn.cursor()
            query_result_exec.execute(query)
            query_result = query_result_exec.fetchall()
            db_reconnect_status += 1
            return query_result, query_result_exec.rowcount
        except Exception:
            db_reconnect2_status = 0
            while 0 == db_reconnect2_status:
                print(Fore.RED + 'Connecting Database...' + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(),
                                                                                          end='\r'))
                try:
                    db_config = read_db_config()
                    conn = MySQLConnection(**db_config)
                    db_reconnect2_status += 1
                    print(Fore.RED + 'Database Connection ID:' + str(conn.connection_id))
                except Exception:
                    sleep(5)
                    db_reconnect2_status = 0


def db_update(query):
    db_reconnect_status = 0
    global conn
    while db_reconnect_status == 0:
        try:
            query_result_exec = conn.cursor()
            query_result_exec.execute(query)
            conn.commit()
            db_reconnect_status += 1
            query_rows = query_result_exec.rowcount
            query_id = conn.connection_id
            return query_rows, query_id
        except Exception:
            db_reconnect2_status = 0
            while 0 == db_reconnect2_status:
                print(Fore.RED + 'Connecting Database...' + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(),
                                                                                          end='\r'))
                try:
                    db_config = read_db_config()
                    conn = MySQLConnection(**db_config)
                    db_reconnect2_status += 1
                    print(Fore.BLUE + 'Database Connection ID:' + str(conn.connection_id))
                except Exception:
                    sleep(5)
                    db_reconnect2_status = 0


def main():
    conn_id = None
    global conn

    while conn_id is None:
        try:
            db_config = read_db_config()
            conn = MySQLConnection(**db_config)
            conn_id = conn.connection_id
        except Exception:
            conn_id = None
            print('Try connecting to database...')

    if config_section_map("dns_reverser")['default_list_name']:
        selected_list = str(config_section_map("dns_reverser")['default_list_name'])
        todo_result_rows = 1
        process_counter = 0
        while todo_result_rows > 0:
            todo_query = 'select distinct(ip) from %s where ip is not null and ip!=\'Fail\' and ip not in ' \
                         '(select refrence from harverster_hosts) limit %s' % \
                         (selected_list, int(config_section_map("dns_reverser")['buffer']))
            todo_result, todo_result_rows = db_select(todo_query)

            if todo_result:

                for to_do_line in range(0, len(todo_result)):
                    process_counter += 1

                    look_for = todo_result[to_do_line][0]
                    looking_for = (str(look_for.strip()))

                    reverse_result = reverse_dns(looking_for)
                    for line in reverse_result:
                        return_insert_query = "insert into  harverster_hosts (host,refrence) " \
                                              "values ('%s','%s')" \
                                              % ((reverse_result[line][0])[:100], todo_result[to_do_line][0])
                        db_update(return_insert_query)


if __name__ == '__main__':
    main()
