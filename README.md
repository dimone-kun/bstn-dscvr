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
	Unknown (192.168.1.105:[])
Host not found:
	Test host 2 (192.168.1.2:[80, 422, 9090])
```

Результат выведется в формате JSON в stdout:
```json
{
  "hosts": [{
    "name": "Test host 1",
    "address": "192.168.1.1",
    "ports": [80],
    "ports__+": [80],
    "ports__-": [8080, 422]
  }, {
    "name": "Unknown",
    "address": "192.168.1.105",
    "ports": [22]
  }],
  "hosts__+": [{
    "name": "Unknown",
    "address": "192.168.1.105",
    "ports": [22]
  }],
  "hosts__-": [{
    "name": "Test host 2",
    "address": "192.168.1.2",
    "ports": "80, 422, 9090"
  }]
}
```