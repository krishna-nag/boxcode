"""
Created on Thu May 31 12:22:16 2018

@author: krishna Nagaraja
"""
import glib
import subprocess
import time
import shutil
import os
import pickle
from boxpython import BoxAuthenticateFlow, BoxSession, BoxError
from pyudev import Context, Monitor

def tokens_changed(refresh_token, access_token):
	
	pickle_off = open("Emp.pickle","rb")
	emp = pickle.load(pickle_off)
	pickle_off.close()
	no=emp["no"]
	emp = {"r":refresh_token,"a":access_token,"no":no}
	pickling_on = open("Emp.pickle","wb")
	pickle.dump(emp, pickling_on)
	pickling_on.close()

def start_session():
	pickle_off = open("Emp.pickle","rb")
	emp = pickle.load(pickle_off)
	access_token=emp["a"]
	refresh_token=emp["r"]
	print access_token
	print refresh_token
	box = BoxSession('c7ai5c6k9o45tzn98m62udt8rq9j52xd', 'apaGFUm7KVNxQZ9KinRDGg9k68AexsBx', refresh_token, access_token, tokens_changed)
	return box

def get_day_no():
	pickle_off = open("Emp.pickle","rb")
	emp = pickle.load(pickle_off)
	no=emp["no"]
	pickle_off.close()
	return no
def setno(no):
	pickle_off = open("Emp.pickle","rb")
	emp = pickle.load(pickle_off)
	emp["no"]=no
	pickle_off.close()
	pickling_on = open("Emp.pickle","wb")
	pickle.dump(emp, pickling_on)
	pickling_on.close()

#################################################################
# Put the id of the folder 'data' or whatever you named it, as noted down in step 4 here 
root_folder_id=0
user="krishn"  #first six characters of user name (must be unique)
################################################################

def upload_folder(path,box,pid):
	x=box.get_folder_items(pid)
	for i in x[u'entries']:
	 if(str(i[u'name']) == "data_folder"):
	   pid=int(str(i[u'id']))
	   break
	walk_generator=os.walk(path)
	root,dirs,files=next(walk_generator)
	rootdir=time.strftime("-%Y-%m-%d")
	rootdir=user+rootdir
	for i in range(1,2000):
    	suffix="-"+str(i)
    	try:
    	 response = box.create_folder(rootdir,pid)
    	 break
    	except BoxError,berr:
    	 continue
	response=box.create_folder("pact_bin",reponse["id"])
	pickle_off=open("Emp.pickle","rb")
	emp=pickle.load(pickle_off)
	latest=emp["no"]
	pickle_off.close()
	for i in files:
    	num=int(re.findall(r'\d+',i)[0])
    	if(num>latest):
    		if(i[0]=='.'):
    		 continue
    		print path+i  
    		try:
    		 box.chunk_upload_file(i, response["id"], path+i)
    		 pickle_on=open("Emp.pickle","wb")
    		 emp2=emp
    		 emp2["no"]=num
    		 pickle.dump(emp,pickle_on)
    		 pickle_on.close()
    		except BoxError, berr:
    		 if(berr.status == 409):
    		  print 'Item with same name exists'
    		 else:
    		  print '%s' % berr            
		
	for i in dirs:
		continue
		if(i[0]=="."):
		 continue            
		print path+i
		upload_folder(path+i+"/",box,response["id"]) 


###################################################################
#####  Enter the absolute path to target folder in pi (don't put / at end)
target_folder="/home/pi/Desktop/data"
###################################################################
try:
    from pyudev.glib import MonitorObserver

    def device_event(observer, device):
    	print "hello"
    	print device.action
    	if(device.action=="add"):
	    	print "add"
	    	time.sleep(1)
	    	op= dict([(item.split()[0],
	             " ".join(item.split()[1:])[" ".join(item.split()[1:]).find("/"):]) for item in subprocess.check_output(
	            ["/bin/bash", "-c", "df"]).decode("utf-8").split("\n") if "/" in item])
	    	print "detected"
	    	
	    	if(device['DEVNAME'] in op.keys()):
	    		target = target_folder+"/"+op[device['DEVNAME']].split("/")[-1]
	    		print target            
		        try:
		            shutil.rmtree(target+"_prev")
		        except OSError:
		            pass
		        try:
		        	os.rename(target,target+"_prev")
		        except OSError:
		            pass	
		        shutil.copytree(op[device['DEVNAME']], target)
		       	print "done"
		       	path=target+"/"
		       	box=start_session()
		       	upload_folder(path,box,root_folder_id)

    	

except:
    from pyudev.glib import GUDevMonitorObserver as MonitorObserver

    def device_event(observer, action, device):
    	print "hello"
    	print action
    	if(action=="add"):
	    	print "add"           
	    	time.sleep(1)
	    	op= dict([(item.split()[0],
	             " ".join(item.split()[1:])[" ".join(item.split()[1:]).find("/"):]) for item in subprocess.check_output(
	            ["/bin/bash", "-c", "df"]).decode("utf-8").split("\n") if "/" in item])
	    	print "detected"
	    	
	    	if(device['DEVNAME'] in op.keys()):
	    		target = target_folder+"/"+op[device['DEVNAME']].split("/")[-1]
	    		print target            
		        try:
		            shutil.rmtree(target+"_prev")
		        except OSError:
		            pass
		        try:
		        	os.rename(target,target+"_prev")
		        except OSError:
		            pass	
		        shutil.copytree(op[device['DEVNAME']], target)
		       	print "done"
		       	path=target+"/"
		       	box=start_session()
		       	upload_folder(path,box,root_folder_id)
       # print 'event {0} on device {1}'.format(action, device)


context = Context()
monitor = Monitor.from_netlink(context)



monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor)

observer.connect('device-event', device_event)
monitor.start()

glib.MainLoop().run()