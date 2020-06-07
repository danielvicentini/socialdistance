from DB import DBClient
from pprint import pprint

if __name__ == '__main__':
    db = DBClient()

    # Write some data
    db.PeopleCountWrite("EDU","camera",2)
    db.PeopleCountWrite("IND","wifi",3)

    #Get written data
    result = db.PeopleCountQuery()
    pprint (result)
