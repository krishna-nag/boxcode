# -*- coding: utf-8 -*-
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
    
pickle_off = open("Emp.pickle","rb")
emp = pickle.load(pickle_off)
refresh_token=emp["r"]
access_token=emp["a"]
pickle_off.close()
pickle_on=open("Emp.pickle","wb")
emp["no"]=0
pickle.dump(emp,pickle_on)
pickle_on.close()

box = BoxSession('c7ai5c6k9o45tzn98m62udt8rq9j52xd', 'apaGFUm7KVNxQZ9KinRDGg9k68AexsBx', refresh_token, access_token, tokens_changed)

x=box.get_folder_items(0)
print "name   type   id"
for i in x[u'entries']:
	print i[u'name']," ",i[u'type'],i[u'id']