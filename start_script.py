"""
Created on Thu May 31 12:22:16 2018

@author: krishna Nagaraja
"""
from boxpython import BoxAuthenticateFlow, BoxSession, BoxError
import pickle

def tokens_changed(refresh_token, access_token):
	emp = {"r":refresh_token,"a":access_token,"no":0}
	pickling_on = open("Emp.pickle","wb")
	pickle.dump(emp, pickling_on)
	pickling_on.close()


#BoxAuthenticateFlow('client-id', 'client-secret')
flow = BoxAuthenticateFlow('c7ai5c6k9o45tzn98m62udt8rq9j52xd', 'apaGFUm7KVNxQZ9KinRDGg9k68AexsBx') #replace with your client id and secret here

print flow.get_authorization_url()

auth=input("auth? ")

access_token, refresh_token = flow.get_access_tokens(auth)
tokens_changed(refresh_token,access_token)



# this creates a box session with the access and refresh tokens, and 
# tokens_chenged function is passed as a parameter
# the purpose of this function is to store access and refresh tokens once they get updated
# (this function will be called automatically once the tokens get expired)
box = BoxSession('c7ai5c6k9o45tzn98m62udt8rq9j52xd', 'apaGFUm7KVNxQZ9KinRDGg9k68AexsBx', refresh_token, access_token, tokens_changed)

#Printing the items in the root folder, so that we can note down the id of the desired folder
x=box.get_folder_items(0)
print "name   type   id"
for i in x[u'entries']:
	print i[u'name']," ",i[u'type'],i[u'id']