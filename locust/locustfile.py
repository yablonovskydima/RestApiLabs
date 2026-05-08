from locust import HttpUser, task, between
import random

STATUSES = ["available", "borrowed", "retired"]
SORT_OPTIONS = ["title", "year"]
AUTHORS = ["George Orwell", "Frank Herbert", "J.R.R. Tolkien"]


class BooksUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(5)
    def get_books_default(self):
        self.client.get("/books/", name="/books/ [default]")

    @task(3)
    def get_books_with_limit(self):
        limit = random.choice([5, 10, 25, 50])
        self.client.get(f"/books/?limit={limit}", name="/books/ [limit]")

    @task(3)
    def get_books_by_status(self):
        status = random.choice(STATUSES)
        self.client.get(f"/books/?status_filter={status}", name="/books/ [status_filter]")

    @task(2)
    def get_books_by_author(self):
        author = random.choice(AUTHORS)
        self.client.get(f"/books/?author={author}", name="/books/ [author]")

    @task(2)
    def get_books_sorted(self):
        sort_by = random.choice(SORT_OPTIONS)
        self.client.get(f"/books/?sort_by={sort_by}", name="/books/ [sort_by]")

    @task(4)
    def get_books_combined(self):
        params = {}

        if random.random() > 0.5:
            params["status_filter"] = random.choice(STATUSES)

        if random.random() > 0.5:
            params["author"] = random.choice(AUTHORS)

        if random.random() > 0.5:
            params["sort_by"] = random.choice(SORT_OPTIONS)

        params["limit"] = random.choice([10, 25, 50])

        query = "&".join(f"{k}={v}" for k, v in params.items())
        self.client.get(f"/books/?{query}", name="/books/ [combined]")

    @task(1)
    def get_books_invalid_sort(self):
        with self.client.get(
            "/books/?sort_by=invalid",
            name="/books/ [invalid sort_by]",
            catch_response=True
        ) as response:
            if response.status_code == 422:
                response.success()
            else:
                response.failure(f"Expected 422, got {response.status_code}")

    @task(1)
    def get_books_invalid_limit(self):
        with self.client.get(
            "/books/?limit=999",
            name="/books/ [invalid limit]",
            catch_response=True
        ) as response:
            if response.status_code == 422:
                response.success()
            else:
                response.failure(f"Expected 422, got {response.status_code}")