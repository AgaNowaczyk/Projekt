import re
import pytest

from playwright.sync_api import Page, expect
from helpers import SAUCE_URL, login, add_all_items_to_cart, remove_all_items_from_cart
        
def test_login_success(page: Page):
    login(page)
    expect(page.locator('.inventory_item')).to_have_count(6)

def test_login_failure(page: Page):
    page.goto(SAUCE_URL)
    page.fill('input[data-test="username"]', "wrong_user")
    page.fill('input[data-test="password"]', "wrong_pass")
    page.click('input[data-test="login-button"]')
    expect(page.locator('[data-test="error"]')).to_be_visible()

def test_product_tiles_content(page: Page):
    login(page)
    items = page.locator('.inventory_item')
    expect(items).to_have_count(6)
    for i in range(6):
        item = items.nth(i)
        expect(item.locator('img.inventory_item_img')).to_be_visible()
        expect(item.locator('.inventory_item_desc')).to_be_visible()
        expect(item.locator('.inventory_item_price')).to_be_visible()
        expect(item.locator('button')).to_have_text("Add to cart")

def test_add_and_remove_from_cart(page: Page):
    login(page)
    add_buttons = page.locator('button[data-test^="add-to-cart"]')
    expect(add_buttons).to_have_count(6)
    
    # Ensure cart is empty before adding items
    expect(page.locator('.shopping_cart_badge')).not_to_be_visible()

    # Add evry item to cart and verify cart count
    for i in range(6):
        expect(add_buttons.first).to_have_text("Add to cart")
        add_buttons.first.click()
        expect(page.locator('.shopping_cart_badge')).to_have_text(f"{i + 1}")

    remove_buttons = page.locator('button[data-test^="remove"]')
    expect(remove_buttons).to_have_count(6)

    # Verify all items can be removed
    for i in range(6):
        expect(remove_buttons.first).to_have_text("Remove")
        remove_buttons.first.click()
        if i < 5:
            expect(page.locator('.shopping_cart_badge')).to_have_text(f"{(5 - i)}")

    # Verify cart is empty after removing all items
    expect(page.locator('.shopping_cart_badge')).not_to_be_visible()

def test_sorting_products(page: Page):
    login(page)
    sort_select = page.locator('[data-test="product-sort-container"]')
    # Sort by name A-Z
    sort_select.select_option("az")
    names = page.locator('.inventory_item_name').all_text_contents()
    assert names == sorted(names)
    # Sort by name Z-A
    sort_select.select_option("za")
    names = page.locator('.inventory_item_name').all_text_contents()
    assert names == sorted(names, reverse=True)
    # Sort by price low-high
    sort_select.select_option("lohi")
    prices = [float(p[1:]) for p in page.locator('.inventory_item_price').all_text_contents()]
    assert prices == sorted(prices)
    # Sort by price high-low
    sort_select.select_option("hilo")
    prices = [float(p[1:]) for p in page.locator('.inventory_item_price').all_text_contents()]
    assert prices == sorted(prices, reverse=True)

@pytest.mark.parametrize("item", [(0), (1), (2), (3), (4), (5)])
def test_add_and_remove_from_item_page(page: Page, item):
    login(page)
    page.goto(f"{SAUCE_URL}inventory-item.html?id={item}")

    add_button = page.locator('button[data-test^="add-to-cart"]').first
    expect(add_button).to_have_text("Add to cart")
    add_button.click()
    expect(page.locator('.shopping_cart_badge')).to_have_text("1")

    remove_button = page.locator('button[data-test^="remove"]').first
    expect(remove_button).to_have_text("Remove")
    remove_button.click()
    expect(page.locator('.shopping_cart_badge')).not_to_be_visible()

def test_hamburger_menu_open_close(page: Page):
    login(page)
    # Open hamburger menu
    page.click('#react-burger-menu-btn')
    expect(page.locator('#react-burger-cross-btn')).to_be_visible()
    # Close hamburger menu
    page.click('#react-burger-cross-btn')
    expect(page.locator('#react-burger-menu-btn')).to_be_visible()

def test_logout_via_hamburger_menu(page: Page):
    login(page)
    page.click('#react-burger-menu-btn')
    logout_link = page.locator('#logout_sidebar_link').first
    expect(logout_link).to_be_visible()
    logout_link.click()

    # After logout, user should be redirected to the login page
    expect(page).to_have_url(SAUCE_URL)

    # After logout, back to inventory is not possible
    page.goto(SAUCE_URL + "inventory.html")
    error_element = page.locator('[data-test="error"]').first
    expect(error_element).to_be_visible()
    expect(error_element).to_have_text("Epic sadface: You can only access '/inventory.html' when you are logged in.")

def test_hamburger_menu_options(page: Page):
    login(page)
    # go to cart page to ensure menu is available from there
    page.click('.shopping_cart_link')
    expect(page).to_have_url(re.compile("cart.html"))

    # Test "All Items"
    page.click('#react-burger-menu-btn')
    expect(page.locator('#inventory_sidebar_link')).to_be_visible()
    page.click('#inventory_sidebar_link')
    expect(page).to_have_url(re.compile("inventory"))

    # Test "About"
    page.click('#react-burger-menu-btn')
    page.click('#about_sidebar_link')
    expect(page).to_have_url(re.compile("saucelabs.com"))

