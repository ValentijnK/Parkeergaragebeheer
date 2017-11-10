Miniproject Parkeergaragebeheer
===============================

Miniproject voor de Hogeschool Utrecht. Het bouwen van een systeem voor een parkeergarage.
Kentekens moeten bij binnenkomst worden gescand en worden opgeslagen met timestamps. Dieselauto's met een afgiftedatum van vóór 2001 mogen de garage niet in.
Data moet beveiligd worden opgeslagen.

Links
-----

[RDW API](https://overheid.io) Ophalen van gegevens op basis van kenteken.

[Automatic License Plate Recognition](https://openalpr.com) Kentekens herkennen van foto's of video's.

[Nederlandse kentekens](https://nl.wikipedia.org/wiki/Nederlands_kenteken) Kenteken sidecodes en informatie

Dependencies
------------

Voer dit commando uit om direct alle dependencies te installeren

```
cd to/project/root
pip3 install -r requirements.txt
```

[Requests](http://docs.python-requests.org/en/master/) HTTP for Humans

[PyMySQL](https://pymysql.readthedocs.io/en/latest/user/index.html) MySQL connector for Python3

[PyCrypto](https://pythonprogramming.net/encryption-and-decryption-in-python-code-example-with-explanation/) AES data encryption

Database
--------

De gebruiker moet zelf een database aanmaken met de volgende parameters:

```

db_name = 'parkeergarage'
user = 'root'
password = ''


```

De gebruiker kan er ook voor kiezen andere parameters te gebruiken, die moeten dan handmatig worden aangepast in de code (hardcoded)

**Note**

Met het bijgeleverde sql bestand kan de tabel worden opgebouwd.