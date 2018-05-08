# 福建师范大学学工处助学服务通知提醒

项目主要借鉴[福建师范大学后勤集团停水停电通知提醒](https://github.com/fjnuer/fjnu-hqjt-notification)，针对学工处网站，修改了爬虫规则。

### 1、前言

获取学工处助学服务最新资讯，当助学服务模块有新消息时，通过邮箱发送给用户，方便助学相关部门及时获取学校的最新通知。

### 2、准备

福建师范大学 [学工处](http://stu.fjnu.edu.cn/5732/list.htm) 页面 助学服务 模块可以查到关于资助活动的最新信息。

![](https://ws1.sinaimg.cn/large/006dRdovgy1fq6rm1c869j314y0pkjyt.jpg)

如图所示，资助活动首页有最新的 14 条信息，爬取标题、链接、和日期，存储于 stu.csv 里面。

每隔固定时间爬取一次内容，与原先的 stu.csv 进行比较，但有内容变更时，就通过邮箱发送给用户。

### 3、部署

#### 3.1、安装依赖的包  

这里，假设服务器上的 Linux 发行版为 Arch Linux 或者 Arch 系的其他发行版。部署时应该安装第三方的包。  

```  
sudo pacman -Syyu
sudo pacman -S python
sudo pacman -S python-requests python-beautifulsoup4 python-lxml python-ruamel-yaml
```

**若您使用其他发行版，例如 Ubuntu 或者 CentOS，请自行确认包名。**  

#### 3.2、 项目结构
![](https://ws1.sinaimg.cn/large/006dRdovgy1fq6rtiu1b2j307q034dfm.jpg)

- log.txt 存储日志文件
- README.md
- stu.csv 存储爬虫结果
- stu.py 主文件
- stu.yml 配置文件


#### 3.3、YAML 配置文件

仓库中的 `hqjt.yml` 文件为 YAML 配置文件，便于人类读写，详细内容可以参考 [阮一峰的网络日志 - YAML 语言教程](http://www.ruanyifeng.com/blog/2016/07/yaml.html) 。  

（1）site  
网站根目录，网站中大量内容采用相对地址，保存时可以加上协议和域名补全为绝对地址。  

（2）certificate  

预留证书。HTTPS 是时代潮流，福建师范大学官网已经采用了 HTTPS，未来会有更多的子站采用 HTTPS。但担心管理人员不慎将证书配置错误，导致无法正常访问或抓取数据，因此这里预留证书。  

（3）keywords  

抓取的关键词。YAML 使用空格缩进（数目不重要），只要相同层级的元素左侧对齐即可，但不允许使用Tab键。  

（4）log  

日志文件，暂时未使用。  

（5）page  

福建师范大学学工处助学服务通知页面地址。  

（6）localdata  

未使用数据库，这里使用 csv 文件保留本地数据。**注意，需手动创建同名文件。**  

（7）subscribers  

订阅者。即邮件将发给谁。这里同样是一个列表。前为名称，后为邮箱地址。这些信息将用于发送的邮件的头部设置中。  

这里是收信人信息。

（8）smtp  

SMTP 设置。以 QQ 邮箱为例：  

 - SMTP 服务器： smtp.qq.com  
 - SMTP 账号：你的 QQ 邮箱地址  
 - SMTP 密码：你的 QQ 邮箱登录授权码（十六位，无空格）  

关于获取QQ 邮箱登录授权码，请参考 [什么是授权码，它又是如何设置？](http://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256)  

这里是发信人信息。

（9）mail  

邮箱的主题和发送者名称。  

（10）headers  

请求头中自定义设置，目前非必须，预留方便以后修改。  

注意：  

写完配置文件后，可以在 [YAML Lint](http://www.yamllint.com/) 在线校验是否正确 。 

#### 3.3、计划任务  

推荐使用 [Timer](https://wiki.archlinux.org/index.php/Systemd/Timers)，但 crontab 更常用，这里以 [crontab(菜鸟教程)](http://www.runoob.com/w3cnote/linux-crontab-tasks.html) 为例。  

1) 每小时访问页面一次。  
```
crontab -e
---
0 * * * * /usr/bin/python /root/hqjt/hqjt.py >> /root/hqjt/log.txt
```

2）每天 8、12、16、20 时访问页面
```
crontab -e
---
0 8,12,16,20 * * * /usr/bin/python /root/hqjt/hqjt.py >> /root/hqjt/log.txt
```

3） 因学工处网站工作时间外外网不能访问（上午 8：00 到下午 17：30），因此，这里我设置为 8：20 - 17：20 ，每小时启动一次。

```
crontab -e
---
20 8-17/1 * * * /usr/bin/python /root/hqjt/hqjt.py >> /root/hqjt/log.txt
```

### 4、邮件

本项目使用 SMTP 发送邮件，为了确保能够正常收到邮件，建议将发件人的地址添加到**白名单**中。

以下为第一次收到邮件的样例，包含通知页面所有符合关键词的通知。

![](https://ws1.sinaimg.cn/large/006dRdovgy1fq6s9nh57sj30wa0g90ud.jpg)

第二次起，只会包含新的通知，请知悉。

![](https://ws1.sinaimg.cn/large/006dRdovgy1fqd84wc6uxj30o906r74g.jpg)