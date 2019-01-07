def delete(file_name):
    import os
    print('Deleting ... {}'.format(file_name))
    os.remove(file_name)


from sys import modules
if __name__ in modules:
    del modules[__name__]
