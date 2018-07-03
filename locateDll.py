import os
from .__init__ import initialize as check
import pandas as pd

configFullpath = check()
confData = pd.read_csv(configFullpath)

def locateDll(dllname, foldername, root="C:\\Program Files"):

	# check from config file
	subconfData = confData[confData['item']==dllname]

	if subconfData.shape[0]==0 or not os.path.exists(subconfData['location'].values[0]): # i.e. if the dllname is not in the config file, we need try to locate that dllname.

		fdList = os.listdir(root)
		isExist = foldername in set(fdList)

		if isExist:
			root = os.path.join(root, foldername)
			# print(root)

			for nroot, dirs, files in os.walk(root):
				remain = set([dllname]).intersection(set(files))
				if len(remain)>0:
					dllpath = os.path.join(nroot, list(remain)[0])

			# save to the config file
			nrow = confData.shape[0]+1
			confData.loc[nrow,:] = [dllname, dllpath]
			confData.to_csv(configFullpath, index = False)

			return dllpath

		else:
			raise Exception('Could not locate {}'.format(foldername))

	else: # i.e. if the dllname is in the config file, we return the path saved in the config file.
		return subconfData['location'].values[0]
