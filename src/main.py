import requests
import re
import pymysql.cursors
from datetime import datetime
# Encryption Imports
from Crypto.Cipher import AES
import base64
import os

# API keys
rdw_api = 'bd91216bb4b6879946c210cdf9dbdfdb00fc75e031816a3c1d89be31ba3512fc'
alpr_api = 'sk_25f871e3d65e30b86d749fe3'

# Url endpoints
rdw_url = 'https://overheid.io/api/voertuiggegevens/'
alpr_url = 'https://api.openalpr.com/v2/recognize?secret_key=' + alpr_api + '&recognize_vehicle=0&country=eu&state=nl&return_image=0&topn=10'

# Headers
rdw_headers = {'ovio-api-key': rdw_api}


# API call to get license plate
def get_license_plate(photo_path):
    file = {'image': ('image', open('license_plates/' + photo_path, 'rb'))}
    r = requests.post(alpr_url, files=file)
    data = r.json()
    license = data['results'][0]['plate']
    if (license):
        # check if license matches sidecode 9
        if re.match('[A-Z][A-Z]\d\d\d[A-Z]', license):
            license_list = list(license)
            license_list.insert(2, '-')
            license_list.insert(6, '-')
            updated_license = ''.join(license_list)
            return (updated_license)
        # license plate is not sidecode 9? check if license matches sidecode 8
        elif re.match('\d[A-Z][A-Z][A-Z]\d\d', license):
            license_list = list(license)
            license_list.insert(1, '-')
            license_list.insert(5, '-')
            updated_license = ''.join(license_list)
            return (updated_license)
        # license plate is not sidecode 9 or 8? check if license matches sidecode 7
        elif re.match('\d\d[A-Z][A-Z][A-Z]\d', license):
            license_list = list(license)
            license_list.insert(2, '-')
            license_list.insert(6, '-')
            updated_license = ''.join(license_list)
            return updated_license
        # if the plate does not match one of the above fallback to sidecode 4/5/6
        else:
            license_list = list(license)
            license_list.insert(2, '-')
            license_list.insert(5, '-')
            updated_license = ''.join(license_list)
            return updated_license


def get_vehicle_info(license):
    r = requests.get(rdw_url + license, headers=rdw_headers)
    return r.json()


def accept_request(vehicle, license):
    fuel = vehicle['hoofdbrandstof']
    if fuel == 'Benzine':
        check_in(license)
    else:
        max_date = datetime.strptime('2001-01-01', '%Y-%m-%d')
        issue_date = datetime.strptime(str(vehicle['datumeersteafgiftenederland'])[:10], '%Y-%m-%d')
        if issue_date > max_date:
            check_in(license)
        else:
            print('Sorry, maar deze vervuilende diesel mag er niet in.')


def check_in(license):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `cars` (`license_plate`, `garage_entry_time`) VALUES (%s, now())"
            cursor.execute(sql, encrypt_info(license))
            connection.commit()
    finally:
        connection.close()


def check_out(license, id):
    encrypted_license = encrypt_info(license)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `cars` SET `garage_leave_time` = now(), `garage_entry_time` = garage_entry_time WHERE `license_plate` = %s AND `id` = %s"
            cursor.execute(sql, (encrypted_license, id))
            connection.commit()
    finally:
        connection.close()


def check_if_exist(license):
    encrypted_license = encrypt_info(license)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `cars` WHERE `license_plate` = %s"
            cursor.execute(sql, encrypted_license)
            result = cursor.fetchone()
            # print(result)
            if result is None:
                return result
            else:
                return True
    finally:
        connection.close()

def get_vehicle_by_id(license):
    encrypted_license = encrypt_info(license)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `cars` WHERE `license_plate` = %s ORDER BY `id` DESC LIMIT 1"
            cursor.execute(sql, encrypted_license)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()


def encrypt_info(info):
    # A block size of 16 equals 128 bits
    block_size = 16
    padding = '{'
    pad = lambda s: s + (block_size - len(s) % block_size) * padding
    # Encrypt with AES, encode with base64
    Encode_AES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    # Generate a randomized secret key
    secret = b"H\x04 \x9e\x10\x16\xf8\xba\x0b2\xf8\xef}'\x90u"
    # Generate the cipher object using the key
    cipher = AES.new(secret)
    # encode the license plate
    encoded = Encode_AES(cipher, info)
    return encoded


# Extra Assignment
def billing(license, id):
    encrypted_license = encrypt_info(license)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `cars` WHERE `license_plate` = %s AND `id` = %s"
            cursor.execute(sql, (encrypted_license, id))
            result = cursor.fetchone()
    finally:
        connection.close()

    total_seconds = (result['garage_leave_time'] - result['garage_entry_time']).total_seconds()
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    print("De parkeertijd bedroeg %d uur %02d minuten %02d seconden" % (h, m, s) + ' op kenteken ' + license)
    email = input('Vul hier uw e-mailadres in:')

    billing_connection = pymysql.connect(host='localhost',
                                         user='root',
                                         password='',
                                         db='parkeergarage',
                                         cursorclass=pymysql.cursors.DictCursor)
    try:
        with billing_connection.cursor() as cursor:
            sql = "UPDATE `cars` SET `garage_entry_time` = garage_entry_time, `garage_leave_time` = garage_leave_time, `email` = %s WHERE `license_plate` = %s AND `id` = %s"
            cursor.execute(sql, (encrypt_info(email), encrypted_license, id))
            billing_connection.commit()
    finally:
        billing_connection.close()

    print('Er wordt een factuur verzonden naar ' + str(email))


license = get_license_plate('kenteken_diesel_1997.jpg')
if check_if_exist(license) is None:
    print('Voertuig bestaat niet. Voertuig beoordelen / inchecken...')
    vehicle = get_vehicle_info(license)
    accept_request(vehicle, license)
elif check_if_exist(license) is True:
    vehicle = get_vehicle_by_id(license)
    if vehicle['garage_leave_time'] is None:
        print('Voertuig uitchecken en betalen')
        check_out(license, vehicle['id'])
        billing(license, vehicle['id'])
    else:
        print('Voertuig is eerder hier geweest! Voertuig inchecken...')
        vehicle = get_vehicle_info(license)
        accept_request(vehicle, license)


