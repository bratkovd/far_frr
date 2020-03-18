import os, requests, shutil

def get_pairs_dev_test(counter):
    try:
        req = requests.get('http://vis-www.cs.umass.edu/lfw/pairsDevTest.txt')

        file = open(os.path.join('pairsDevTest.txt'), "w")
        file.write(req.text)
        file.close()
    except:
        exit(1)

    rfile = open(os.path.join('pairsDevTest.txt'), "r").readlines()

    counter = 1
    match_list = []
    mismatch_list = []

    for l in rfile:
        if (counter > 1) and (counter <= 501):
            n = l.split()
            match_list.append([n[0] + '--' + n[1], n[0] + '--' + n[2]])
        elif (counter > 501) and (counter <= 1001):
            n = l.split()
            mismatch_list.append([n[0] + '--' + n[1], n[2] + '--' + n[3]])

        counter += 1

    os.remove(os.path.join('pairsDevTest.txt'))
    data_set = {'match_pairs': match_list[0:int(counter)], 'mismatch_pairs': mismatch_list[0:int(counter)]}

    return data_set

def get_files():
    path = 'E:\lfw_all'
    path_orig = 'E:\mvd_base\orig'
    path_size_center = 'E:\mvd_base\center'
    path_size_height = 'E:\mvd_base\height'
    dirs = os.listdir(path)[0:500000]

    # Копирование папок в orig
    iter_num = 1
    for dir in dirs:
        try:
            shutil.copytree(os.path.join(path, dir), os.path.join(path_orig, dir))
            shutil.copytree(os.path.join(path, dir), os.path.join(path_size_center, dir))
            shutil.copytree(os.path.join(path, dir), os.path.join(path_size_height, dir))
            iter_num += 1
            print(f'Скопировали {iter_num} папок')
        except Exception as e:
            print(e)



if __name__ == '__main__':
    #data = get_pairs_dev_test(500)
    #print(data)
    get_files()