import sys
import glob
import os


def main():
    prefix = sys.argv[1]
    grouping = int(sys.argv[2])
    extension = sys.argv[3]
    if len(sys.argv) >= 5:
        remove = sys.argv[4]
    else:
        remove = None
    print('PREFIX: [{}]'.format(prefix))
    print('GROUPING: [{}]'.format(grouping))
    print('EXTENSION: [{}]'.format(extension))
    print('REMOVE: [{}]'.format(remove))
    images = glob.glob('*.{}'.format(extension))
    images.sort()
    print('IMAGES: [{}]'.format(len(images)))
    if len(images) == 0:
        return
    re_group = None
    directory = None
    s = len(prefix)
    t = s + grouping
    moved, un_moved = 0, 0
    for image in images:
        if remove is not None:
            image = image.replace(remove, '')
        if not image.startswith(prefix):
            continue
        group = unicode(image[s:t], 'utf-8')
        while group.isnumeric() is False:
            group = group[:-1]
        if group != re_group:
            if re_group is not None:
                print('MOVED: {} <- y{: 3} n{: 3}'.format(re_group, moved, un_moved))
            re_group = group
            moved, un_moved = 0, 0
            directory = '{}{}'.format(prefix, group)
            if not os.path.exists(directory):
                os.makedirs(directory)
        if remove is None:
            source = image
        else:
            source = '{}{}'.format(remove, image)
        destination = os.path.join(directory, image)
        try:
            os.rename(source, destination)
            moved += 1
        except:
            un_moved += 1
    if re_group is not None:
        print('MOVED: {} <- y{: 3} n{: 3}'.format(re_group, moved, un_moved))


if __name__ == '__main__':
    main()
