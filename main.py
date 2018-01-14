import os, shutil
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import random

class Generator:
    rate = 0.0
    inputFolder = "Annotations"
    outputFolder = "Annotations0"
    vocPath = "/media/xum/New Volume/data/VOCdevkit/VOC2007/"
    categories = [
        "aeroplane", "bicycle", "bird", "boat", "bottle",
        "bus", "car", "cat", "chair", "cow",
        "diningtable", "dog", "horse", "motorbike", "person",
        "pottedplant", "sheep", "sofa", "train", "tvmonitor"
    ]
    stat_cat_obj = {"_default": 0}
    stat_cat_pic = {"_default": 0}
    stat_cat_boo = {"_default": 0}
    # outputFolder = "Annotations" + str(int(rate * 10))

    def __init__(self, rate=0.5):
        self.rate = rate
        self.outputFolder = self.inputFolder + str(int(rate * 10))
        output_path = self.vocPath + self.outputFolder
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        shutil.copytree(self.vocPath + self.inputFolder, output_path)
        print("Created folder " + output_path)
        self.init_dict()

    def init_dict(self):
        for cat in self.categories:
            self.stat_cat_obj[cat] = 0
            self.stat_cat_pic[cat] = 0
            self.stat_cat_boo[cat] = 0

    def open_xml(self, file_name="2007_000027.xml", old = True):
        if old:
            return ET.parse(self.vocPath + self.inputFolder + '/' + file_name)
        else:
            return ET.parse(self.vocPath + self.outputFolder + '/' + file_name)

    def save_xml(self, data, file_name="2007_000027.xml"):
        # Add marker
        element = ET.Element("MissingRate")
        element.text = str(self.rate)
        root = data.getroot()
        node = root.find('object')
        node.append(element)
        data.write(self.vocPath + self.outputFolder + '/' + file_name)

    def read_xml(self, data):
        objects = []
        nodes = data.getroot().findall('object')
        for node in nodes:
            name = node.find('name')
            objects.append(name.text)
        # print(objects)
        return objects

    def stat(self, file="trainval.txt"):
        if file=="trainval.txt":
            path = self.vocPath + self.inputFolder
        else:
            path = self.vocPath + self.outputFolder
        file_train = self.vocPath + "ImageSets/Main/"+file
        print("Checking boxes from train list: "+file)
        with open(file_train) as f:
            lines = f.readlines()  # get file names
        # not this one -> for file in os.listdir(path):
        for line in lines:
            print(" - Checking file "+line.rstrip())
            # file_path = os.path.join(path, file)
            file = line.rstrip()+".xml"
            self.stat_cat_obj["_default"] += 1
            objects = self.read_xml(self.open_xml(file, False))
            for object in objects:
                self.stat_cat_obj[object] += 1
                self.stat_cat_boo[object] = 1
                assert len(self.stat_cat_obj) == 21
            for cat in self.categories:
                self.stat_cat_pic[cat] += self.stat_cat_boo[cat]
                self.stat_cat_boo[cat] = 0
            self.stat_cat_pic["_default"] += 1
        print("done")
        for keys, values in self.stat_cat_obj.items():
            print(keys,values)

    def stat_show(self):
        g.stat()
        plt.bar(left=xrange(len(self.stat_cat_obj)),
                height=self.stat_cat_obj.viewvalues())
        plt.xticks(xrange(len(self.stat_cat_obj)), self.stat_cat_obj.keys())
        plt.setp(plt.axes().get_xticklabels(), rotation=70)
        plt.show()
        val = [self.stat_cat_obj.values()[k]*1.0 / self.stat_cat_pic.values()[k] for k in xrange(21)]
        plt.bar(left=xrange(len(self.stat_cat_obj)), height=val)
        plt.xticks(xrange(len(self.stat_cat_obj)), self.stat_cat_obj.keys())
        plt.setp(plt.axes().get_xticklabels(), rotation=70)
        plt.show()

    def drop_prob(self, id="000005", rate=0.5):
        # inputFolder
        filename = id + ".xml"
        data = self.open_xml(filename,old=False)
        nodes = data.getroot().findall('object')
        if rate != 0:
          for node in nodes:
            if random.random() < rate: # missing rate
                data.getroot().remove(node)
                # remove the object
          data.write( self.vocPath + self.outputFolder + "/" + id + ".xml" )
        return len(data.getroot().findall('object'))

    def update_list(self):
        file = self.vocPath + "ImageSets/Main/trainval.txt"
        print("Update training list ..")
        with open(file) as f:
            lines = f.readlines() # get file names
        new_content = []
        indeces = []
        count = 0
        for content in lines:
            if self.drop_prob(content.rstrip("\n"), rate=0) > 0:
                new_content.append(content)
                indeces.append(str(count))
            count += 1
        new_file = self.vocPath + "ImageSets/Main/trainval"+ str(int(self.rate * 10)) + ".txt"
        with open(new_file, "w") as f:
            f.writelines(new_content)
            print("Update training list .. OK")
        with open(new_file+"(idx)", "w") as f:
            f.writelines(indeces)

        self.stat(file="trainval"+str(int(self.rate * 10))+".txt")

    def drop_freq(self):
        # check if self.stat run before
        if self.stat_cat_pic["_default"] == 0:
            self.stat()
        # get picture list
        file = self.vocPath+"ImageSets/Main/trainval.txt"
        with open(file) as f:
            lines = f.readlines()  # get file names
        # get drop list for each cat
        for cat in self.categories:
            print( " - Now dropping categoray "+ cat )
            drop_num = int(self.stat_cat_obj[cat]*self.rate)
            drop_list = random.sample(range(self.stat_cat_obj[cat]),drop_num) # index from 0
            index = 0
            for content in lines:
                filename = content.rstrip() + ".xml"
                data = self.open_xml(filename, old = False)
                nodes = data.getroot().findall('object')
                for node in nodes:
                    if node.find('name')==cat:
                        if index in drop_list:
                            # delete that object
                            data.getroot().remove(node)
                    index += 1
                data.write(self.vocPath + self.outputFolder + '/' + filename)
        self.update_list()


    def missing(self, id = "000005"):
        file = self.vocPath+"ImageSets/Main/trainval.txt"
        print("Dropping boxes one by one ..")
        with open(file) as f:
            lines = f.readlines() # get file names
        new_content = []
        for content in lines:
            if self.drop_prob(content.rstrip("\n"), self.rate) >0:
                new_content.append(content)
        new_file = self.vocPath + "ImageSets/Main/trainval"+ str(int(self.rate * 10)) + ".txt"
        with open(new_file, "w") as f:
            f.writelines(new_content)

        print("Created new missing annotations with mr="+str(self.rate))






g = Generator(0.5)

g.drop_freq()
