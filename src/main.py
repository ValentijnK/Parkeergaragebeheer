import requests
import re
import pymysql.cursors
from datetime import datetime

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

def acceptRequest(vehicle):
    fuel = vehicle['hoofdbrandstof']
    if fuel == 'Benzine':
        check_in(vehicle)
    else:
        max_date = datetime.strptime('2001-01-01', '%Y-%m-%d')
        date_afgiteDatum = datetime.strptime(str(vehicle['datumeersteafgiftenederland'])[:10], '%Y-%m-%d')
        if date_afgiteDatum > max_date:
            check_in(vehicle)
        else:
            print('Sorry, maar deze vervuilende diesel mag er niet.')

def check_in(vehicle):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='parkeergarage',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `cars` (`license_plate`) VALUES (%s)"
            cursor.execute(sql, str(vehicle['kenteken']))
            connection.commit()
    finally:
        connection.close()

print(acceptRequest(getVehicleInfo(getLicensePlate('kenteken_2.jpg'))))
