# -*- coding: utf-8 -*-
# !/usr/bin/evn python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import requests
import time
import pdfkit
import re
from bs4 import BeautifulSoup


# 本脚本目前只适用于保存微信公众号文章
# 本脚本可以对多篇的公众号文章进行保存，需要将你保存的公众号文章链接写入urls4.txt中，注意一行只写一条链接
# 链接后面不要添加空格

# wkhtmltopdf所在的位置
wkhtmltopdf_path = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
# chromedriver所在的位置
chromedriver = os.getcwd() + '\\chromedriver.exe'
# Article文件夹的路径
article_total_path = os.getcwd() + '\\Article\\'


# 获取进行保存操作的日期
def get_save_date():
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return date


# 命名文件夹,如果文件夹不存在则创建文件夹
def name_folder(article_folder_path):
    try:
        if not os.path.exists(article_folder_path):
            os.makedirs(article_folder_path)
    except Exception as e:
        print('抱歉，命名文件夹出错，请联系管理员', '异常为', e)


# 在当前目录创建Article文件夹
name_folder(article_total_path)


# 获取公众号文章的标题和作者
def get_title_author(url):
    try:
        response = requests.get(url)
        spe_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find(attrs={'property': 'twitter:title'}) is None:
            if soup.find(attrs={'property': 'og:title'}):
                title = soup.find(attrs={'property': 'og:title'})['content']
            elif soup.title:
                title = soup.title.string
            else:
                title = '无'
        else:
            title = soup.find(attrs={'property': 'twitter:title'})['content']
        title = re.sub(spe_str, "_", title)  # 替换特殊字符
        title_format = '「' + title+'」'  # 格式处理
        if soup.find(id='js_author_name') is None:
            if soup.find(id='js_name'):
                author_name = soup.find(id='js_name').string.strip()
            else:
                timeStr = str(time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time())))
                author_name = title + timeStr
        else:
            author_name = soup.find(id='js_author_name').string
        author_name = re.sub(spe_str, "_", author_name)  # 替换特殊字符
        author_name_format = '作者' + author_name
        article_folder_path = os.path.join(os.path.join(article_total_path, author_name, title))
        article_msg = [title, title_format, author_name, author_name_format, article_folder_path]
        return article_msg
    except Exception as e:
        print('抱歉，获取标题和作者出错，请联系管理员', '异常为', e)


# 命名图片 html 以及 pdf
def name_pic_html_pdf(url, article_msg):
    try:
        date = get_save_date()
        PIC_NAME = article_msg[1] + 'by' + article_msg[3] + '于' + date+'.png'
        HTML_NAME = article_msg[1] + 'by' + article_msg[3] + '于' + date+'.html'
        PDF_NAME = article_msg[1] + 'by' + article_msg[3] + '于' + date+'.pdf'
        name_msg = [PIC_NAME, HTML_NAME, PDF_NAME]
        return name_msg
    except Exception as e:
        print('抱歉，命名文件出错，请联系管理员', '异常为', e)


# 根据页面进行截图
def save_pic(url, pic_name, article_folder_path):
    try:
        os.environ['webdriver.chrome.driver'] = chromedriver
        # 设置chrome开启的模式，headless就是无界面模式，只有开启这个模式才能截取全屏
        chrome_options = Options()
        chrome_options.add_argument('headless')
        # 屏蔽chromedriver运行日志
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
        # 接下来是全屏的关键，用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
        # 控制浏览器写入并转到链接
        driver.get(url)
        # 创建一个列表，用于记录每一次拖动滚动条后页面的最大高度
        all_window_height = []
        # 当前页面的最大高度加入列表
        all_window_height.append(driver.execute_script('return document.body.scrollHeight;')) 
        while True:
            # 执行拖动滚动条操作
            driver.execute_script('scroll(0,100000)')
            time.sleep(3)
            check_height = driver.execute_script('return document.body.scrollHeight;')
            # 判断拖动滚动条后的最大高度与上一次的最大高度的大小，相等表明到了最底部
            if check_height == all_window_height[-1]:
                break
            else:
                # 如果不相等，将当前页面最大高度加入列
                all_window_height.append(check_height)
        width = driver.execute_script('return document.documentElement.scrollWidth')
        height = driver.execute_script('return document.documentElement.scrollHeight')
        # 将浏览器的宽高设置成刚刚获取的宽高
        driver.set_window_size(width, height)
        time.sleep(2)
        pic_path = os.path.join(os.path.join(article_folder_path, pic_name))
        print('开始截图')
        time_start = time.time()
        if driver.save_screenshot(pic_path):
            time_end = time.time()
            time_con = time_end - time_start
            time_con = round(time_con, 1)
            print('完成截图')
            return time_con
        else:
            print('抱歉，截图失败，请联系管理员')
    except Exception as e:
        print('抱歉，保存图片出错，请联系管理员', '异常为', e)
    finally:
        driver.close()


