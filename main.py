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


def get_file_list(cmd = 'ssh root@10.0.0.1 "find /opt/home/"'):
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

remote_file_list = get_file_list()
while len(remote_file_list) <= 0:
    remote_file_list = get_file_list()
    time.sleep(1)


def download(url, local_file):
    cmd = '{} -I dummy "{}"   --sout="#transcode{{vcodec=h264,acodec=mp3,ab=128,channels=2,samplerate=44100}}:std{{access=file,mux=mp4,dst={}}}"'
    cmd2 = cmd.format(VLC_CMD, url, local_file) + " --play-and-exit"
    print(cmd2)
    base_name = os.path.basename(local_file)

    if base_name in remote_file_list:
        print('file uploaded already:', base_name)
        return True
    if os.path.exists(local_file) and os.path.getsize(local_file) > 10 * 1024 * 1024:
        print('file downloaded already: ' + local_file)
        return True
    else:
        if os.path.exists(local_file):
            os.remove(local_file)
        rc, out = run_cmd(cmd2)
        print(out)
        return 'error' not in out or os.path.getsize(local_file) > 10 * 1024 * 1024


def processHttp(title, url):
    seg_list = url.split('-')
    id = '100'
    if len(seg_list) > 5:
        id = seg_list[5]
    save_file = os.path.join(save_dir, title + "-" + id + '.m4v')
    rc = download(url, save_file)
    try_times = 1
    while True != rc:
        time.sleep(60)
        rc = download(url, save_file)
        try_times += 1
        if try_times > 60 * 3:
            return False

    return True


if __name__ == "__main__":
    title = None
    with open(playlist_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            # ##EXTINF:0,American Dad
            # if line.startswith('#EXTINF'):
            #     title = line.split(',')[1]
            #     title = title.replace(' ', '-').replace(':', '-')
            #     continue
            # if line.startswith('http'):
            #     if not processHttp(title, line):
            #         break
            if len(line) > 0:
                print line
                seg_list = line.split(',')
                title = seg_list[0].strip().replace(' ', '-').replace(':', '-').replace('\'', '-')
                date = seg_list[1].strip().replace(' ', '-').replace(':', '-')
                url = seg_list[2].strip()
                if date == 'None' or not url.startswith('http'):
                    print 'skip: ', line
                    continue
                if not processHttp(title + '-' + date, url):
                    break