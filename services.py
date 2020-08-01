import requests



def call_api(sleep_status):

    
    url = 'http://127.0.0.1:5000/post/1'
    myobj = {"set_alarm":sleep_status}

    x = requests.patch(url, json= myobj)
  