# 将公众号文章url的网页内容保存为html
def turn_url_to_html(url, html_name, article_folder_path):
    try:
        html_path = os.path.join(os.path.join(article_folder_path, html_name))
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html5lib')
        # 将拥有'data-src'属性的图片标签的'data-src'改为'src'，解决JS懒加载的问题
        for img in soup.find_all('img', {'data-src': True}):
            img['src'] = img['data-src']
            del img['data-src']
        html = bytes(str(soup.html), encoding="utf-8")
        print('开始保存html')
        time_start = time.time()
        with open(html_path, 'wb') as f:
            f.write(html)
            time_end = time.time()
            time_con = time_end - time_start
            time_con = round(time_con, 1)
            print('完成html保存')
            return time_con
    except Exception as e:
        print('抱歉，保存html出错，请联系管理员', '异常为', e)
    finally:
        f.close()


# 将turn_url_to_html()函数中保存的html转换为PDF
def turn_html_to_pdf(url, html_name, pdf_name, article_folder_path):
    try:
        # PDF的格式参数
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'no-outline': None
            }
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        html_path = os.path.join(os.path.join(article_folder_path, html_name))
        pdf_path = os.path.join(os.path.join(article_folder_path, pdf_name))
        print('开始转换为PDF')
        time_start = time.time()
        pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
    except IOError:
        time_end = time.time()
        print('完成PDF转换')
        time_con = time_end - time_start
        time_con = round(time_con, 1)
        return time_con
    except Exception as e:
        print('抱歉，保存pdf出错，请联系管理员', '异常为', e)


# 遍历urls列表同时然后保存为png html及pdf
def save_pic_html_pdf_by_urls():
    try:
        urls = []
        with open('urls4.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                url = line.strip('\n')
                urls.append(url)
        for url in urls:
            try:
                print('开始保存', url, '的内容')
                # 调用get_title_author函数
                article_msg = get_title_author(url)
                # 调用name_pic_html_pdf()函数
                name_msg = name_pic_html_pdf(url, article_msg)
                # 调用name_folder函数
                name_folder(article_msg[4])
                start_str = '开始对文章' + article_msg[1] + '进行保存操作(保存为png、html以及pdf)：'
                complete_str = '已完成对文章' + article_msg[1] + '的保存操作。文章的截图、HTML及PDF保存在文件夹 ' + article_msg[4]
                print(start_str)
                time_start = time.time()
                pic_time_con = save_pic(url, name_msg[0], article_msg[4])
                html_time_con = turn_url_to_html(url, name_msg[1], article_msg[4])
                pdf_time_con = turn_html_to_pdf(url, name_msg[1], name_msg[2], article_msg[4])
                time_end = time.time()
                simple_time = round(time_end-time_start, 1)
                print(complete_str)
                print('其中，截图时间为:', pic_time_con, '秒,保存为html的时间为:', html_time_con, '秒,转换为PDF的时间为:',  pdf_time_con, '秒,单篇总耗时为:', simple_time, '秒')
            except Exception as e:
                print('抱歉，程序出错，请联系管理员', '异常为', e)
                continue
    except Exception as e:
        print('抱歉，程序出错，请联系管理员', '异常为', e)
    finally:
        f.close()


if __name__ == '__main__':
    time.sleep(2)
    time_start_all = time.time()
    save_pic_html_pdf_by_urls()
    time_end_all = time.time()
    total_time = round(time_end_all-time_start_all, 1)
    print('本次保存所有文章的总耗时为', total_time, '秒')
    time.sleep(2)
