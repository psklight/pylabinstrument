import os
from .__init__ import initialize as check
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog

configFullpath = check()
confData = pd.read_csv(configFullpath)

def openfile_dialog(foldername="a"):
    app = QApplication([dir])
    msg = "Select " + foldername +" folder"
    print(msg)
    fname = QFileDialog.getExistingDirectory(None, msg, '/home')
    return str(fname)

def locateDll(dllname, foldername, root="C:\\Program Files"):

	# check from config file
	subconfData = confData[confData['item']==dllname]

	if subconfData.shape[0]==0 or not os.path.exists(subconfData['location'].values[0]): # i.e. if the dllname is not in the config file, we need try to locate that dllname.

		fdList = os.listdir(root)
		isExist = foldername in set(fdList)

		if not isExist: ## cannot find foldername in current root, will try to let user pick the location once.
			folderpath = openfile_dialog(foldername)
		else:
			folderpath = os.path.join(root, foldername)

		if folderpath!='' and os.path.exists(folderpath):
			dllpath = ""
			for nroot, dirs, files in os.walk(folderpath):
				remain = set([dllname]).intersection(set(files))
				if len(remain)>0:
					dllpath = os.path.join(nroot, list(remain)[0])

			if dllpath!="": # save to the config file
				nrow = confData.shape[0]+1
				confData.loc[nrow,:] = [dllname, dllpath]
				confData.to_csv(configFullpath, index = False)
				print('saved')
				return dllpath
			else:
				raise Exception('Fail to locate {}'.format(foldername))

		else:
			## cannot find foldername in current root, will try to let user pick the location once.
			raise Exception('Fail to locate {} folder'.format(foldername))


	else: # i.e. if the dllname is in the config file, we return the path saved in the config file.
		return subconfData['location'].values[0]