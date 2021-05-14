# Hosts discover prototype

Модуль поиска хостов по сети.

## Использование
```shell
python dscvr 192.168.1.2,192.168.1.1,192.168.1.105 80:83,8080
```

В результате в консоль выведется сравнение найденных хостов и их портов с зарегистрированными
(данные для сравнения берутся из `data.example.json`):

```text
Following expected ports are not found for host "Test host 1" (192.168.1.1): {8080, 422}
Additional port found for host "Test host 1" (192.168.1.1): {80}
New host found:
	None (192.168.1.105:[])
Host not found:
	Test host 2 (192.168.1.2:[80, 422, 9090])
```