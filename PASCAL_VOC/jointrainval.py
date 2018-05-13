import json
from sys import argv

year = int(argv[1])

data_val = json.load(open('pascal_val%d.json'%year))
data_train = json.load(open('pascal_train%d.json'%year))

data = {}

data[u'type'] = data_train['type']
data[u'categories'] = data_train['categories']

data[u'images'] =  data_train['images'] + data_val['images']
data[u'annotations'] =  data_train['annotations'] + data_val['annotations']


with open('voc_%d_trainval.json'%year,'wb') as f:
	json.dump(data,f)
