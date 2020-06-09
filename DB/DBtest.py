from DB import DBClient
from pprint import pprint
from inventory import DeviceInfo

if __name__ == '__main__':
    db = DBClient()

    # Write some data
    db.PeopleCountWrite("Q2FV-CWAD-KJJN", 2)
    db.PeopleCountWrite("Q2PD-XNUL-RYYQ", 5)

    #Get written data
    result = db.PeopleCountQuery()
    pprint (result)
