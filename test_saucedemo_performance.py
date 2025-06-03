import time
import pytest
from playwright.sync_api import Page
from helpers import login
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set your performance threshold in seconds
MAX_LOAD_TIME = 2.0

def test_inventory_page_load_performance(page: Page):
    # Measure time from click login button to load inventory page
    start_time = login(page)    
    page.wait_for_selector('.inventory_list', timeout=MAX_LOAD_TIME * 1000)
    load_time = time.time() - start_time

    assert load_time <= MAX_LOAD_TIME, f"Inventory page load time {load_time:.2f}s exceeds threshold {MAX_LOAD_TIME}s"

def test_inventory_page_load_under_pressure(browser_type):

    NUM_USERS = 5
    results = []

    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        futures = [executor.submit(load_inventory, browser_type.name) for _ in range(NUM_USERS)]
        for future in as_completed(futures):
            results.append(future.result())

    for idx, load_time in enumerate(results):
        assert load_time <= MAX_LOAD_TIME, (
            f"User {idx+1}: Inventory page load time {load_time:.2f}s exceeds threshold {MAX_LOAD_TIME}s"
        )

def load_inventory(browser_type_name):
    from playwright.sync_api import sync_playwright
    from helpers import login
    import time
    MAX_LOAD_TIME = 10.0
    with sync_playwright() as p:
        browser = getattr(p, browser_type_name).launch()
        page = browser.new_page()
        try:
            # Measure time from click login button to load inventory page
            start_time = login(page)
            page.wait_for_selector('.inventory_list', timeout=MAX_LOAD_TIME * 1000)
            load_time = time.time() - start_time
            return load_time
        finally:
            page.close()
            browser.close()