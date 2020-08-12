import requests



def call_api(sleep_status):

    
    url = 'http://127.0.0.1:5000/post/1'
    myobj = {"set_alarm":sleep_status}

    x = requests.patch(url, json= myobj)
    
    
def call_api_mouth(mouth_status):

    url = 'http://127.0.0.1:5000/post/1'
    myobj1 = {"mouth_status":mouth_status}

    x = requests.patch(url, json= myobj1)


  
