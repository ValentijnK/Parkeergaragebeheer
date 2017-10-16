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
    # print(data)
    license = data['results'][0]['plate']
    # print(license)
    if(license):
        # check if license matches sidecode 7
        if(re.match('\d\d[A-Z][A-Z][A-Z]\d', license)):
            licenseList = list(license)
            licenseList.insert(2,'-')
            licenseList.insert(6,'-')
            updatedLicense = ''.join(licenseList)
            return (updatedLicense)
        # if no sidecode 7 is detected fallback to sidecode 6
        else:
            licenseList = list(license)
            licenseList.insert(2, '-')
            licenseList.insert(5, '-')
            updatedLicense = ''.join(licenseList)
            return updatedLicense


def getVehicleInfo(license):
    r = requests.get(rdwUrl + license, headers=rdwHeaders)
    print(r.json())

getVehicleInfo(getLicensePlate('kenteken_2.jpg'))