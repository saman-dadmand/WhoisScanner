__author__ = 'Saman'
from mysql.connector import MySQLConnection
from config import read_db_config
from config import config_section_map
from colorama import Fore
from colorama import init
import datetime
from time import sleep
import socket

from re import findall

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
            return query_result
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


def host2ip(site):
    try:
        host = socket.gethostbyaddr(site)
        ip = findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', str(host[2]))
        return ip[0]
    except socket.error:
        return 'Fail'


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

    if config_section_map("ip_resolver")['default_list_name']:
        selected_list = str(config_section_map("ip_resolver")['default_list_name'])
        loop_counter = 1
        process_counter = 0
        while loop_counter > 0:
            # lock record for process
            lock_record_query = 'update %s set lockedby=connection_id(),lockedat=now(),HFlag=\'I\' ' \
                                'where lockedby is null and status=\'Site registered\' ' \
                                'and (ip is null or ip=\'Fail\') and trycount<%s order by trycount limit %s '\
                                % (selected_list,config_section_map("ip_resolver")['try_count'],
                                    int(config_section_map("ip_resolver")['buffer']))
            loop_counter, connection_d = db_update(lock_record_query)

            if loop_counter:
                todo_query = 'select no,site from %s where  lockedby=%s ' % (
                    selected_list, connection_d)
                todo_result = db_select(todo_query)
                if todo_result:

                    for to_do_line in range(0, len(todo_result)):
                        process_counter += 1
                        try:
                            look_for = todo_result[to_do_line][1]
                            looking_for = (str(look_for.strip()))
                            ip = host2ip('www.' + looking_for)
                            print(Fore.CYAN + looking_for+': '+ip)
                            return_update_query = "update %s set HFlag=\'R\',lockedby=null,ip='%s' " \
                                                  ",trycount=trycount+1 where  No=%s " \
                                                  % (selected_list,ip, todo_result[to_do_line][0])
                            db_update(return_update_query)

                        except Exception:
                            print('exception')
                            return_update_query = "update %s set HFlag=Null,lockedby=null " \
                                                  ",trycount=trycount+1 where  No=%s " \
                                                  % (selected_list, todo_result[to_do_line][0])
                            db_update(return_update_query)
                else:
                    print('All record are processed for ' + selected_list + ' list!')

if __name__ == '__main__':
    main()
