
import os
import subprocess
import time
import xml.dom.minidom as DOM
import upnpclient as UPNP

download_line_set = set()

download_file = '/Users/maochuanli/Desktop/download.m3u'
playlist_file = "/Users/maochuanli/Desktop/download.m3u"
save_dir = '/Users/maochuanli/Desktop'
VLC_CMD = '/Applications/VLC.app/Contents/MacOS/VLC'

if os.path.exists('/home/cubie'):
    download_file = '/home/cubie/download.m3u'
    playlist_file = "/home/cubie/download.m3u"
    save_dir = '/usb/tv_files/'
    VLC_CMD = 'vlc'
    print('Cubie board runtime........')
else:
    print('Still on Mac Book.....')

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
        print(cmd)
        print('scp error: ', rc, out)

def is_file_being_written(local_file_list):
    cmd = 'lsof ' + local_file_list
    rc, out = run_cmd(cmd)
    return rc == 0


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

remote_file_list = []
# remote_file_list = get_file_list()
# while len(remote_file_list) <= 0:
#     remote_file_list = get_file_list()
#     time.sleep(1)


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

def getUpnpFolderList(docStr):
    folder_list = []
    document = DOM.parseString(docStr)
    containerElements = document.getElementsByTagName('container')
    for container in containerElements:
        # print(container.tagName, container.attributes.get('id').nodeValue)
        titleList = container.getElementsByTagName('dc:title')
        id = container.attributes.get('id').nodeValue
        title = titleList[0].firstChild.nodeValue
        folder_list.append((id, title))
    return folder_list


def getUpnpPlayList(docStr):
    play_list = []
    document = DOM.parseString(docStr)
    itemElements = document.getElementsByTagName('item')
    for item in itemElements:
        id = item.attributes.get('id').nodeValue

        titleList = item.getElementsByTagName('dc:title')
        title = titleList[0].firstChild.nodeValue

        # if 'Neighbours' == title and 'PARENT-1-18-86347800' in id:
        #     print(item.toprettyxml())

        dateList = item.getElementsByTagName('dc:date')
        if len(dateList) <= 0:
            # print('no date item: ', item)

            continue
        date = dateList[0].firstChild.nodeValue

        resList = item.getElementsByTagName('res')
        mrl = resList[0].firstChild.nodeValue
        play_list.append( (id, title, date, mrl.strip())  )
    return play_list


def upnp_browse(browse_action, objID):
    response_list = []

    start_index = 0
    try:
        response = browse_action.call(ObjectID=objID, BrowseFlag='BrowseDirectChildren', Filter='*',
                                      StartingIndex=start_index,
                                      RequestedCount=5000, SortCriteria='')
    except Exception as e:
        print(e)
        return response_list

    response_list.append(response)
    num_returned = response['NumberReturned']
    num_matched = response['TotalMatches']

    while start_index + num_returned < num_matched:
        response = browse_action.call(ObjectID=objID, BrowseFlag='BrowseDirectChildren', Filter='*',
                                      StartingIndex=start_index,
                                      RequestedCount=5000, SortCriteria='')
        num_returned = response['NumberReturned']
        num_matched = response['TotalMatches']
        response_list.append(response)
        start_index += num_returned

    return response_list


def unwrap_folder(browse_action, folderID):
    response_list = upnp_browse(browse_action, folderID)
    for response in response_list:
        response_xml = response['Result']
        if '<container' in response_xml:
            folders = getUpnpFolderList(response_xml)
            for folder in folders:
                print('Folder> ', folder[0], folder[1])
                unwrap_folder(browse_action, folder[0])
        elif '<item' in response_xml:
            plays = getUpnpPlayList(response_xml)
            for play in plays:
                print('Video> ', play[0], play[1], play[2], play[3])
                download_line_set.add('{},{},{}'.format(play[1], play[2], play[3]))

def get_play_list():
    services = UPNP.SSDP().discover()
    browse_action = None
    for service in services:
        action = service.find_action('Browse')
        print(service.friendly_name, action)
        if 'DMR' in service.friendly_name and action is not None:
            browse_action = action

    root_response_list = upnp_browse(browse_action, '0')
    for response in root_response_list:
        response_xml = response['Result']
        folders = getUpnpFolderList(response_xml)
        for folder in folders:
            print('Root Folder> ', folder[0], folder[1])
            unwrap_folder(browse_action, folder[0])

    with open(download_file, 'w') as f:
        for play_line in download_line_set:
            f.write('{}\n'.format(play_line))

def download_playlist():
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
                print (line)
                seg_list = line.split(',')
                title = seg_list[0].strip().replace(' ', '-').replace(':', '-').replace('\'', '-').replace('&', '-')
                date = seg_list[1].strip().replace(' ', '-').replace(':', '-')
                url = seg_list[2].strip()
                if date == 'None' or not url.startswith('http'):
                    print ('skip: ', line)
                    continue
                # if 'Neighbours' == title and 'T18' in date:

                if not processHttp(title + '-' + date, url):
                    break
                else:
                    print('skip episode: ', line)
                    continue

def copy_to_remote_tomato():
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

def main():
    get_play_list()
    download_playlist()
    # copy_to_remote_tomato()

if __name__ == "__main__":
    main()