import os, shutil

def get_dirs():
    path = 'E:\lfw_all'
    target_path = 'E:\lfw_mvd'

    dirs = os.listdir(path)

    match_count = 0
    mismatch_count = 0
    match_list = []
    mismatch_list = []
    for dir in dirs:
        files = os.listdir(os.path.join(path, dir))
        if len(files) == 2 and match_count <= 500:
            match_list.append(dir)
            match_count += 1
        if len(files) == 1 and mismatch_count <= 1000:
            mismatch_list.append(dir)
            mismatch_count += 1
        if (match_count > 500) and (mismatch_count > 1000):
            break

    mismatch_pairs = [mismatch_list[i:i + 2] for i in range(0, len(mismatch_list), 2)]

    print('Начали копировать')
    for match in match_list:
        shutil.copytree(os.path.join(path, match), os.path.join(target_path, 'match', match))
        print(match)

    n = 1
    for mismatch in mismatch_pairs:
        try:
            os.mkdir(os.path.join(target_path, 'mismatch', str(n)))
        except:
            pass

        for file_mismatch in mismatch:
            print(n)
            photos = os.listdir(os.path.join(path, file_mismatch))
            shutil.copyfile(os.path.join(path, file_mismatch, photos[0]), os.path.join(target_path, 'mismatch', str(n), photos[0]))
        n += 1



if __name__ == '__main__':
    get_dirs()