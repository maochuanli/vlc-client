
import vlc
import time

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

    time.sleep(30)
    if m.subitems():
        for i in range(m.subitems().count()):
            media_item = m.subitems().item_at_index(i)
            sub_url = media_item.get_mrl()
            if sub_url.startswith('http'):
                print 'item: ', media_item.get_meta(vlc.Meta.Title), media_item.get_type(), media_item.get_meta(
                    vlc.Meta.Date)
            else:
                mrl_list.append(sub_url)
    else:
        print 'no sub items'
    p.stop()
    #print 'sub list:', mrl_list

    for mrl in mrl_list:
        print mrl
        #if mrl.startswith('upnp'):
        display(instance, mrl)

    return mrl_list

def printMediaMeta(media):
    strbuff = ''
    for i in range(12):
        meta = vlc.Meta(i)
        strbuff += str(media.get_meta(meta)) + ', '
    print strbuff

if __name__ == '__main__':
    vlc_instance = vlc.Instance("--no-video --aout=alsa")

    # vlc_instance = vlc.get_default_instance()
    sd = vlc_instance.media_discoverer_new_from_name('upnp')
    # sd.start()
    time.sleep(10)
    print 'is media discovery running', sd.is_running()
    #sd.stop()
    ml = sd.media_list()
    print 'media list count: ', ml.count()

    for x in range(ml.count()):
        media = ml.item_at_index(x)
        printMediaMeta(media)
        #print 'media is: ', dir(media)
        mrl = media.get_mrl()
        print mrl
        # if '10.0.0.201' in mrl:
        display(vlc_instance, mrl)
