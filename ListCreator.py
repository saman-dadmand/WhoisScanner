__author__ = 'Saman Dadmand'
import sys

from mysql.connector import MySQLConnection, Error
from itertools import product
from string import ascii_lowercase
from config import read_db_config


def exist_list(tbl_name_val):
    table_list = "select table_name,table_rows from information_schema.tables where table_name='%s' ;" % tbl_name_val
    args = tbl_name_val
    try:

        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(table_list)
        res1 = cursor.fetchall()
        for row_count in res1:
            return row_count[1]
    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()


def create_table(tbl_name_val):
    query = "CREATE TABLE IF NOT EXISTS %s ( " \
            "No int NOT NULL auto_increment," \
            "Site varchar(100)," \
            "Status varchar(30)," \
            "Email varchar(100)," \
            "Person varchar(100)," \
            "Phone varchar(25)," \
            "lockedby bigint,  " \
            "lockedat datetime," \
            "Trycount int default 0 , " \
            "Hostname varchar(50)," \
            "PRIMARY KEY (No)" \
            ") ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;" % tbl_name_val
    args = tbl_name_val

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query)
        print('New Table Created:' + str(tbl_name_val))

    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()


def drop_table(tbl_name_val):
    drop_item = "drop table %s" % tbl_name_val
    args = tbl_name_val
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(drop_item)
        print(str(tbl_name_val) + ' Table Droped!')

    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()


def main():
    print('Put txt file in the same folder of exe!')
    table_name = 'lst_' + (input('Please name your list (lst_ will be add as prefix automatically):').lower())
    if table_name == 'lst_':
        sys.exit(0)
    exist_control = exist_list(table_name)
    if exist_control is None:
        create_table(table_name)
    elif exist_control == 0:
        drop_table(table_name)
        create_table(table_name)
    else:
        print('The named table is exist and contain ' + str(exist_control) + ' Records')
        ask = input('Do you want to drop ' + str(exist_control) + ' table? (yes/no)')
        if ask.lower() == 'yes':
            drop_table(table_name)
            create_table(table_name)

        else:
            print('Exit without any change!')
            sys.exit(0)

    extension = str(input('Please Enter Your Extension(ir,co.ir ,...):'))
    list_method=input('Choice your Method( 1:Auto Letter Generator 2:Import Text File ) :')
    if list_method == '1':
        letter_number = int(input('Number of Letters:'))
        keywords = [''.join(i) for i in product(ascii_lowercase, repeat=letter_number)]
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        for line in range(0, len(keywords)):
            cursor = conn.cursor()
            Query = "insert into %s (site) values (concat('%s','.','%s'));" \
                    % (table_name, '{0}'.format(str(keywords[line])),extension)
            cursor.execute(Query)
            print(str(line+1),end='\r')
        print(str(line+1),'Records Imported!')
    elif list_method == '2':
        dic_filename_mask = str(input('Whats the Text Dictionary Filename {without extension}:'))
        filename = dic_filename_mask + '.txt'
        dic_list = open(filename)
        print('Total Count of Records: ' + str(sum(1 for _ in dic_list)))
        dic_list.close()
        # dic_list = open(filename)
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        load_text_file_query = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s  LINES TERMINATED BY '\\r\\n' (SITE);" \
                               % (filename, table_name)
        print('Transferring List...')
        cursor.execute(load_text_file_query)
        print('Add Extension to list...')
        update_extension_query = "update %s set site=concat(site,'.','%s')" % (table_name, extension)
        cursor.execute(update_extension_query)
        conn.commit()
        cursor.close()
        conn.close()
    else:
        print('Wrong Choice,Bye!')

    print("Finish")

if __name__ == '__main__':
    main()
