import requests

def get_ngrok_base():
    import requests
    r = requests.get('http://localhost:4040/api/tunnels')
    info_json = r.json()
    remote_base = next(t["public_url"] for t in info_json["tunnels"] if t["public_url"].startswith('https'))
    return remote_base
