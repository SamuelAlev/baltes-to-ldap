import sys
import math
import time
import re
import os

import ldap
import ldap.modlist as modlist

import pyodbc


def main():
    ldap_inst = try_ldap_bind(
        os.environ['LDAP_HOST'], os.environ['LDAP_ADMIN_USER'], os.environ['LDAP_ADMIN_PASS'])
    print("Connected to LDAP")
    mssql_inst = try_mssql_bind()

    cursor = mssql_inst.cursor()
    cursor.execute('SELECT * FROM [Baltes].[dbo].[BaltesStarface]')

    for row in cursor:
        create_user(ldap_inst, {
            'firstname': row[1] or 'NoName',
            'lastname': row[0] or 'NoName',
            'number': re.sub("[^0-9]", "", row[2])
        })


def try_mssql_bind():
    conn = pyodbc.connect('Driver=FreeTDS;'
                          'Server=' + os.environ['DB_HOST'] + ';'
                          'Database=' + os.environ['DB_NAME'] + ';'
                          #   'Trusted_Connection=yes;'
                          'UID=' + os.environ['DB_USER'] + ';'
                          'PWD=' + os.environ['DB_PASS'] + ';')

    return conn


def try_ldap_bind(ldap_host, admin_dn, admin_pass):
    try:
        ldap_conn = ldap.initialize(ldap_host)
    except ldap.SERVER_DOWN:
        print("Can't contact LDAP server")
        exit(4)

    try:
        ldap_conn.simple_bind_s(admin_dn, admin_pass)
    except ldap.INVALID_CREDENTIALS:
        print("This password is incorrect!")
        sys.exit(3)

    return ldap_conn


def create_user(ldap_instance, user):
    # username = ''.join(map(lambda e: e[0], user['firstname'].split(
    #     ' '))).lower() + user['lastname'].lower()
    fullname = user['firstname'].strip().title() + ' ' + \
        user['lastname'].strip().title()
    dn = 'uid=' + fullname + ',' + os.environ['LDAP_BASE_DN']

    entry = []
    entry.extend([
        ('objectClass', [b"person", b"inetOrgPerson", b"top"]),
        ('uid', fullname.encode()),
        ('cn', fullname.encode()),
        ('givenName', user['firstname'].strip().title().encode()),
        ('mobile', user['number'].encode()),
        ('sn', user['lastname'].strip().title().encode()),
    ])

    try:
        ldap_instance.add_s(dn, entry)
        print('Added:', fullname)
    except ldap.ALREADY_EXISTS:
        print('Error:', fullname, 'already exist')
    except:
        print('Error:', fullname, sys.exc_info()[0])


if __name__ == "__main__":
    main()
