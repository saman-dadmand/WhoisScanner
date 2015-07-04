def main():
    from mysql.connector import MySQLConnection, Error
    from tabulate import tabulate
    from config import read_db_config
    import sys
    import os
    # List available table

    table_list = "select table_name,table_rows from information_schema.tables " \
                 "where table_name like 'lst_%' and table_rows>0;"
    db_config = read_db_config()
    conn = MySQLConnection(**db_config)
    cursor_table_list = conn.cursor()
    cursor_table_list.execute(table_list)
    table_list_exec = (cursor_table_list.fetchall())
    table_list_result = {}
    for line in range(0, len(table_list_exec)):
        cursor_table_detail = conn.cursor()
        table_records_status_query = "select count(site),(select case when count(site)=0 then 'Completed'" \
                                     " else 'Not Completed' end from %s where status='Passed' or status is null ) " \
                                     "as Status  from %s where email!='' " \
                                     % (table_list_exec[line][0],table_list_exec[line][0])
        cursor_table_detail.execute(table_records_status_query)
        table_records_status_result = cursor_table_detail.fetchall()
        table_list_result.setdefault(table_list_exec[line][0], []).append(table_records_status_result[0][0])
        table_list_result.setdefault(table_list_exec[line][0], []).append(table_list_exec[line][1])
        table_list_result.setdefault(table_list_exec[line][0], []).append(table_records_status_result[0][1])
    print('Please Choice your dictionary list from below list')
    print(tabulate(zip(table_list_result.keys(), table_list_result.values(), ),
                   headers=['List Name', 'Email Count/Record Count/Status'],
                   tablefmt="grid"))
    selected_list = input('List Name:').lower()
    if selected_list in table_list_result.keys():
        export_list_type = input('0 for all records,1 for records with email\n')
        start_record = int(input('Export start from record No:(0 for beginning)\n'))
        result_filename = selected_list + '_result.txt'
        if os.path.isfile(result_filename):
            overwrite_ask = input('The result file is exist! do you want to overwrite it?(y/n):')
            if overwrite_ask.lower() == 'y':
                try:
                    os.remove(result_filename)
                except OSError:
                    print('Error:' + OSError.winerror)
            else:
                sys.exit(0)
            result_file = open(result_filename,"w")
            result_file.write('No|Site|Status|Email|Person|Phone\n')
            result_file.close()
        if export_list_type == '1': #Just Data with Email
            export_list_query = "select No,Site,ifnull(Status,'') as Status,ifnull(Email,'') as Email," \
                                "ifnull(Person,'') as Person,ifnull(Phone,'') as Phone from %s " \
                                "where email!='' and email is not null and status='Site registered' " \
                                "and no>%s order by No " % (selected_list,start_record)
        else:
            export_list_query = "select No,Site,ifnull(Status,'') as Status,ifnull(Email,'') as Email," \
                                "ifnull(Person,'') as Person,ifnull(Phone,'') as Phone from %s " \
                                "where no>%s order by No;" % (selected_list,start_record)
        export_list_curssor = conn.cursor()
        export_list_curssor.execute(export_list_query)
        export_result=export_list_curssor.fetchall()
        for line in range(0, len(export_result)):
            with open(result_filename, "a") as fw:
                fw.write('{0}|{1}|{2}|{3}|{4}|{5}\n'.format(str(export_result[line][0]), str(export_result[line][1]),
                                                        str(export_result[line][2]), str(export_result[line][3]),
                                                        str(export_result[line][4]),str(export_result[line][5])))
                print(str(line+1),'/',str(export_list_curssor.rowcount),'Processed',end='\r')
        conn.close

    else:
        print('Wrong List Name')


if __name__ == '__main__':
    main()
