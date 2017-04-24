''' LOOK UP COMPANY NAME IN THE DATABSE,
IF NOT THERE, ADD IT USING GOOGLE!!!'''
import pandas as pd

import models
from utils import name_clean

def create_company(symbol,name,sector,exchange):
    name = name_clean(name)
    models.Company.create(
        symbol = symbol,
        name = name,
        sector = sector,
        exchange = exchange)

def company_dictionary():
    company_dict = {}
    for firm in models.Company.select():
        company_dict[firm.symbol] = [firm.name,firm.exchange]
    return company_dict

'''CREATE FUNCTION THAT DOWNLOADS ALL 'UPDATE' or "n/a"
sectors and tries to update/add to database!!!!!'''
