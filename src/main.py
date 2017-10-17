import requests
import re

# API keys
rdwAPI = ''
alprAPI = ''

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
    print(r.json())

getVehicleInfo(getLicensePlate('kenteken.png'))