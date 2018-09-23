def cat(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f.readlines()):
            print('{:03} {}'.format(i+1, l), end='')
