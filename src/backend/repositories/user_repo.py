import json

class CustomerRepository:
    CUSTOMER_FILE = 'data/customer_db.json'
    
    def __init__(self):
        '''
        Checks if data/customer_db.json exists. If not, creates it and writes the headers.
        '''
        pass
    
    def get_all_customers(self):
        '''
        Returns all the Customer(s) from the database.
        '''
        with open(self.CUSTOMER_FILE) as file:
            customers = json.load(file)['Customers']
            return customers
    
    def get_customer_by_id(self):
        '''
        Returns the Customer instance according to the id.
        '''
        return []
    
    def get_customer_by_username(self, username):
        '''
        Returns the Customer instance according to the username.
        '''
        with open(self.CUSTOMER_FILE) as file:
            customers = json.load(file)['Customers']
            for row in customers:
                if row['username'] == username :
                    return row
            return None

    
    def get_customer_by_email(self, email):
        '''
        Returns the Customer instance according to the email.
        '''
        with open(self.CUSTOMER_FILE) as file:
            customers = json.load(file)['Customers'] 
            for row in customers:
                if row['email'] == email :
                    return row
            return None