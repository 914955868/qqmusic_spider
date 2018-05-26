__author__ = 'li'
__date__ = '2018/5/7 14:08'
from bs4 import BeautifulSoup
import requests
import re
import pymysql

#获取每个字母对应的最大页数
def letter_pagenumber():
    letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ9"
    dit = dict.fromkeys(letter)
    for i in letter:
        url = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&key=all_all_' + i + '&pagesize=100&pagenum=1&g_tk=5381&jsonpCallback=GetSingerListCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
        page = requests.get(url)
        page_number = int(re.findall('\"total_page\":\d*', page.text)[0].replace('\"total_page\":', ''))
        dit[i] = page_number
    return dit


# 以列表形式返回指定字母、起止页数所有歌手id
def letter_singerurl(letter, pagestart, pageend):
    assert 0 <= pageend <= letter_pagenumber()[letter], '页码超出上限'
    singer_urls = []
    for i in range(pagestart, pageend):
        url = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&key=all_all_' + letter + '&pagesize=100&pagenum=' + str(
            i + 1) + '&g_tk=5381&jsonpCallback=GetSingerListCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
        page = requests.get(url)
        for j in re.findall('\"Fsinger_mid\":".*?"', page.text):
            singer_url = j.split('"')[3]
            singer_urls.append(singer_url)
    return singer_urls


class Singer:
    songlist = []
    mvlist = []
    albumlist = []
    #入库方法
    def intertmysql(self):
        conn = pymysql.connect(host="localhost", user="root", password="li123456789", db="qqMusic",
                               charset="utf8")  # 链接数据库
        cursor = conn.cursor()
        singerinsert = "insert into singer(id,url,info,sname,fan,songnum,songurl,albnum,albnumurl,mvnum,mvurl)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        reCount = cursor.execute(singerinsert, (
        self.id, self.url, self.info, self.name, self.fan, self.songnum, self.songurl, self.albnum, self.albnumurl,
        self.mvnum, self.mvurl))
        conn.commit()
        cursor.close()
        conn.close()
    #构造方法
    def __init__(self, id):
        self.id = id  # 歌手id
        self.url = 'https://y.qq.com/n/yqq/singer/' + id + '.html'  # 歌手主页网址
        infourl = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_singer_desc.fcg?singermid=' + id + '&utf8=1&outCharset=utf-8&format=xml'  # 歌手信息请求网址
        self.info = requests.get(infourl,
                                 headers={'Referer': 'https://c.y.qq.com/xhr_proxy_utf8.html'}).text  # 获取歌手信息xml
        homepage = requests.get(self.url)  # 获取歌手主页html
        soup = BeautifulSoup(homepage.text, 'html.parser')  # bs4解析
        self.name = soup.find('h1', attrs={'class': 'data__name_txt js_index'}).text
        fanurl = 'https://c.y.qq.com/rsc/fcgi-bin/fcg_order_singer_getnum.fcg?singermid=' + id
        fanrefer = 'https://y.qq.com/n/yqq/singer/' + id + '.html'
        fanhtml = requests.get(fanurl, headers={'Referer': fanrefer})
        self.fan = int(re.findall('\"num\":\d*', fanhtml.text)[0].replace('\"num\":', ''))
        if soup.find('a', attrs={'data-stat': 'y_new.singer.header.song_tab'}):
            self.songnum = int(
                soup.find('a', attrs={'data-stat': 'y_new.singer.header.song_tab'}).findChild('strong').text)  # 单曲数
            self.songurl = 'https://y.qq.com/n/yqq/singer/' + id + '.html#tab=song&'
        else:
            self.songnum = 0  # 单曲数
            self.songurl = " "  
        if soup.find('a', attrs={'data-stat': 'y_new.singer.header.album_tab'}):
            self.albnum = int(
                soup.find('a', attrs={'data-stat': 'y_new.singer.header.album_tab'}).findChild('strong').text)  # 专辑数
            self.albnumurl = 'https://y.qq.com/n/yqq/singer/' + id + '.html#tab=album&'
        else:
            self.albnum = 0  # 专辑数
            self.albnumurl = " "
        if soup.find('a', attrs={'data-stat': 'y_new.singer.header.mv_tab'}):
            self.mvnum = int(
                soup.find('a', attrs={'data-stat': 'y_new.singer.header.mv_tab'}).findChild('strong').text)  # mv数
            self.mvurl = 'https://y.qq.com/n/yqq/singer/' + id + '.html#tab=mv&'
        else:
            self.mvnum = 0
            self.mvurl = " "

    def set_id(self, id):
        self.id = id

    def set_info(self, url):
        self.url = url

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def show(self):
        print(self.id, self.url, self.name, self.fan, self.songnum, self.songurl, self.albnum, self.albnumurl,
              self.mvnum, self.mvurl)

    def get_info(self):
        return self.info

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def get_id(self):
        return self.id

    def get_fan(self):
        return self.fan


if __name__ == '__main__':
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ9"
    for i in letters:
        end = letter_pagenumber()[i]
        list = letter_singerurl(i, 0, end)
        for j in list:
            try:
                singer = Singer(j)
                singer.show()
                singer.intertmysql()
            except:
                continue
