import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



""" Machine Master """
class machine_master(osv.osv):
    _name = 'vit_pharmacy_machine_hour.machine_master'
    _description = 'Machine Master'

    _columns = {
        'name': fields.char('Name/Brand'),
        'code': fields.char('Code'),
        'type': fields.char('Type'),
        'departement': fields.char('Departement'),
        'location': fields.char('Location'),       
        'capacity': fields.char('Capacity'),       
    }

   