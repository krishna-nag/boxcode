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

# print "access: "+str(access_token)
# print "refresh: "+str(refresh_token)

box = BoxSession('c7ai5c6k9o45tzn98m62udt8rq9j52xd', 'apaGFUm7KVNxQZ9KinRDGg9k68AexsBx', refresh_token, access_token, tokens_changed)

x=box.get_folder_items(0)
print "name   type   id"
for i in x[u'entries']:
	print i[u'name']," ",i[u'type'],i[u'id']