from suds.client import Client

HOST = 'localhost'
PORT = 8069
DB_NAME = 'openerp'

client = Client('http://%s:%s/soap/openerp?wsdl' % (HOST, PORT))

response = client.service.get_member(member_no='2015/11/000022')
print response