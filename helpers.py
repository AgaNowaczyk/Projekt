import time

SAUCE_URL = "https://www.saucedemo.com/"

USERNAME = "standard_user"
#USERNAME = "problem_user"
#USERNAME = "performance_glitch_user"
#USERNAME = "error_user"
#USERNAME = "visual_user"

PASSWORD = "secret_sauce"

def login(page, username=USERNAME, password=PASSWORD) -> float:
    page.goto(SAUCE_URL)
    page.fill('input[data-test="username"]', username)
    page.fill('input[data-test="password"]', password)
    ctime = time.time()
    page.click('input[data-test="login-button"]')
    return ctime

def add_all_items_to_cart(page):
    add_buttons = page.locator('button[data-test^="add-to-cart"]')
    for i in range(6):
        add_buttons.first.click()

def remove_all_items_from_cart(page):
    remove_buttons = page.locator('button[data-test^="remove"]')
    for i in range(6):
        remove_buttons.first.click()