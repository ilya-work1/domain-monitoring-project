from locust import HttpUser, task, between
import random

class DomainMonitoringUser(HttpUser):
    wait_time = between(1, 2)
    
    def load_domains_from_file(self):
        """Load domains from the test file"""
        try:
            with open('domain_test.txt', 'r') as file:
                domains = [line.strip() for line in file if line.strip()]
            print(f"Loaded {len(domains)} domains from file")
            return domains
        except Exception as e:
            print(f"Error loading domains: {e}")
            return []

    def on_start(self):
        """Setup and login before starting tests"""
        self.username = f"locust_user_{random.randint(1,10000)}"
        self.client.post("/NewUser", data={
            "username": self.username,
            "password": "test_password"
        })
        self.login()
        self.domains = self.load_domains_from_file()
        print(f"User {self.username} initialized with {len(self.domains)} domains")

    def login(self):
        response = self.client.post("/login", data={
            "username": self.username,
            "password": "test_password"
        })

    @task
    def bulk_domain_check(self):
        """Test checking all domains from file"""
        print(f"User {self.username} starting bulk check of {len(self.domains)} domains")
        response = self.client.post("/check_domains", json={
            "domains": self.domains
        })
        print(f"Bulk check completed for {self.username}. Status: {response.status_code}")
        
    @task
    def get_domains_status(self):
        """Check status of domains"""
        response = self.client.get("/get_domains")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data)} domains for {self.username}")