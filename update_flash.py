__author__ = 'azjcode'
import sys
import os
import os.path
import json
import hashlib
import urllib.request
import shutil
import threading

# PS:本脚本直接运行，即可下载全部文件（会覆盖全部，运行前建议备份原文件）

service_url = 'http://down.crysadmapp.cn/crysadm'
# service_url = 'https://github.com/hauntek/crysadm/raw/master/'
rootdir = '.' # 脚本当前路径
ignore_file = [] # 忽略文件

def urlopen(url):
    return urllib.request.urlopen(url).readlines()

def urlretrieve(url, filename):
    urllib.request.urlretrieve(url, filename) 

def SnapshotW(path, cont):
    f = open(path, "a")
    for con in cont:
        j_con = json.dumps(con)
        r = f.write(j_con + "\n") 
    f.close()
    return r

def md5Checksum(filePath):
    fh = open(filePath, 'rb')
    m = hashlib.md5()
    while True:
        data = fh.read(8192)
        if not data:
            break
        m.update(data)
    fh.close()
    return m.hexdigest()

# 检查目录及子目录文件，生成md5校验
def Checksum(rootdir='.', check=False):
    data_list = list()
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            file = os.path.join(parent, filename)
            md5 = md5Checksum(file)
            file = file.replace('\\', '/') # 路径转换
            file = file.replace(rootdir + '/', '') # 根目录转换
            payload = {
                'file': file,
                'md5': md5,
            }
            data_list.append(payload)

    if check == True:
        if os.path.exists('filemd5.txt'):
            os.remove('filemd5.txt') # 删除本地校验记录
        if len(data_list) > 0:
            SnapshotW('filemd5.txt', data_list) # 生成本地校验记录

    return data_list

def down_thread(url, data_list):
    progress = 0
    number = 0
    try:
        for data in data_list:
            urls = url + data.get('file')
            filename = data.get('file')
            fname = filename.split('/')[-1]
            if fname != filename:
                dirpath = filename.replace(fname, '/' + fname)
                dirpath = dirpath.split('//')[0]
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
            urlretrieve(urls, filename)
            number += 1
            progress = number / len(data_list) * 100 # 百分比进度算法
            tmp_str = '正在下载 %s/%s 文件 - %.2f' % (number, len(data_list), progress) + "%"
            sys.stdout.write(tmp_str + "\r")
            sys.stdout.flush()
    except Exception as e:
        pass

    print('下载完成')

def update(backups=True):

    data_list = list()
    data_file = Checksum(rootdir, True) # 是否生成本地校验记录

    try:
        data = urlopen(service_url + '/filemd5.txt')
        for b_date in data:
            data_info = json.loads(b_date.decode('utf-8'))
            if data_info['file'] in ignore_file: continue
            if data_info in data_file: continue
            data_list.append(data_info)
            print('发现更新文件：%s' % data_info['file'])
    except Exception as e:
        return '云端对比文件出现错误，请稍后重试'

    url = service_url + '/'
    if len(data_list) > 0:
        if backups:
            if os.path.exists('.backups'):
                shutil.rmtree('.backups')
            shutil.copytree('.', '.backups')
        threading.Thread(target=down_thread, args=(url, data_list)).start()
    else:
        return '本地源代码和云端一致，无需更新'

    return ''

print(update(False))
