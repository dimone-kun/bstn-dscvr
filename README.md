# Hosts discover prototype

Модуль поиска хостов по сети.

## Использование
```shell
python dscvr 192.168.0.1,192.168.1.0/255.255.255,192.168.2.0/24 80:83,8080
```

В результате в консоль выведется хосты, к которым не удалось получить доступ и результаты проверки
портов на доступных хостах:

```text
Port 80 is open for 192.168.1.1
Port 81 is closed for 192.168.1.1
Port 82 is closed for 192.168.1.1
Port 83 is closed for 192.168.1.1
Port 8080 is closed for 192.168.1.1
Host 192.168.1.2 is unavailable
```