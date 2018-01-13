import os, shutil
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

class Generator:
    rate = 0.0
    inputFolder = "Annotations"
    outputFolder = "Annotations0"
    vocPath = "/Users/xum/Documents/DeepLearning/VOCdevkit/VOC2012/"
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
        os.mkdir(output_path)
        print("Create folder " + output_path)
        self.init_dict()

    def init_dict(self):
        for cat in self.categories:
            self.stat_cat_obj[cat] = 0
            self.stat_cat_pic[cat] = 0
            self.stat_cat_boo[cat] = 0

    def print_node(self, node):
        print "=============================================="
        print "node.attrib:%s" % node.attrib
        if node.attrib.has_key("age") > 0:
            print "node.attrib['age']:%s" % node.attrib['age']
        print "node.tag:%s" % node.tag
        print "node.text:%s" % node.text

    def open_xml(self, file_name="2007_000027.xml"):
        return ET.parse(self.vocPath+self.inputFolder+'/'+file_name)

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

    def stat(self):
        path = self.vocPath + self.inputFolder
        for file in os.listdir(path):
            # file_path = os.path.join(path, file)
            self.stat_cat_obj["_default"] += 1
            objects = self.read_xml(self.open_xml(file))
            for object in objects:
                self.stat_cat_obj[object] += 1
                self.stat_cat_boo[object] = 1
                assert len(self.stat_cat_obj) == 21
            for cat in self.categories:
                self.stat_cat_pic[cat] += self.stat_cat_boo[cat]
                self.stat_cat_boo[cat] = 0
            self.stat_cat_pic["_default"] += 1
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

    def drop_prob(self, rate=0.5):
        # inputFolder
        pass



g = Generator(0.1)
'''
xml_data = g.open_xml()
g.read_xml(xml_data)
g.save_xml(xml_data)
'''
g.stat_show()