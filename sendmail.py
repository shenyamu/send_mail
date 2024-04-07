#!/f/python/python
#-*- coding: UTF-8 -*-

import email
import smtplib
import getopt
import sys
import importlib
import os
import logging 
import codecs   
import datetime

def usage():
    logger.info(
    """
    Usage:sendmail [option]
    -i:邮件文件名，多个时用","分割
    -v:显示发送过程详细信息
    -t:指定收件人，多个时用","分割
    -d:指定收件域或ip
    -f:指定发件人
    -p:指定发件人密码
    -e:指定ehlo的内容
    -c:指定文件编码格式
    -h:帮助信息
    """)

logger = logging.getLogger("sendmail")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()  
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
ch.setFormatter(formatter)  
logger.addHandler(ch)
    
if len(sys.argv) == 1:
    usage()
    sys.exit()

domain=""
rcpt = [] #list，可指定多个收件人
sender = ""
debug=0
passwd=""
hello="test.com"
coding=''

try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:d:t:vf:p:e:c:")   # sys.argv[1:] 过滤掉第一个参数(它是脚本名称，不是参数的一部分)
except getopt.GetoptError as err:
    logger.error("argv error:{}".format(err))
    sys.exit()
for cmd, arg in opts:  # 使用一个循环，每次从opts中取出一个两元组，赋给两个变量。cmd保存选项参数，arg为附加参数
    if cmd in ("-h"):
        usage()
        sys.exit()
    elif cmd in ("-i"):
        qid_list=arg.split(',')
        if len(qid_list) > 0:
            eml_list=qid_list
        else:
            eml_list[0]=arg
    elif cmd in("-d"):
        domain=arg
    elif cmd in ("-t"):
        rctmp_list=arg.split(',')
        if len(rctmp_list) > 0:
            rcpt=rctmp_list
        else:
            rcpt[0]=arg
    elif cmd in ("-v"):
        debug=1
    elif cmd in ("-f"):
        sender=arg
    elif cmd in ("-p"):
        passwd=arg
    elif cmd in ("-e"):
        hello=arg
    elif cmd in ("-c"):
        coding=arg
        
logger.info("your python version:{}.{}".format(sys.version_info.major,sys.version_info.minor))
if len(domain)==0 or len(sender)==0:
    logger.error("The recipient domain or sender is empty")
    sys.exit()
    
server = smtplib.SMTP(domain, 25, hello)
if passwd.strip() != "":
    logger.info("start smtp login, account:{}".format(sender))
    server.login(sender, passwd)
if debug == 1:
    server.set_debuglevel(1)
            
for qid in eml_list:
    if not os.path.exists(qid):  
        logger.error("{}:file no exist!".format(qid))
        continue    
    try:
        #fp = open(qid, "r")
        if len(coding)==0:
            fp = codecs.open(qid, "r")
        else:
            fp = codecs.open(qid, "r",  encoding=coding)
        msg = email.message_from_file(fp)
    except Exception as e:
        logger.error("read eml fail:{}, retry utf-8".format(e))
        fp = codecs.open(qid, "r", encoding='utf-8')
        msg = email.message_from_file(fp)
    try:
        msg.replace_header('from', sender)
        header_to=','.join(rcpt)
        msg.replace_header('to', header_to)
        now_datetime = datetime.datetime.now()
        formatted_datetime = now_datetime.strftime('%d %b %Y %H:%M:%S %z')
        #msg.replace_header('date', formatted_datetime)
        msg.__delitem__('X-Bordeaux-Mailfrom')
        msg.__delitem__('DKIM-Signature')
        logger.info("start send mail, from:{}, to:{}".format(sender, rcpt))
        if sys.version_info.major == 2:
            mailcon=msg.as_string()
        else:
            mailcon=msg.as_string().encode('utf-8')
        response = server.sendmail(sender, rcpt, mailcon)
        logger.info("send mail success")
    except smtplib.SMTPException as e:
        logger.error("send mail fail:{}".format(e))
server.quit()
logger.info("all done,exit")