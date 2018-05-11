#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built-in module
import io		# io
import os       # OS
import random   # Random
import re       # RegEx
import time     # Time
import datetime # datetime
import socket   # Socket
import ssl      # SSL
import json     # JSON
import csv      # CSV
import smtplib  # SMTP Library
from smtplib import SMTP_SSL
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

# 3rd-party module
import requests
import ruamel.yaml  
from bs4 import BeautifulSoup

def get_content(url , headers = None, certificate = None):
    # 设置一些请求头部默认字段
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    }
    # 加入自定义字段，若同名可覆盖默认字段的值
    for h in headers:
        custom_headers[h] = headers[h]

    random_timeout = random.randint(80, 180)
    while True:
        try:
            if certificate:
                resp = requests.get(url, headers = custom_headers, timeout = random_timeout, verify=certificate)
            else:
                resp = requests.get(url, headers = custom_headers, timeout = random_timeout)
            resp.encoding = 'utf-8'
            break
        except socket.timeout as e:
	        # 访问错误，输出运行时间信息
            print(time.strftime('%Y-%m-%d %H:%M:%S %A\n',time.localtime(time.time())))
            print( '3:', e)
            time.sleep(random.randint(8,15))

        except socket.error as e:
	        # 访问错误，输出运行时间信息
            print(time.strftime('%Y-%m-%d %H:%M:%S %A\n',time.localtime(time.time())))
            print( '4:', e)
            time.sleep(random.randint(20, 60))

        except http.client.BadStatusLine as e:
        # except http.client.HTTPException as e:
	        # 访问错误，输出运行时间信息
            print(time.strftime('%Y-%m-%d %H:%M:%S %A\n',time.localtime(time.time())))
            print( '5:', e)
            time.sleep(random.randint(30, 80))

        except http.client.IncompleteRead as e:
	        # 访问错误，输出运行时间信息
            print(time.strftime('%Y-%m-%d %H:%M:%S %A\n',time.localtime(time.time())))
            print( '6:', e)
            time.sleep(random.randint(5, 15))
    return resp.text

def get_notices(data, site, keywords = None):
    # 定义爬虫规则
    soup = BeautifulSoup(data,'lxml')
    # tt = soup.select('.main_shadow')
    titles = soup.select(".main_shadow > table > tr > td > a")
    dates = soup.select(".main_shadow > table > tr > td > div")
    temp_dates = []
    for d in dates:
        temp = d.get_text()
        temp_dates.append(temp)
    # # 后 14 条结果为所需
    # titles      =   titles[-14:]
    # temp_dates  =   temp_dates[-14:]

    notices = []
    i = 0
    for n in titles:
        temp = []
        
        # 获取标题，若存在关键词列表则判断
        title = n.get_text()
        if keywords and not any(s in title for s in keywords):
            i += 1
            continue

        # 获取链接，所需页面都以 list.html 结尾
        link = n.get("href")
        if re.search('list\.htm$', link):
            i += 1
            continue
        # 一条通知
        temp = [
            temp_dates[i],
            title,
            site + link
        ]
        i += 1
        notices.append(temp)
    return notices

def write_data(data, name):
    file_name = name
    with open(file_name, 'w', errors='ignore', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(data)

def read_data(filename):
    items = []
    with open(filename, 'r', errors='ignore', encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            items.append(r)
    return items
    
def email_format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
    
def cmp(a, b):
    return sorted(a) == sorted(b)

def send_mail(smtp_setting, msg_setting, msg_content, recipient):
    smtp_server         =   smtp_setting['server'] 
    smtp_sender         =   smtp_setting['email'] 
    smtp_password       =   smtp_setting['password'] 

    mail_subject    =   msg_setting['subject']
    mail_from_name  =   msg_setting['from']
    mail_from_addr  =   smtp_sender
    mail_to_name    =   recipient['name']
    mail_to_addr    =   recipient['addr']
    mail_content    =   msg_content
    
    message = MIMEText(mail_content, 'html', 'utf-8') 
    message['Subject'] = Header(mail_subject, 'utf-8').encode()
    message['From'] = email_format_addr('%s <%s>' % (mail_from_name, mail_from_addr)) 
    message['To'] =  email_format_addr('%s <%s>' % (mail_to_name, mail_to_addr))

    # 发送邮件前 输出运行时间信息
    print(time.strftime('\n%Y-%m-%d %H:%M:%S %A',time.localtime(time.time())))
    try:
        smtp = SMTP_SSL(smtp_server)
        # smtp.set_debuglevel(1) # 开启调试模式，1 开启，0关闭
        smtp.ehlo(smtp_server)
        smtp.login(smtp_sender, smtp_password)
        smtp.sendmail(mail_from_addr, mail_to_addr, message.as_string())
        smtp.quit()
	
        print("[ok]邮件发送成功", mail_to_name, mail_to_addr)
    except smtplib.SMTPException:
        print("[error]无法发送邮件", mail_to_name, mail_to_addr)

if __name__ == '__main__':  
    ## 读取配置文件
    current_path = os.path.split(os.path.realpath(__file__))[0] + '/'
    hqjt_yaml_file = current_path + "stu.yml"
    with io.open(hqjt_yaml_file, "r", encoding="utf-8") as docs:  
        try:  
            alldata = ruamel.yaml.round_trip_load(docs)
        except ruamel.yaml.YAMLError as exc:  
            print(exc)  
    # 抓取部分
    page            =   alldata['page']
    headers         =   alldata['headers']
    certificate     =   ( current_path + alldata['certificate'] ) if alldata['certificate'] else None
    keywords        =   alldata['keywords']
    localdata       =   current_path + alldata['localdata']
    # 处理部分
    site            =   alldata['site']
    # 送信部分
    recipients      =   alldata['subscribers']
    smtp_setting    =   alldata['smtp']
    msg_setting     =   alldata['mail']
    
    # 输出运行时间信息
    # print(time.strftime('%Y-%m-%d %H:%M:%S %A\n',time.localtime(time.time())))
    
    # print(recipients[0]['name'])
	
    ## 程序正式运行
    # get_content 仅获取网页 
    content = get_content(page, headers, certificate)
    # get_notices 获取通知列表，若 keywords 列表不为 None，则只输出包含关键词的通知
    current_notices = get_notices(content, site, keywords)

    # read_data 获取之前的通知
    local_data = read_data(localdata)

    # write_data 写入新数据，每次运行将现在访问结果覆盖写入到 stu.csv 中
    write_data(current_notices, localdata)

    # cmp 比对数据，只取新通知，并构造邮件内容
    new_notices = []
    msg_content = '助学服务有新的通知：'
    if False == cmp(local_data, current_notices):
        for n in current_notices:
            if n not in local_data:
                now = datetime.datetime.now()
                there_days_ago = now + datetime.timedelta(days=-3)
                current_date = datetime.datetime.strptime(n[0],"%Y-%m-%d")
                flag = (current_date - there_days_ago).days
                # log
                print('[log] n not in local_data')
                print(n)
                if flag <= 4 and flag >= -1:
                    print('[log] n 添加到发送信息列表')
                    print(n)
                    new_notices.append(n)
        if new_notices:
            for nn in new_notices:
                msg_content = msg_content + '<p>%s <a href="%s">%s</a></p>' % (nn[0], nn[2], nn[1])
    # 输出时间
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    if new_notices:
        recipient = {}
        for r in recipients:
            recipient['name'] = r['name']
            recipient['addr'] = r['addr']
            send_mail(smtp_setting, msg_setting, msg_content, recipient)
    else:
        pass
