from telnetlib import Telnet
from re import search
from time import sleep
import datetime
import math
import winsound
import sys
import socket
from mysql.connector import MySQLConnection
from tabulate import tabulate
from config import read_db_config
from config import config_section_map
from config import internet_status
from config import public_ip
from config import mail_sender

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
                print('Reconnecting Database...'+'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(), end='\r'))
                try:
                    db_config = read_db_config()
                    conn = MySQLConnection(**db_config)
                    db_reconnect2_status += 1
                    print('Database Connection ID:'+str(conn.connection_id))
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
                print('Reconnecting Database...'+'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(), end='\r'))
                try:
                    db_config = read_db_config()
                    conn = MySQLConnection(**db_config)
                    db_reconnect2_status += 1
                    print('Database Connection ID:'+str(conn.connection_id))
                except Exception:
                    sleep(5)
                    db_reconnect2_status = 0


def telnet_parser(telnet_result, todo_result, to_do_line, look_for, selected_list, looking_for):
    search_result = search('no entries found', telnet_result)
    search_unregable = search('This domain is not available for registration', telnet_result)
    search_special = search(
        'This domain is only available for registration under certain conditions',
        telnet_result)

    if search_result:  # Find Site Available For Normal Register
        print(str(todo_result[to_do_line][0]) + " : Site is not registered --> ", look_for, end='\r')
        # update table query
        return_update_query = "update %s set Status='Site is not registered' ,lockedby=null ,Hostname='%s' " \
                              "where  No=%s " % (selected_list, socket.gethostname(), todo_result[to_do_line][0])
        db_update(return_update_query)

    elif search_special:  # Find Site Available For Special Register
        print(str(todo_result[to_do_line][0]) + " : Special registration--> ", look_for, end='\r')
        # update Query
        return_update_query = "update %s set Status='Special registration',lockedby=null ,Hostname='%s' " \
                              "where  No=%s " % (selected_list,socket.gethostname(), todo_result[to_do_line][0])
        db_update(return_update_query)

    else:  # Try retrieve data from registered site
        email = search(r'(e-mail:\W+\w+\W+)t(\S+@\S+)\\n', telnet_result)
        search_phone = search(r'(phone:\W+\w+\W+)t(.*?)\\n', telnet_result)
        person = search(r'(person:\W+\w+\W+)t(.*?)\\n', telnet_result)
        if person is None:
            person_name = ''
        else:
            person_name = (person.group(2))
        if search_phone is None:
            phone_number = ''
        else:
            phone_number = (search_phone.group(2))
        if email:
            # update Query
            print(str(todo_result[to_do_line][0]), ': Site registered -->', looking_for, 'Email:',
                  email.group(2),
                  person_name + ' ' + phone_number, end='\r')
            return_update_query = "update %s set Status='Site registered',Email='%s'" \
                                  ",phone='%s',person='%s',lockedby=null ,Hostname='%s' where  No=%s " % \
                                  (selected_list, email.group(2), phone_number,
                                   person_name,socket.gethostname(), todo_result[to_do_line][0])
            db_update(return_update_query)

        else:
            if search_unregable:
                # update Query
                print(str(todo_result[to_do_line][0]), ': Unregistrable-->', look_for, end='\r')
                return_update_query = "update %s set Status='Unregistrable',lockedby=null ,Hostname='%s' " \
                                      "where  No=%s " % (selected_list,socket.gethostname(), todo_result[to_do_line][0])
                db_update(return_update_query)
            else:
                # update Query
                print(str(todo_result[to_do_line][0]), ': Site registered No Email-->', look_for, 'Email:',
                      'Cannot retrieve email address!', end='\r')
                return_update_query = "update %s set Status='Registered No Email',lockedby=null ,Hostname='%s' " \
                                      "where  No=%s " % (selected_list, socket.gethostname(), todo_result[to_do_line][0])
                db_update(return_update_query)


def block_out(ip_address):
    print('Block out counter archived!')
    winsound.Beep(1000, 4000)
    ip_research_counter = 1
    if internet_status() is True:
        print('Blocked IP:' + str(ip_address).strip())
        refresh_ip = None
        while (refresh_ip == ip_address) or refresh_ip is None:
            print('Program will be wait until you to renew internet ip for:'
                  + str(config_section_map("general")['ip_refresh_second'])
                  + ' second {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            sleep(int(config_section_map("general")['ip_refresh_second']))
            refresh_ip = public_ip()
            print('Refreshed IP:' + str(refresh_ip))

    else:
        while internet_status() is False:
            print('Connection is lost!,Check your internet connection! Try:', ip_research_counter,
                  ' second {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            sleep(int(config_section_map("general")['ip_refresh_second']))
            ip_research_counter += 1


def main():
    # List available table
    conn_id = None
    global conn

    internet_try_counter = 1
    while internet_status() is not True:
        print('Connection is lost!,Check your internet connection! Refresh interval:',
              int(config_section_map("general")['ip_refresh_second']), 'second,Try:', internet_try_counter)
        sleep(int(config_section_map("general")['ip_refresh_second']))
        internet_try_counter += 1
    ip_address = public_ip()
    print(str(ip_address))

    while conn_id is None:
        try:
            db_config = read_db_config()
            conn = MySQLConnection(**db_config)
            conn_id = conn.connection_id
        except Exception:
            conn_id = None
            print('Try connecting to database...')

    table_list = "select table_name,table_rows from information_schema.tables " \
                 "where table_name like 'lst_%' and table_rows>0;"
    table_list_exec = db_select(table_list)
    table_list_result = {}
    for line in range(0, len(table_list_exec)):

        table_records_status_query = "select count(site) from %s where status='Passed' or status is null " \
                                     "or status='Registered No Email'" % (table_list_exec[line][0])
        table_records_status_result = db_select(table_records_status_query)
        table_list_result.setdefault(table_list_exec[line][0], []).append(table_records_status_result[0][0])
        table_list_result.setdefault(table_list_exec[line][0], []).append(table_list_exec[line][1])
    if config_section_map("general")['default_list_name']:
        selected_list = str(config_section_map("general")['default_list_name'])
        print('Searching ' + selected_list + ' list...')
        if selected_list in table_list_result.keys():
            print('Processable,Total Record:' + str(table_list_result[selected_list]))
    else:
        print('Please Choice your dictionary list from below list')
        print(tabulate(zip(table_list_result.keys(), table_list_result.values(), ),
                       headers=['List Name', 'Processable/Record Count'],
                       tablefmt="grid"))
        selected_list = input('List Name:').lower()
    if selected_list in table_list_result.keys():
        delay = float(config_section_map("search")['delay_second'])
        whois = "whois.nic.ir"
        port = 43
        try_count = config_section_map("search")['try_count']
        loop_counter = 1
        process_counter = 0
        passed_counter = 0
        while loop_counter > 0:
            # lock record for process
            if process_counter > 0 and (process_counter / int(config_section_map("search")['mid_sleep_record'])) - (
                    math.floor(process_counter / int(config_section_map("search")['mid_sleep_record']))) == 0:
                print('Sleep mode:' + str(
                    config_section_map("search")['mid_sleep_time']) + ' second {:%Y-%m-%d %H:%M:%S}'.format(
                    datetime.datetime.now()))
                sleep(int(config_section_map("search")['mid_sleep_time']))

            process_counter += 1
            lock_record_query = "update %s set lockedby=connection_id(),lockedat=now()," \
                                "trycount=trycount+1,Hostname='%s' " \
                                "where lockedby is null and (status='Passed' or status is null " \
                                "or status='Registered No Email' ) and trycount<%s order by trycount limit %s" \
                                %(selected_list,socket.gethostname(),
                                  try_count, int(config_section_map("search")['buffer']))
            loop_counter, connection_d = db_update(lock_record_query)

            if loop_counter:
                todo_query = "select no,site from %s where  lockedby=%s and trycount<=%s " % (
                    selected_list, connection_d, try_count)
                todo_result = db_select(todo_query)
                if todo_result:
                    for to_do_line in range(0, len(todo_result)):
                        try:
                            sleep(delay)
                            look_for = todo_result[to_do_line][1]
                            looking_for = (str(look_for.strip()))
                            telnet_connect = Telnet(whois, port,
                                                    timeout=int(config_section_map("telnet")['telnet_timeout']))
                            telnet_connect.write(looking_for.encode("ascii") + b"\r\n")
                            telnet_result = str(telnet_connect.read_all())

                            if telnet_result == "b''":
                                print(str(todo_result[to_do_line][0]) + ' : Passed --> ' + looking_for, end='\r')
                                return_update_query = "update %s set Status='Passed',lockedby=null ,Hostname='%s' " \
                                                      "where  No=%s " \
                                                      % (selected_list,socket.gethostname(), todo_result[to_do_line][0])
                                db_update(return_update_query)

                            else:
                                telnet_parser(telnet_result, todo_result, to_do_line, look_for, selected_list,
                                              looking_for)
                                passed_counter = 0

                        except Exception:
                            passed_counter += 1
                            print('Telnet exception Passed -->', str(look_for), 'Count', passed_counter, end='\r')
                            winsound.Beep(9000, 300)
                            return_update_query = "update %s set Status='Passed',lockedby=null ,Hostname='%s' " \
                                                  "where  No=%s " \
                                                  % (selected_list,socket.gethostname(), todo_result[to_do_line][0])
                            db_update(return_update_query)
                            if passed_counter >= int(config_section_map("search")['block_counter_out']):
                                ip_address = public_ip()
                                mail_sender(socket.gethostname(), 'Blocked')
                                block_out(ip_address)
        else:
            print('All record are processed for ' + selected_list + ' list!')
    else:
        print('List does not exist!Bye!')
        sys.exit(0)


if __name__ == '__main__':
    main()
