import json
import numpy as np
import random
import json

def split_voc(fully_ratio, h_ratio):
    """
    :param fully_ratio: Ratio for the fully supervised dataset
    :param h_ratio: Ratio for the fully supervised part for the bilevel dataset
    :return: Three datasets, data_fully for the full supervised detector, data_fully_w for the bilevel detector with
    bboxes and data_weakly_w for the bilevel detector with weakly annotated data.
    """

    # Load Dataset
    voc_train = json.load(open('pascal_train2007.json'))
    classes = {}
    databyclass_train = {}

    for x in voc_train['categories']:
        classes[x['id']] = x['name']
        databyclass_train[x['id']] = {'images': []}

    # Separate the full dataset between categories
    count = 0
    images_saved = []
    for image in voc_train['images']:
        for ann in voc_train['annotations']:
            if image['id'] == ann['image_id'] and image['id'] not in images_saved:
                images_saved.append(image['id'])
                count += 1
                databyclass_train[ann['category_id']]['images'].append(image)

    # Init of the three datasets
    data_fully = {'type': voc_train['type'], 'categories': voc_train['categories'], 'images': [], 'annotations': []}
    data_fully_w = {'type': voc_train['type'], 'categories': voc_train['categories'], 'images': [], 'annotations': []}
    data_weakly_w = {'type': voc_train['type'], 'categories': voc_train['categories'], 'images': [], 'annotations': []}

    # Split the dataset by images
    for cls in classes.keys():
        random.seed(1)
        num_images = len(databyclass_train[cls]['images'])
        print('Num images for class %d: %d' % (cls, num_images))
        list_idx_total = list(np.linspace(0, num_images - 1, num_images))
        list_fully = random.sample(range(num_images - 1), int((fully_ratio + h_ratio) * num_images))
        list_no_fully = [int(x) for x in list_idx_total if x not in list_fully]
        for num, idx in enumerate(list_fully):
            if num <= np.round(num_images * fully_ratio):
                data_fully['images'].append(databyclass_train[cls]['images'][idx])
            else:
                data_fully_w['images'].append(databyclass_train[cls]['images'][idx])
        for idx_w in list_no_fully:
            data_weakly_w['images'].append(databyclass_train[cls]['images'][idx_w])

    # Ids of the images for the three new datasets
    ids_fully = [x['id'] for x in data_fully['images']]
    ids_fully_w = [x['id'] for x in data_fully_w['images']]
    ids_weakly_w = [x['id'] for x in data_weakly_w['images']]

    # Instances corresponding to each dataset
    for ann in voc_train['annotations']:
        if ann['image_id'] in ids_fully:
            data_fully['annotations'].append(ann)
        elif ann['image_id'] in ids_fully_w:
            data_fully_w['annotations'].append(ann)
        elif ann['image_id'] in ids_weakly_w:
            data_weakly_w['annotations'].append(ann)

    print('Images fully for fully %d' % len(data_fully['images']))
    print('Images fully for weakly %d' % len(data_fully_w['images']))
    print('Images weakly for weakly %d' % len(data_weakly_w['images']))

    return data_fully, data_fully_w, data_weakly_w


if __name__ == '__main__':
    fully_ratio = 1 / 10
    h_ratio = 3 / 10
    data_fully, data_fully_w, data_weakly_w = split_voc(fully_ratio, fully_ratio)
    names = ['voc_2007_fully_f', 'voc_2007_fully_w', 'voc_2007_weakly_w']

    with open('/home/pardogl/shared/datasets/VOC/PASCAL_VOC/divided/%s'%names[0]+'.json','w') as f:
        json.dump(data_fully, f)
    with open('/home/pardogl/shared/datasets/VOC/PASCAL_VOC/divided/%s'%names[1]+'.json','w') as f:
        json.dump(data_fully_w, f)
    with open('/home/pardogl/shared/datasets/VOC/PASCAL_VOC/divided/%s'%names[2]+'.json','w') as f:
        json.dump(data_weakly_w, f)
    