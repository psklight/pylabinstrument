import os
import pandas as pd

name = 'pyoptics'

def initialize(reset=False):

	userprofile = os.environ['USERPROFILE']

	foldername = '.'+name
	fulldir = os.path.join(userprofile, foldername)

	if not os.path.exists(fulldir):
		os.mkdir(fulldir)

	filename = 'dlllocations.csv'

	# if the file does not exist, create an empty one
	if not os.path.exists( os.path.join(fulldir, filename) ) or reset:
		data = pd.DataFrame(columns=['item','location'])
		data.to_csv(os.path.join(fulldir, filename), index=False)

	return os.path.join(fulldir, filename)


initialize()