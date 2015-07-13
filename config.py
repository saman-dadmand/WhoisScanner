from configparser import ConfigParser
import urllib
import urllib.request
from re import findall
from smtplib import SMTP
import datetime

Config = ConfigParser()
Config.read("config.ini")
Config.sections()


def config_section_map(section):
    parser = {}
    options = Config.options(section)
    for option in options:
        try:
            parser[option] = Config.get(section, option)
            if parser[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            parser[option] = None
    return parser


def read_db_config(filename='config.ini', section='mysql'):
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def public_ip():
    ip = {}
    try:
        print('Checking Public IP Address...')
        with urllib.request.urlopen(config_section_map("general")['public_ip_ref']) as ext_ip:
            ip = findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',
                         str(ext_ip.read()))
    except Exception:
        ip = None

    return ip


def internet_status():
    try:
        print('Checking internet connection...')
        response = urllib.request.urlopen('https://www.google.com')
        print('Connected')
        return True
    except Exception:
        return False

def mail_sender(hostname, event):
    try:
        debuglevel = 0
        smtp = SMTP()
        smtp.set_debuglevel(debuglevel)
        smtp.connect(config_section_map("email")['server'], config_section_map("email")['port'])
        smtp.login(config_section_map("email")['user'], config_section_map("email")['password'])

        from_addr = config_section_map("email")['sender']
        to_addr = config_section_map("email")['notify']

        subj = "Whois Scanner Blocked!"
        date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

        message_text = "Hello\nMessage from [%s] hostname: The %s event occurred at %s \n\nBye\n" % (hostname,event, date)

        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (from_addr, to_addr, subj, date, message_text)

        smtp.sendmail(from_addr, to_addr, msg)
        smtp.quit()
    except Exception:
        print('Cannot Send Email!')
