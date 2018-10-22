#!/usr/bin/env python
# coding: utf-8

# In[3]:


import json

credentials = {}  
credentials['CONSUMER_KEY'] = '0EnBDiOh6UoTIITmK0JwvWIRw'  
credentials['CONSUMER_SECRET'] = 'NDcLH741wk77rDkMc6V1mSSFj1v1o8KxGd7F0MBQmHDeu9Bez5'
credentials['ACCESS_TOKEN'] = '1054432340225781766-yqq6MT890900jlg8pTErUzGurAmmHO'
credentials['ACCESS_SECRET'] = '6v2YkbOCSvwuIK1cj4KqIgdNSA0zaNqcf3SxIO3w5DVCN'

# Save the credentials object to file
with open("twitter_credentials.json", "w") as file:  
    json.dump(credentials, file)


# In[ ]:




