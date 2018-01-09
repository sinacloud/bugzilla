
# 安装 bugzilla

## 打开容器终端

http://sae.sina.com.cn/ => 应用 => 容器管理 => 点击 "终端"

## 进入安装目录

```
cd /var/www/html/bugzilla/
```

## 执行安装脚本 init.py

```
[root@localhost /var/www/html/bugzilla]# python init.py
------------------------------  Begin database config  ------------------------------
Please input admin email: bugzilla_mail@sina.com
Input admin password: 
Confirm admin password: 
Admin email is: bugzilla_mail@sina.com 
Admin password is: 123456
Database init success
------------------------------  End database config  ------------------------------
Do you want to config smtp server[Y/n]?Y
------------------------------  Begin SMTP config  ------------------------------
Input admin SMTP server: smtp.sina.com
Input smtp email: notice@sina.com
Input smtp password: 
Confirm smtp password: 
------------------------------  End SMTP config  ------------------------------
NOTICE: you can config smtp at url: http://yourdomain/editparams.cgi
```

* Please input admin email: 输入管理员登录邮箱
* Input admin password: 输入管理员登录密码
* Confirm admin password: 再次输入管理员登录密码
* Do you want to config smtp server[Y/n]?Y 是否开启邮件通知,建议开启
* Input admin SMTP server: 输入SMTP服务器地址,建议使用 http://mail.sina.com/ 新浪邮箱
* Input smtp email: 输入通知邮箱地址
* Input smtp password: 输入通知邮箱地址密码
* Confirm smtp password: 再次输入通知邮箱地址密码


