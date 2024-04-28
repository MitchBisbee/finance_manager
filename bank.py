import requests

# class Accounts:
#    """## Makes API request from plaid to pull your bank account information

#    def __init__(self) -> None:
#        pass

# Your Plaid API keys
client_id = 'user_good'
secret = 'pass_good'

# Step 3: Create a Link token
headers = {'Content-Type': 'application/json'}
data = {
    'client_id': client_id,
    'secret': secret,
    'client_name': 'Your App Name',
    'country_codes': ['US'],
    'language': 'en',
    'user': {
        'client_user_id': 'unique_user_id',
    },
    'products': ['transactions']
}
response = requests.post(
    'https://sandbox.plaid.com/link/token/create', json=data, headers=headers)
print(response)
