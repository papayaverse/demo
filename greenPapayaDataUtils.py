import requests
import json

class greenPapayaDataUtils :
    
    def __init__(self) :
        self.infura_url = 'https://nft.api.infura.io/networks/43113/'
        self.proj_id = '85e35e212e7c431a838571e469b3c64b'
        self.proj_secret = '67760e3a23204a7e84a170d1364e33c0'


    # token_address is a String by default
    def getCollectionMetadata(self, token_address):
        request_url = self.infura_url + 'nfts/' + token_address
        response = requests.get(request_url, auth=(self.proj_id, self.proj_secret))
        if response.status_code == 200:
            res = response.json()
            print(res)
        return response

    # token_address, token_id are strings
    def getNFTMetadata(self, token_address, token_id):
        request_url = self.infura_url + 'nfts/' + token_address + '/tokens/' + token_id
        response = requests.get(request_url, auth=(self.proj_id, self.proj_secret))
        if response.status_code == 200:
            res = response.json()
            print(res)

    #token_address is a string
    def getNFTsByCollection(self, token_address):
        request_url = self.infura_url + 'nfts/' + token_address + '/tokens/'
        response = requests.get(request_url, auth=(self.proj_id, self.proj_secret))
        if response.status_code == 200:
            res = response.json()
            print(res)

    # address is a string
    def getNFTsOwned(self, address):
        request_url = self.infura_url + 'accounts/' + address + '/assets/nfts/'
        response = requests.get(request_url, auth=(self.proj_id, self.proj_secret))
        if response.status_code == 200:
            res = response.json()
            if res['total'] == 0:
                print('No NFTs owned by ' + address)
            else:
                print(res)
            return res
