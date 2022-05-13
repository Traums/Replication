# Репликация БД

Исполнители: Мартюшев, Маров, Пономарева.

Демо: https://www.youtube.com/watch?v=yNkXkKOghTU

## Настройка среды
- Было создано 3 виртуальные машины
	1 Ubuntu1 192.168.23.140 
	2 Ubuntu2 192.168.23.141
	3 Arbitr  192.168.23.142
- Для Arbitr сгенерированы RSA ключи для беспарольного выполнения функций скрипта.
- На Arbitr настроен скрипт Replica.py мониторящий состояние БД и осуществляющий репликацию
- На ВМ Ubuntu1 и Ubuntu2 настроен postgres

```
apt-get install postgresql
```

### Настройка Ubuntu1 - Master
Модифицирован файл pg_hba.conf

```
host    replication    postgres    192.168.23.141/32    md5
```

Модифицирован файл postgresql.conf

```
listen_addresses = '*'
wal_level = hot_standby
archive_mode = on
archive_command = 'cd .'
max_wal_senders = 8
hot_standby = on
```

### Настройка Ubuntu2 - Standby

Модифицирован файл pg_hba.conf
```
host    replication    postgres    192.168.23.140/32    md5
```

Модифицирован файл postgresql.conf
```
listen_addresses = '*'
wal_level = hot_standby
archive_mode = on
archive_command = 'cd .'
max_wal_senders = 8
hot_standby = on
```

Выполнена команда для репликации с Master
```
pg_basebackup -P -R -X stream -c fast -h MASTER_ВНУТРЕННИЙ_IP -U postgres -D ./main
```

## Тестирование

Скрипт Replica.py работает в фоновом режиме на ВМ Arbitr.
Метод check_ping проверяет доступность ВМ командой ping.
Метод check_connection проверяет доступность БД на нацеленной ВМ командой select 1;

В случае падения Ubuntu1 данные дублируются на Ubuntu2 и сервер переходит в основной режим.
После восстановления связи с Ubuntu1 данные реплицируются и конфигурация возвращается к исходному варианту.