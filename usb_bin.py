"""
Created on Thu May 31 12:22:16 2018

@author: krishna Nagaraja

This file is for the smoke sensor, which takes only non-image data
"""
import glib
import subprocess
import time
import shutil
import os
import pickle
from boxpython import BoxAuthenticateFlow, BoxSession, BoxError
from pyudev import Context, Monitor
import re

# For storing tokens and the number of the latest file uploaded, 
# a pickle file is used. The name of this file is Emp.pickle
# The advantage of pickle file is that python datastructures like dictionaries
# can be stored and accessed very fast. Here we store a dictionary called Emp
# The keys of this dictionary are :
# a: access_token
# r: refresh_token
# no: the number of the latest file uploaded

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




#################################################################
# Put the id of the folder 'data' or whatever you named it, as noted down in step 4 here 
root_folder_id=49857411974 # foder id of PACT_web_service
user="krishn"  #first six characters of user name (must be unique)
################################################################

def upload_folder(path,box,pid):
	#In PACT_web_service, we have to get id of data_folder
	x=box.get_folder_items(pid)
	for i in x[u'entries']:
	 if(str(i[u'name']) == "data_folder"):
	   print str(i[u'id'])
	   pid=int(str(i[u'id']))
	   break
	#once we have the id of the data_foder, we want to create a new folder
	# with the format "subID-yyyy-mm-dd-serialno"   
	
	rootdir=time.strftime("-%Y-%m-%d")
	rootdir=user+rootdir
	for i in range(1,2000):
	 suffix="-"+str(i)
	 try:
	  response = box.create_folder(rootdir+suffix,pid)
	  print suffix
	  break
	 except BoxError,berr:
	  continue
	# Then we create a folder pact_bin inside it
	try:
	 response=box.create_folder("pact_bin",response["id"])
	 print "done.."
	except BoxError,berr:
	 print berr

	walk_generator=os.walk(path)
	root,dirs,files=next(walk_generator)

	pickle_off=open("Emp.pickle","rb")
	emp=pickle.load(pickle_off)
	latest=emp["no"] #load the latest number of file uploaded
	pickle_off.close()
	for i in files:
	 num=int(re.findall(r'\d+',i)[0]) #The number on the bin file
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
	#ignore this loop	
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
		        	#delete previous file
		            shutil.rmtree(target+"_prev")
		        except OSError:
		            pass
		        try:
		        	#store the previous file for backup
		        	os.rename(target,target+"_prev")
		        except OSError:
		            pass
		        #copy files from USB to pi	
		        shutil.copytree(op[device['DEVNAME']], target)
		       	print "done"
		       	path=target+"/"
		       	box=start_session()
		       	#upload to box
		       	upload_folder(path,box,root_folder_id)
       # print 'event {0} on device {1}'.format(action, device)


context = Context()
monitor = Monitor.from_netlink(context)



monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor)

#call the function device_event when an event is observed
observer.connect('device-event', device_event)
monitor.start()

glib.MainLoop().run()