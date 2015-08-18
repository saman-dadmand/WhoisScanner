__author__ = 'Saman'

from bs4 import BeautifulSoup
import urllib
from urllib import request
from colorama import init
from re import search
from colorama import Fore
from config import config_section_map

init()


def reverse_dns(target):
    # First Page Parsing and Getting count of total result
    result = {}
    print('\n' + Fore.BLACK + 'Try DNS Reverse for:' + target, end='\r')
    link = "http://www.bing.com/search?q=ip%3a" + target + "&count=0&filt=custom&first=1&FORM=PERE"
    try:
        print(Fore.CYAN + 'Try DNS Reverse for:' + target + ' Page 1', end='\r')
        sock = urllib.request.urlopen(link)
        htmlsource = sock.read()
        soup = BeautifulSoup(htmlsource, 'html5lib')
        result_count = search(r'("sb_count">)(\S+) results', str(soup.find(id="b_tween")))
        records = 0
        if result_count:
            records = int(str(result_count.group(2)).replace(',', ''))

        for link in soup.find_all('a'):
            pre_result = str(link.get('href'))
            if pre_result[:4] == 'http' and pre_result[:9] != 'http://go':
                result.setdefault(pre_result, []).append(pre_result)

        # Detect other pages and parse it
        if records >= 10:
            page_number = 1
            x = 0
            y = 1
            while x != y:
                if page_number >= int(config_section_map("dns_reverser")['pages_to_process']):
                    break

                link = "http://www.bing.com/search?q=ip%3a" + target + "&count=0&filt=custom&first=" + \
                       str(page_number) + "1&FORM=PERE"
                try:
                    print(Fore.CYAN + 'Try DNS Reverse for:' + target + ' Page ' + str(page_number + 1), end='\r')
                    sock = urllib.request.urlopen(link)
                    htmlsource = sock.read()
                    soup = BeautifulSoup(htmlsource, 'html5lib')
                    result_count = search(r'("sb_count">)(\w+)-(\w+) of (\S+) results', str(soup.find(id="b_tween")))
                    if result_count:
                        x = int(str(result_count.group(3)).replace(',', ''))
                        y = int(str(result_count.group(4)).replace(',', ''))
                    else:
                        x = 0
                        y = 0

                    for link in soup.find_all('a'):
                        pre_result = str(link.get('href'))
                        if pre_result[:4] == 'http' and pre_result[:9] != 'http://go':
                            result.setdefault(pre_result, []).append(pre_result)
                    page_number += 1
                except Exception:
                    print('Other page exception')
        sock.close()
    except Exception:
        print('First Page exception')

    return result