def test_cart_page_content(page: Page):
    login(page)
    add_all_items_to_cart(page)
    page.click('.shopping_cart_link')
    
    # Verify cart page content
    cart_items = page.locator('[data-test=inventory-item]')
    expect(cart_items).to_have_count(6)
    for item in cart_items.all():
        expect(item.locator('[data-test=inventory-item-name]')).to_be_visible()
        expect(item.locator('[data-test=inventory-item-desc]')).to_be_visible()
        expect(item.locator('[data-test=inventory-item-price]')).to_be_visible()
        expect(item.locator('[data-test=item-quantity]')).to_have_text("1")
        expect(item.locator('button[data-test^="remove"]')).to_have_text("Remove")

    remove_all_items_from_cart(page)

    # Verify cart is empty after removing all items
    expect(cart_items).not_to_be_visible()

@pytest.mark.parametrize("item", [(0), (1), (2), (3), (4), (5)])
def test_checkout_any_item(page: Page, item):
    login(page)
    page.locator('button[data-test^="add-to-cart"]').nth(item).click()
    page.click('.shopping_cart_link')
    page.click('button[data-test="checkout"]')
    page.fill('input[data-test="firstName"]', "Jan")
    page.fill('input[data-test="lastName"]', "Kowalski")
    page.fill('input[data-test="postalCode"]', "00-001")
    page.click('input[data-test="continue"]')
    expect(page.locator('.summary_info')).to_be_visible()
    page.click('button[data-test="finish"]')
    expect(page.locator('.complete-header')).to_have_text("Thank you for your order!")
    page.click('button[data-test="back-to-products"]')
    expect(page).to_have_url(re.compile("inventory"))

@pytest.mark.parametrize("customer, result", [
    ({'fn': '', 'ln': '', 'c': ''}, {'valid': 'false', 'error': "Error: First Name is required" }), 
    ({'fn': "Jan", 'ln': '', 'c': ''}, {'valid': 'false', 'error': "Error: Last Name is required" }), 
    ({'fn': "Jan", 'ln': "Kowalski", 'c': ''}, {'valid': 'false', 'error': "Error: Postal Code is required" }),
    ({'fn': "Jan", 'ln': "Kowalski", 'c': '00-001'}, {'valid': 'true', 'error': "" })
])
def test_checkout_form_validation(page: Page, customer, result):
    login(page)
    page.locator('button[data-test^="add-to-cart"]').first.click()
    page.click('.shopping_cart_link')
    page.click('button[data-test="checkout"]')

    page.fill('input[data-test="firstName"]', customer['fn'])
    page.fill('input[data-test="lastName"]', customer['ln'])
    page.fill('input[data-test="postalCode"]', customer['c'])

    page.click('input[data-test="continue"]')

    error_element = page.locator('[data-test="error"]')
    
    if result['valid'] == 'false':
        expect(error_element).to_be_visible()
        expect(error_element).to_have_text(result['error'])
    else:
        expect(error_element).not_to_be_visible()
        expect(page.locator('.summary_info')).to_be_visible()

def test_session_expiry(page: Page):
    login(page)
    # Simulating session expiry is not possible without manipulating cookies or time.
    # Remove cookies and check for redirection:
    page.context.clear_cookies()
    page.reload()
    expect(page).to_have_url(SAUCE_URL)
    expect(page.locator('[data-test="error"]')).to_be_visible()

def test_footer_social_links(page: Page):
    login(page)

    twitter_link = page.locator('a[href*="twitter.com"]')
    facebook_link = page.locator('a[href*="facebook.com"]')
    linkedin_link = page.locator('a[href*="linkedin.com"]')

    expect(twitter_link).to_be_visible()
    expect(facebook_link).to_be_visible()
    expect(linkedin_link).to_be_visible()
    
    with page.expect_popup() as twitter_popup:
        twitter_link.click()
    twitter_page = twitter_popup.value
    assert "x.com" in twitter_page.url

    with page.expect_popup() as facebook_popup:
        facebook_link.click()
    facebook_page = facebook_popup.value
    assert "facebook.com" in facebook_page.url

    with page.expect_popup() as linkedin_popup:
        linkedin_link.click()
    linkedin_page = linkedin_popup.value
    assert "linkedin.com" in linkedin_page.url

def test_cart_state_preserved_after_logout_and_login(page: Page):
    # Login and add two items to cart
    login(page)
    add_buttons = page.locator('button[data-test^="add-to-cart"]')
    add_buttons.nth(0).click()
    add_buttons.nth(1).click()
    expect(page.locator('.shopping_cart_badge')).to_have_text("2")

    # Logout via hamburger menu
    page.click('#react-burger-menu-btn')
    page.locator('#logout_sidebar_link').click()
    expect(page).to_have_url(SAUCE_URL)

    # Login again
    login(page)
    # Cart should still have 2 items after logout/login (state preserved)
    expect(page.locator('.shopping_cart_badge')).to_have_text("2")

def test_cart_state_not_preserved_in_new_context(browser):
    # Start first context and add item to cart
    context1 = browser.new_context()
    page1 = context1.new_page()
    login(page1)
    page1.locator('button[data-test^="add-to-cart"]').first.click()
    expect(page1.locator('.shopping_cart_badge')).to_have_text("1")
    context1.close()

    # Start new context (simulates new browser session)
    context2 = browser.new_context()
    page2 = context2.new_page()
    login(page2)
    # Cart should be empty in new session
    expect(page2.locator('.shopping_cart_badge')).not_to_be_visible()
    context2.close()
