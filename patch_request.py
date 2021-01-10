import requests



def patch_sleep_stat(sleep_stat):

    
    url = 'http://127.0.0.1:5000/post/1'
    myobj = {"eye_status":sleep_stat}

    x = requests.patch(url, json= myobj)


def patch_yawn_stat(yawn_stat):

    url = 'http://127.0.0.1:5000/post/1'
    myboj ={"mouth_status":yawn_stat}

    x= requests.patch(url,json=myboj)
  
