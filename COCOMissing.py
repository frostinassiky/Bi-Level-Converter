from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, shutil
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import random



import numpy as np
import json
import random
import time

class COCOMissingGenerator:
    rate = 0.0
    inputFile = "/instances_train2014_mr0.json"
    annotation_path = "/home/xum/Documents/Datasets/COCO/annotations"
    annotation_file = annotation_path+inputFile
    saved_file = []

    def __init__(self, rate=0.5):
        self.rate = rate
        self.cats_stat = np.zeros((100,))
        self.missed_num = 0
        outputFile = "/instances_train2014_mr"+str(rate)+".json"
        self.saved_file = self.annotation_path + outputFile

        # load
        print('Loading annotations into memory...')
        tic = time.time()
        self.dataset = json.load(open(self.annotation_file, 'r'))
        assert type(self.dataset) == dict, \
            'annotation file format {} not supported'.format(type(self.dataset))
        print('Done in t={:0.2f}s'.format(time.time() - tic))

    def stat(self):
        for anno in self.dataset["annotations"]:
            cat = anno["category_id"]
            self.cats_stat[cat] = self.cats_stat[cat] + 1

    def stat_show(self):
        import matplotlib.pyplot as plt
        n = len(self.cats_stat)
        x = range(n)
        width = 1 / 1.5
        plt.bar(x, self.cats_stat, width, color="blue")
        fig = plt.gcf()
        return fig


    def drop_freq(self):
        # check length
        self.print()

        # stat
        self.stat()
        self.stat_show()

        # new annotations_80cls
        annotations_80cls = []
        for anno in self.dataset["annotations"]:
            annotations_80cls.append(anno)
        all_anna_num = len(annotations_80cls)  # =75247
        self.missed_num = int(all_anna_num * self.rate)

        # new images_80cls
        images_80cls = []
        count = 0
        for pict in self.dataset["images"]:
            id = pict["id"]
            count = count + 1
            if count % 100 == 0:
                print("Processing", count, '/', len(self.dataset["images"]))

            for anno in annotations_80cls:
                if anno["image_id"] == id:
                    # print("add class number ",anno["id"])
                    images_80cls.append(pict)
                    break

        # delete missing label
        missed_index = []
        for k in range(0, self.missed_num):
            missed_index = random.randint(0, len(annotations_80cls))
            discard = annotations_80cls.pop(missed_index)
        remaind_anna_num = len(annotations_80cls)

        # merge
        dataset_3cls = {
            "info": self.dataset["info"],
            "images": images_80cls,
            "licenses": self.dataset["licenses"],
            "annotations": annotations_80cls,
            "categories": self.dataset["categories"]
        }

        # save
        filePath = self.saved_file
        with open(filePath, 'w') as fid:
            json.dump(dataset_3cls, fid)

        print("missing label file saved to " + self.saved_file)
        print("original annotation number: ", all_anna_num)
        print("missing rate: ", self.rate)
        print("remaind annotation number: ", remaind_anna_num)



    def print(self):
        # check length
        import pprint
        pprint.pprint(len(self.dataset))


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mr = float(sys.argv[1])
    else:
        mr = 0.5
    print ('Missing Rate ', mr)
    g = COCOMissingGenerator(mr)

    g.drop_freq()