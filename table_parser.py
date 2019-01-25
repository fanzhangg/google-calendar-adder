import requests
from bs4 import BeautifulSoup
import bs4
from typing import List
from typing import Dict


class TableParser(object):
    """
    Parse the event information in the target table
    """
    def __init__(self, url: str, table_head: str):
        self.url = url
        self.table_head = table_head

    def get_web_page(self) -> str:
        """
        Download the content of the target web page
        :return: the content of the target web page
        """
        headers = {
            'User-Agent' :
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181\
                Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == requests.codes.ok:
            print(f"Request {self.url}. Done.")
            return response.text
        else:
            raise requests.RequestException(f"Request {url}. Failed")

    def get_table(self)->bs4.Tag:
        """
        Get the Tag object of the target table
        :return: the Tag object of the target table
        """
        markup = self.get_web_page()
        soup = BeautifulSoup(markup, features='html5lib')
        # TODO: change this code if the web page has a different format
        head = soup.find(text=self.table_head)
        print('head:', head)
        # According to the source code, the table element is right after the head
        table = head.findNext('table')
        print('Retrieve table. Done')
        return table

    def extract_table(self)->List[Dict[str, str]]:
        """
        Extract information from the form
        :return: the text of the table
        """
        events = []
        table = self.get_table()
        # table.children returns a list_iterator
        # tb is the children of children of table element
        tbodys = table.children
        for table_rows in tbodys:
            try:
                for table_row in table_rows:
                    datas = [data for data in table_row]
                    if len(datas) > 1:
                        events.append({'summary': datas[5].string,
                                       'date': datas[1].string})
            except AttributeError:
                pass
        return events


if __name__ == "__main__":
    parser = TableParser('https://www.macalester.edu/registrar/academiccalendars/#a20182019', 'Spring 2019')
    events = parser.extract_table()
    print(events)

