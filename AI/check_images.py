import os
from pprint import pprint
files = [f[:-4] for f in os.listdir('static/media')if f[-3:] == 'jpg']
with open('breeds.csv', 'r') as f:
	labels = f.read().split('\n')
# print(files)
for label in labels:
	label = label[label.find(',')+1:]
	if label is not '' and label not in files:
		print('error with ' + label)
	else:
		os.rename('static/media/' + label + '.jpg', 'static/media/' + label.replace(' ', '_') + '.jpg')