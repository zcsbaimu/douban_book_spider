import urllib.parse
import numpy
import requests
import re
import time
from lxml import etree
import pymysql

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
url = ""


class DouBan():
    def __init__(self):
        self.header = header
        self.cookie = {'bid': '4IL9zUuRbao', ' ct': 'y',
                       ' _vwo_uuid_v2': 'DEB5CD2B472BA09CCAED99EE858F0995B|5c6aac251d475d9a92a3df8bbc80eef8',
                       ' ll': '"118277"', ' viewed': '"36206462_36197707_36361935_36412372"', ' ap_v': '0,6.0',
                       ' dbcl2': '"271125516:euhW9X7FNfw"', ' ck': 'vBPl', ' push_noty_num': '0',
                       ' push_doumail_num': '0',
                       ' _pk_id.100001.3ac3': 'b94259c767694130.1685777411..1685792818.undefined.',
                       ' _pk_ses.100001.3ac3': '*'}

    def get_tag(self):
        url = 'https://book.douban.com/tag/?&'
        params = {'view': 'type',
                  'icn': 'index-sorttags-all'}
        response = requests.get(url=url, headers=header, params=params, cookies=self.cookie)
        tag_find = re.compile('<td><a href="(.*?)">(.*?)</a><b>(.*?)</b></td>')
        tag = re.findall(tag_find, response.text)
        # print(tag)
        return tag

    def tag_deal(self, tag):
        return_list = []
        page = 0
        while page < 1:
            url = f'https://book.douban.com/tag/{urllib.parse.quote(tag[1])}?start={page * 20}&type=T'
            time.sleep(numpy.random.rand() * 5)
            try:
                response = requests.get(url=url, headers=self.header, cookies=self.cookie)
            except Exception as e:
                print(e)
                continue
            tree = etree.HTML(response.text)
            li_list = tree.xpath('//*[@id="subject_list"]/ul/li')
            for li in li_list:
                try:
                    data_list = []
                    title = li.xpath('div[2]/h2/a/@title')
                    desc = ''.join(li.xpath('div[2]/div/text()')).replace(' ', '').replace('\n', '').split('/')
                    rating = li.xpath('div[2]/div[2]/span[2]/text()')
                    people_num = [''.join(li.xpath('div[2]/div[2]/span[3]/text()')).replace('\n', '').replace(' ', '')]
                    url = li.xpath('div[1]/a/img/@src')
                    content = li.xpath('div[2]/p/text()')
                    data_list.append(title[0])
                    data_list.append(desc[0])
                    data_list.append(desc[1])
                    data_list.append(desc[2])
                    data_list.append(desc[3])
                    try:
                        data_list.append(rating[0])
                    except:
                        data_list.append(str(0))
                    data_list.append(people_num[0])
                    data_list.append(url[0])
                    data_list.append(content[0])
                    return_list.append(data_list)
                except Exception as e:
                    print(e)
                    continue
            page += 1
        return return_list

    def create_mysql(self):
        self.db = pymysql.connect(host="localhost", user='root', password='linghua', database='douban',
                                  charset='utf8mb4')
        self.cursor = self.db.cursor()

    def mysql_data_add(self, data_list, table):
        try:
            self.cursor.execute(f"drop table if exists {table}")
            sql = f"""create table {table}(
        id integer  not null primary key AUTO_INCREMENT,
        title char(50),
        author varchar(200),
        publish_house char(50),
        datatime char(50),
        price char(20),
        rateing char(20),
        people_num char(20),
        url_data char(120),
        desc_text varchar(400)
        )DEFAULT CHARSET=utf8;
        """

            self.cursor.execute(sql)
            print(f"create {table} successful")
            sql2 = f'ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4'
            self.cursor.execute(sql2)
            for data in data_list:
                # print(data)
                sql1 = f"insert into {table}(title,author,publish_house,datatime,price,rateing,people_num,url_data,desc_text) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s' )" % \
                       (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8])
                self.cursor.execute(sql1)
            self.db.commit()
            print(f'{table} save douban database')

        except Exception as e:

                print(e)


if __name__ == "__main__":
    test = DouBan()
    tag = test.get_tag()
    test.create_mysql()
    tag2 = [('/tag/小说', '几米', '(7465934)')]
    for i in tag:
        data_list = test.tag_deal(i)
        test.mysql_data_add(data_list, i[1])
    test.db.close()
