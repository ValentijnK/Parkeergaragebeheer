import requests
import re
import pymysql.cursors
from datetime import datetime
# Encryption Imports
from Crypto.Cipher import AES
import base64
import os

# API keys
rdwAPI = 'bd91216bb4b6879946c210cdf9dbdfdb00fc75e031816a3c1d89be31ba3512fc'
alprAPI = 'sk_25f871e3d65e30b86d749fe3'

# Url endpoints
rdwUrl = 'https://overheid.io/api/voertuiggegevens/'
alprUrl = 'https://api.openalpr.com/v2/recognize?secret_key=' + alprAPI + '&recognize_vehicle=0&country=eu&state=nl&return_image=0&topn=10'

# Headers
rdwHeaders = {'ovio-api-key': rdwAPI}

# API call to get license plate
def getLicensePlate(photoPath):
    file = {'image': ('image', open('license_plates/' + photoPath, 'rb'))}
    r = requests.post(alprUrl, files=file)
    data = r.json()
    license = data['results'][0]['plate']
    if(license):
        # check if license matches sidecode 9
        if re.match('[A-Z][A-Z]\d\d\d[A-Z]', license):
            licenseList = list(license)
            licenseList.insert(2,'-')
            licenseList.insert(6,'-')
            updatedLicense = ''.join(licenseList)
            return (updatedLicense)
        # license plate is not sidecode 9? check if license matches sidecode 8
        elif re.match('\d[A-Z][A-Z][A-Z]\d\d', license):
            licenseList = list(license)
            licenseList.insert(1, '-')
            licenseList.insert(5, '-')
            updatedLicense = ''.join(licenseList)
            return (updatedLicense)
        # license plate is not sidecode 9 or 8? check if license matches sidecode 7
        elif re.match('\d\d[A-Z][A-Z][A-Z]\d', license):
            licenseList = list(license)
            licenseList.insert(2, '-')
            licenseList.insert(6, '-')
            updatedLicense = ''.join(licenseList)
            return updatedLicense
        # if the plate does not match one of the above fallback to sidecode 4/5/6
        else:
            licenseList = list(license)
            licenseList.insert(2, '-')
            licenseList.insert(5, '-')
            updatedLicense = ''.join(licenseList)
            return updatedLicense


def getVehicleInfo(license):
    r = requests.get(rdwUrl + license, headers=rdwHeaders)
    return r.json()

def acceptRequest(vehicle, license):
    fuel = vehicle['hoofdbrandstof']
    if fuel == 'Benzine':
        check_in(license)
    else:
        max_date = datetime.strptime('2001-01-01', '%Y-%m-%d')
        date_afgiteDatum = datetime.strptime(str(vehicle['datumeersteafgiftenederland'])[:10], '%Y-%m-%d')
        if date_afgiteDatum > max_date:
            check_in(license)
        else:
            print('Sorry, maar deze vervuilende diesel mag er niet.')

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

def check_out(license):
    encrypted_license = encrypt_info(license)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `cars` SET `garage_leave_time` = now(), `garage_entry_time` = garage_entry_time WHERE `license_plate` = %s"
            cursor.execute(sql, encrypted_license)
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
            return result
    finally:
        connection.close()

def encrypt_info(info):
    # A block size of 16 equals 128 bits
    BLOCK_SIZE = 16
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    # Encrypt with AES, encode with base64
    EncodeAES = lambda c, s:base64.b64encode(c.encrypt(pad(s)))
    # Generate a randomized secret key
    secret = b"H\x04 \x9e\x10\x16\xf8\xba\x0b2\xf8\xef}'\x90u"
    # Generate the cipher object using the key
    cipher = AES.new(secret)
    # encode the license plate
    encoded = EncodeAES(cipher, info)
    return encoded

# Extra Assignment
def billing(license):
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
            sql = "UPDATE `cars` SET `garage_entry_time` = garage_entry_time, `garage_leave_time` = garage_leave_time, `email` = %s WHERE `license_plate` = %s"
            cursor.execute(sql, (encrypt_info(email),encrypted_license))
            billing_connection.commit()
    finally:
        billing_connection.close()

    print('Er wordt een factuur verzonden naar ' + str(email))

license = getLicensePlate('kenteken_3.jpg')

if(check_if_exist(license) is None):
    vehicle = getVehicleInfo(license)
    acceptRequest(vehicle, license)
else:
    check_out(license)
    billing(license)