import os
import time
import subprocess

# playlist_file = "/mnt/downloads/download.m3u"
# save_dir = '/mnt/downloads'
# VLC_CMD = 'vlc'

playlist_file = "/Users/maochuanli/Desktop/download.m3u"
save_dir = '/Users/maochuanli/Desktop'
VLC_CMD = '/Applications/VLC.app/Contents/MacOS/VLC'

def run_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    result = process.communicate()[0]
    return process.returncode, result

def get_file_list(cmd):
    #
    file_list = []
    rc, out = run_cmd(cmd)
    print ('get file list rc:', rc)
    if rc == 0:
        lines = out.split('\n')
        for line in lines:
            file_name = line.strip().split('/')[-1]
            if file_name.endswith('m4v'):
                print('find file: ', file_name)
                file_list.append(file_name)

    return file_list

def copy_to_remote(local_file_path):
    if 'Neighbours' in local_file_path:
        dest_dir = '/opt/home/Neighbours/'
    elif 'American-Dad' in local_file_path:
        dest_dir = '/opt/home/American-Dad/'
    elif 'Movie' in local_file_path:
        dest_dir = '/opt/home/Movies'
    else:
        dest_dir = '/opt/home/'


    cmd = 'scp {} root@10.0.0.1:{}'.format(local_file_path, dest_dir)
    rc, out = run_cmd(cmd)
    if rc == 0:
        print('delete local file: ', local_file_path)
        os.remove(local_file_path)
    else:
        print('scp error: ', rc)

def is_file_being_written(local_file_list):
    cmd = 'lsof ' + local_f_path
    rc, out = run_cmd(cmd)
    return rc == 0

if __name__ == "__main__":
    all_file_list = []
    remote_cmd = 'ssh root@10.0.0.1 "find /opt/home/"'
    remote_file_set = set(get_file_list(remote_cmd))
    # all_file_list.extend(remote_file_set)

    local_cmd = 'find {}'.format(save_dir)
    local_file_list = get_file_list(local_cmd)
    # print('local file list', local_file_list)
    local_file_list.sort()
    for f in local_file_list:
        print(f)
        local_f_path = os.path.join(save_dir, f)
        if f in remote_file_set:
            print('file in remote server, delete it: ', local_f_path)
            os.remove(local_f_path)
        else:
            if is_file_being_written(local_f_path):
                print('local file being written, skip copy: ', local_f_path)
            else:
                print('copy to remote: ', local_f_path)
                copy_to_remote(local_f_path)