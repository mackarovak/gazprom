from locust import HttpUser, between, task

class MyUser(HttpUser):
    wait_time = between(5, 9)
    host="http://0.0.0.0:8000"
    @task(1)
    def insert_data(self):
        id_device = 1
        data = {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0
        }
        self.client.post(f"/device/{id_device}/readings", json=data)

    @task(2)
    def get_data(self):
        device_id = 2 
        self.client.get(f"/device/{device_id}/readings")

    @task(3)
    def create_user(self):
        user_data = {"user_name": "TestUser"}
        self.client.post("/users/", json=user_data)

    @task(4)
    def get_characteristics(self):
        device_id=2
        self.client.get(f"/devices/{device_id}/stats/")

    @task(5)
    def get_user_statistics(self):
        user_id = 1  
        self.client.get(f"/users/{user_id}/stats")

    @task(6)
    def get_user_statistics_by_device(self):
        user_id = 1 
        device_id = 3  
        self.client.get(f"/users/{user_id}/devices/{device_id}/stats")


    @task(7)
    def get_characteristics_with_dates(self):
        start_date = "2024-01-01"
        end_date = "2024-03-31"
        device_id=2
        self.client.get(f"/devices/{device_id}/stats/", params={"start_date": start_date, "end_date": end_date})