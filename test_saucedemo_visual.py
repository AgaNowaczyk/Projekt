import pytest
from playwright.sync_api import Page
from helpers import login, SAUCE_URL, add_all_items_to_cart, remove_all_items_from_cart

def test_login_view(page: Page, assert_snapshot):
    page.goto(SAUCE_URL)
    assert_snapshot(page.screenshot(full_page=True))

def test_inventory_view(page: Page, assert_snapshot):
    login(page)
    # Ensure the inventory page item images are loaded
    page.wait_for_selector('.inventory_item_img')

    assert_snapshot(page.screenshot(full_page=True))

@pytest.mark.parametrize("item", [(0), (1), (2), (3), (4), (5)])
def test_item_page(page: Page, assert_snapshot, item):
    login(page)
    page.goto(f"{SAUCE_URL}inventory-item.html?id={item}")
    
    #Ensure the item image is loaded
    page.wait_for_selector('.inventory_details_img')
    
    assert_snapshot(page.screenshot(full_page=True))

def test_cart_view(page: Page, assert_snapshot):
    login(page)
    add_all_items_to_cart(page)
    page.click('.shopping_cart_link')
    
    # Ensure the cart page is loaded
    page.wait_for_selector('.cart_list')

    assert_snapshot(page.screenshot(full_page=True))

def test_checkout_form_view(page: Page, assert_snapshot):
    login(page)
    add_all_items_to_cart(page)
    page.click('.shopping_cart_link')
    page.click('button[data-test="checkout"]')
    
    # Ensure the checkout form is loaded
    page.wait_for_selector('input[data-test="firstName"]')
    
    assert_snapshot(page.screenshot(full_page=True))

def test_order_summary_view(page: Page, assert_snapshot):
    login(page)
    add_all_items_to_cart(page)
    page.click('.shopping_cart_link')
    page.click('button[data-test="checkout"]')
    
    page.fill('input[data-test="firstName"]', 'Test')
    page.fill('input[data-test="lastName"]', 'User')
    page.fill('input[data-test="postalCode"]', '12345')
    page.click('input[data-test="continue"]')
    
    # Ensure the order summary is loaded
    page.wait_for_selector('.summary_info')
    
    assert_snapshot(page.screenshot(full_page=True))

def test_thank_you_view(page: Page, assert_snapshot):
    login(page)
    add_all_items_to_cart(page)
    page.click('.shopping_cart_link')
    page.click('button[data-test="checkout"]')
    page.fill('input[data-test="firstName"]', 'Test')
    page.fill('input[data-test="lastName"]', 'User')
    page.fill('input[data-test="postalCode"]', '12345')
    page.click('input[data-test="continue"]')
    page.click('button[data-test="finish"]')
    
    # Ensure the thank you page is loaded
    page.wait_for_selector('.complete-header')
    
    assert_snapshot(page.screenshot(full_page=True))