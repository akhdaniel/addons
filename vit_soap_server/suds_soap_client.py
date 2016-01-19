from suds.client import Client
from datetime import datetime

HOST = 'localhost'
PORT = 8069
DB_NAME = 'openerp'

client = Client('http://%s:%s/soap/netpro?wsdl' % (HOST, PORT))
response = client.service.cek_member_in_claim(dbUser='', dbPassword='', ClaimType='', CardNo='9988', sDate=datetime.now(), PayTo='', errMessage='', ResponseCode='')
print response