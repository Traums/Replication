import psycopg2
import sys
import time
import os, platform
from psycopg2 import Error

def check_connection(check_ip):
    try:
        connection = psycopg2.connect(user="postgres", password="123", host=check_ip, port="5432",
                                        database="postgres")
        cursor = connection.cursor()
        sql_query = 'select 1;'
        cursor.execute(sql_query)
        connection.commit()
        print("БД доступна.")
    except (Exception, Error) as error:
         print("БД недоступна.")

def check_ping(hostname):
    response = os.system("ping -c 1 " + hostname + " > /dev/null")
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False
    return pingstatus

def Replication_process(Primary_ip, Standby_ip):
    id = 1
    flag_promote = False
    flag_master_drop = False
    while ( True ):
        if ( check_ping(Primary_ip) and flag_master_drop == False ):
            print(f"[{id}] Связь с Master есть.")
            check_connection(Primary_ip)

        if ( not check_ping(Primary_ip) and check_ping(Standby_ip) ):
            print(f"[{id}] [Master недоступен, переключение на StandBy].")
            check_connection(Standby_ip)
            flag_master_drop = True
            if (flag_promote == False):
                os.system(f"ssh -i p1 postgres@{Standby_ip} '/usr/lib/postgresql/12/bin/pg_ctl promote -D /var/lib/postgresql/12/main > /dev/null'")
                flag_promote = True
                print("[StandBy переведен в основной режим].")

        if ( check_ping(Primary_ip) and flag_master_drop ):
            print((f"[{id}] Связь с Master восстановлена."))
            check_connection(Primary_ip)
            try:
                os.system(f"ssh -i p0 postgres@{Primary_ip} 'rm -rf /var/lib/postgresql/12/main; mkdir /var/lib/postgresql/12/main; chmod go-rwx /var/lib/postgresql/12/main | pg_basebackup -P -R -X stream -c fast -h 192.168.23.141 -U postgres -D /var/lib/postgresql/12/main | sudo /etc/init.d/postgresql restart'")
                os.system(f"ssh -i p0 postgres@{Primary_ip} 'sudo /etc/init.d/postgresql restart'")
                flag_master_drop = False
                flag_promote = False
                print("Репликация успешно выполнена.") 
            except (Exception, Error) as error:
                print(f"Ошибка репликации")
        id+=1
        time.sleep(2)

def main():

    Primary_ip = '192.168.23.140'
    Standby_ip = '192.168.23.141'
    
    Replication_process(Primary_ip, Standby_ip)

if __name__ == "__main__":
    main()