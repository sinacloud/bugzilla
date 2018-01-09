#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import os
import re
import subprocess
import sys


def main():
    db_host = os.getenv('MYSQL_HOST')
    db_user = os.getenv('MYSQL_USER')
    db_passwd = os.getenv('MYSQL_PASS')
    db_name = os.getenv('MYSQL_DB')
    db_port = os.getenv('MYSQL_PORT')

    d = {
        'MYSQL_HOST': db_host,
        'MYSQL_USER': db_user,
        'MYSQL_PASS': db_passwd,
        'MYSQL_DB': db_name,
        'MYSQL_PORT': db_port,
        'ADMIN_KEYS': db_passwd
    }

    email_re = re.compile(r'[\w.-]+@[\w.-]+.\w+')
    # init localconfig
    localconfig = '/var/www/html/localconfig'
    if os.path.exists(localconfig):
        try:
            lines = open(localconfig).readlines()
            flen = len(lines) - 1

            for i in range(flen):
                line = lines[i]
                for k, v in d.items():
                    if k in line:
                        lines[i] = line.replace(k, v)

            with open(localconfig, 'w') as f:
                f.writelines(lines)
        except Exception as e:
            print e

    else:
        print 'localconfig file is not exists'

    # init database
    db_port = int(db_port)
    sqlfile = '/var/www/html/bugs.sql'

    boundary = '-' * 30

    if os.path.exists('/usr/bin/mysql'):
        cmd = '/usr/bin/mysql -h%s -u%s -p%s -P %d -e "use %s; show tables" 2>/dev/null' % (
            db_host, db_user, db_passwd, db_port, db_name)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()

        if err:
            print 'Database not init before install bugzilla.'
            sys.exit(1)

        # empty database need init
        if not output:
            print '%s %s %s' % (boundary, ' Begin database config ', boundary)
            admin_email = raw_input('Please input admin email: ')

            if not admin_email:
                print 'You must set env ADMIN_USER to install bugzilla.'
                sys.exit(1)

            if not re.match(email_re, admin_email):
                print "Email address not valid"
                sys.exit(1)

            c = 0
            while c < 3:
                admin_password = getpass.getpass('Input admin password: ')
                re_admin_password = getpass.getpass('Confirm admin password: ')

                if admin_password != re_admin_password:
                    print 'The password entered twice does not match, please try again.'
                    c = c + 1
                else:
                    break

            gCmd = '/usr/bin/perl genpasswd.pl %s 2>/dev/null' % admin_password
            g = subprocess.Popen(gCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            goutput, gerr = g.communicate()

            if not gerr:
                old_admin_user = 'bugzilla_mail@sina.com'
                old_admin_passwd = '123456654321'
                replaceCmd = "sed -i -e 's#%s#%s#g' -e 's#%s#%s#g' %s" % (
                    old_admin_user, admin_email, old_admin_passwd, goutput, sqlfile)
                r = subprocess.Popen(replaceCmd, shell=True)
                r.wait()
                if r.returncode != 0:
                    print 'Admin user and password init failed!'
                    sys.exit(1)

                msg = 'Admin email is: %s \nAdmin password is: %s\n' % (admin_email, admin_password)
                print msg

                # import database
                iCmd = '/usr/bin/mysql -h%s -u%s -p%s -P %d  %s < %s 2>/dev/null' % (
                    db_host, db_user, db_passwd, db_port, db_name, sqlfile)
                p = subprocess.Popen(iCmd, shell=True)
                p.wait()
                if p.returncode != 0:
                    print 'Database import failed'
                    sys.exit(1)
                else:
                    print 'Database init success'
                    # mv bugs.sql to other place
                    os.remove(sqlfile)
                    print '%s %s %s\n' % (boundary, ' End database config ', boundary)
            else:
                print 'Generate admin user password error: %s' % gerr
                sys.exit(1)
    else:
        print 'system no mysql command'

    # init data
    # http://domain/editparams.cgi
    params_file = '/var/www/html/data/params.json'

    yes = set(['y', 'ye', 'yes'])
    smtp_answer = raw_input('Do you want to config smtp server[Y/n]?').lower()

    if smtp_answer in yes:
        print '%s %s %s' % (boundary, ' Begin SMTP config ', boundary)
        if not os.path.exists(params_file):
            print 'file %s not exists' % params_file
            sys.exit(1)
        else:
            smtp_server = raw_input('Input admin SMTP server: ')
            if smtp_server:
                replaceCmd = "sed -i -e 's#%s#%s#g'  %s" % ('ADMIN_SMTP', smtp_server, params_file)
                r = subprocess.Popen(replaceCmd, shell=True)
                r.wait()
                if r.returncode != 0:
                    print 'Admin smtp server write failed'
                    sys.exit(1)

            smtp_email = raw_input('Input smtp email: ')
            if smtp_email:
                if not re.match(email_re, smtp_email):
                    print "SMTP email address not valid"
                    sys.exit(1)

                replaceCmd = "sed -i -e 's#%s#%s#g'  %s" % ('ADMIN_EMAIL_USER', smtp_email, params_file)
                r = subprocess.Popen(replaceCmd, shell=True)
                r.wait()
                if r.returncode != 0:
                    print 'smtp email  write failed'
                    sys.exit(1)

            k = 0
            while k < 3:
                smtp_password = getpass.getpass('Input smtp password: ')
                re_smtp_password = getpass.getpass('Confirm smtp password: ')

                if smtp_password != re_smtp_password:
                    print 'The password entered twice does not match, please try again.'
                    k = k + 1
                else:
                    replaceCmd = "sed -i -e 's#%s#%s#g'  %s" % ('ADMIN_EMAIL_PASS', smtp_password, params_file)
                    r = subprocess.Popen(replaceCmd, shell=True)
                    r.wait()
                    if r.returncode != 0:
                        print 'smtp password write failed'
                        sys.exit(1)
                    break

            #  admin_domain = raw_input('Input admin domain: ')
            #  if admin_domain:
            admin_domain = ''
            replaceCmd = "sed -i -e 's#%s#%s#g'  %s" % ('ADMIN_DOMAIN', admin_domain, params_file)
            r = subprocess.Popen(replaceCmd, shell=True)
            r.wait()
            #  if r.returncode != 0:
            #  print 'Admin domain domain write failed'
            #  sys.exit(1)

            print '%s %s %s\n' % (boundary, ' End SMTP config ', boundary)
        checksetup_db = "sed -i 's/$dbh->bz_setup_database/#$dbh->bz_setup_database/g' checksetup.pl"
        checksetup_tb = "sed -i 's/$dbh->bz_populate_enum_tables/#$dbh->bz_populate_enum_tables/g' checksetup.pl"
        r = subprocess.Popen(checksetup_db, shell=True)
        r.wait()
        r = subprocess.Popen(checksetup_tb, shell=True)
        r.wait()

        r = subprocess.Popen('./checksetup.pl', shell=True)
        r.wait()
        
        print 'NOTICE: you can config smtp at url: http://yourdomain/editparams.cgi\n'


if __name__ == '__main__':
    main()
