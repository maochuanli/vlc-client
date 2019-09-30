
import vlc
import time

download_list = []
download_file = '/Users/maochuanli/Desktop/download.m3u'

def printMediaMeta(media):
    title = media.get_meta(vlc.Meta.Title)
    strbuff = '{}, {}, {}'.format(title, media.get_meta(vlc.Meta.Date), media.get_mrl())
    print strbuff
    if title and title != 'None' and ('Movie:' in title or 'Neighbours' in title or 'American Dad' in title):
        download_list.append(strbuff)


def display(instance, url):
    mrl_list = []
    m=instance.media_new(url)


    p=instance.media_player_new()
    p.set_media(m)
    p.play()
    # if url.startswith('http'):
    #     m.parse()
    #     print 'is parsed:', m.is_parsed()
    #     print 'get title: ', p.get_full_title_descriptions()
    #     if url.startswith('http'):
    #         # for dis in p.get_full_title_descriptions():
    #         #     print 'description: ', dis
    #         # media_item = m.subitems().item_at_index(i)
    #         # sub_url = media_item.get_mrl()
    #
    #         print 'what does media item has: ', m.get_meta(vlc.Meta.Title), m.get_type()

    time.sleep(5)
    for i in range(m.subitems().count()):
        media_item = m.subitems().item_at_index(i)
        sub_url = media_item.get_mrl()
        printMediaMeta(media_item)
        if sub_url.startswith('http'):
            # print 'item: ', media_item.get_meta(vlc.Meta.Title), media_item.get_type(), media_item.get_meta(
            #     vlc.Meta.Date)
            pass
        else:
            mrl_list.append(sub_url)
    p.stop()
    #print 'sub list:', mrl_list

    for mrl in mrl_list:
        print mrl
        #if mrl.startswith('upnp'):
        display(instance, mrl)

    return mrl_list

if __name__ == '__main__':
    vlc_instance = vlc.Instance("--no-video --aout=alsa")
    # vlc_instance = vlc.get_default_instance()
    sd = vlc_instance.media_discoverer_new('upnp')
    sd.start()
    time.sleep(10)
    #sd.stop()
    ml = sd.media_list()
    print 'media list count: ', ml.count()

    for x in range(ml.count()):
        media = ml.item_at_index(x)

        #print 'media is: ', dir(media)
        mrl = media.get_mrl()
        print mrl
        if '10.0.0.201' in mrl:
            display(vlc_instance, mrl)

    if len(download_list) > 0:
        with open(download_file, 'w') as f:
            for line in download_list:
                f.write(line + '\n')