from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 to 5 seconds between tasks

    def on_start(self):
        """ login method on start  """
        self.login()
  
    def login(self):
        """ make the login request for creating session """
        response = self.client.post("/login", data={"username": "danbd", "password": "123456"})
        if response.status_code == 200:           
            print("Login successful")
        else:
            print("Login failed")
            self.interrupt()  # Arrête cet utilisateur si la connexion échoue

    @task
    def homepage(self):
        self.client.get("/")  # Simulates visiting the homepage

    @task
    def bulk_domains(self):
        self.client.post('/check_domains', json={"domains":["apple.com","youtube.com","vimeo.com","en.wikipedia.org","youtu.be","microsoft.com","pinterest.com","bit.ly","facebook.com","wikipedia.org","twitter.com","wordpress.org","play.google.com","apps.apple.com","maps.google.com","instagram.com","docs.google.com","adobe.com","plus.google.com","goo.gl","wordpress.com","amazon.com","x.com","tiktok.com","player.vimeo.com","itunes.apple.com","policies.google.com","whatsapp.com","europa.eu","mozilla.org","blogspot.com","github.io","drive.google.com","cloudflare.com","t.me","apache.org","medium.com","wa.me","reddit.com","flickr.com","tumblr.com","gravatar.com","nginx.org","spotify.com","archive.org","soundcloud.com","w3.org","open.spotify.com","yahoo.com","office.com","ec.europa.eu","nytimes.com","creativecommons.org","www.ncbi.nlm.nih.gov","t.co","httpd.apache.org","forbes.com","baidu.com","sourceforge.net","web.archive.org","sites.google.com","who.int","theguardian.com","paypal.com","m.facebook.com","youtube-nocookie.com","tinyurl.com","issuu.com","live.com","opera.com","doi.org","bbc.com","vk.com","bbc.co.uk","mit.edu","googleblog.com","harvard.edu","weebly.com","zoom.us","dropbox.com","reuters.com","cdc.gov","cnn.com","amazonaws.com","google.com","miit.gov.cn","googletagmanager.com","github.com","http://google.com","https://www.facebook.com","api.whatsapp.com","maps.app.goo.gl","wixsite.com","macromedia.com","linkedin.com","beian.miit.gov.cn","forms.gle","nginx.com","nih.gov","sciencedirect.com","qq.com","f5.com"]})  # Simulates checking 100 domains.