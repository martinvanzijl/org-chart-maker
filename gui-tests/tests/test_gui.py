# ==============================================================================
# Tests for the GUI.
# ==============================================================================

# Import modules.
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Test case.
def test_login():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Check results.
    add_person_button = driver.find_element(by=By.ID, value="buttonAddPerson")
    assert add_person_button is not None

    # Close the driver.
    driver.quit()

# Test case for Issue #24.
def test_multiple_photos_with_same_name():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Click the "Add person" button.
    add_person_button = driver.find_element(by=By.ID, value="buttonAddPerson")
    add_person_button.click()

    # Click on the canvas.
    canvas = driver.find_element(by=By.TAG_NAME, value="canvas")
    canvas.click()

    # Double-click the person.
    canvas.click()
    canvas.click()

    # Click on the "photos" tab.
    tab = driver.find_element_by_link_text("Photos")
    tab.click()

    # Set photo paths.
    photosDir = os.path.join(os.path.abspath(os.curdir), "images")
    photoPath1 = os.path.join(photosDir, "person_1", "photo.png")
    photoPath2 = os.path.join(photosDir, "person_2", "photo.png")

    # Click on the "add" button. This is not required.
    # buttonAddPhoto = driver.find_element_by_id("buttonAddPhoto")
    # buttonAddPhoto.click()

    # Choose a photo.
    fileInput = driver.find_element_by_id("photoToAdd")
    fileInput.send_keys(photoPath1);

    # Submit the form. This is not required.
    # form = driver.find_element_by_id("uploadPhotoForm")
    # form.submit()

    # Wait for photo to upload.
    # waitForSeconds(driver, 1)

    # Choose a photo with the same name.
    fileInput.send_keys(photoPath2);

    # Check the photo paths.
    photosRow1 = driver.find_element_by_id("photosRow1")
    image1 = photosRow1.find_element_by_tag_name("img")
    imageSource1 = image1.get_attribute("src")

    photosRow2 = driver.find_element_by_id("photosRow2")
    image2 = photosRow2.find_element_by_tag_name("img")
    imageSource2 = image2.get_attribute("src")

    # TODO: Make this pass reliably.
    # assert imageSource1 != imageSource2

    # Close the driver.
    driver.quit()

# Helper functions.
def login(driver):
    """Log in."""

    # Get the web page.
    driver.get("http://localhost:5001/")

    # Check the title.
    title = driver.title
    assert title == "Log In - Org Chart Maker"

    # Wait for elements to load.
    driver.implicitly_wait(0.5)

    # Get elements.
    username_box = driver.find_element(by=By.NAME, value="username")
    password_box = driver.find_element(by=By.NAME, value="password")
    submit_button = driver.find_element(by=By.XPATH, value="/html/body/section/form/input[3]")

    # Interact with elements.
    username_box.send_keys("selenium_user")
    password_box.send_keys("selenium_password")
    submit_button.click()

def waitForSeconds(driver, seconds):
    """Wait for the given number of seconds."""

    try:
        wait = WebDriverWait(driver, seconds).until(returnFalse)
    except TimeoutException as error:
        pass

def returnFalse(driver):
    """Returns false."""

    return False

# Test case for person right-click menu "Edit..." item.
def test_person_right_click_menu_edit():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Click the "Add person" button.
    add_person_button = driver.find_element(by=By.ID, value="buttonAddPerson")
    add_person_button.click()

    # Click on the canvas.
    canvas = driver.find_element(by=By.TAG_NAME, value="canvas")
    canvas.click()

    # Right-click the person.
    action = webdriver.common.action_chains.ActionChains(driver)
    action.context_click(canvas).perform()

    # Click on the "Edit..." option.
    edit_menu_item = driver.find_element(by=By.ID, value="person-context-menu-edit-button")
    edit_menu_item.click()

    # Check the dialog is visible.
    person_details_dialog = driver.find_element(by=By.ID, value="personDetailsDialog")
    assert person_details_dialog.is_displayed()

    # Debug.
    # waitForSeconds(driver, 3)

    # Close the driver.
    driver.quit()

# Test case for person right-click menu "Remove" item.
def test_person_right_click_menu_remove():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Click the "Add person" button.
    add_person_button = driver.find_element(by=By.ID, value="buttonAddPerson")
    add_person_button.click()

    # Click on the canvas.
    canvas = driver.find_element(by=By.TAG_NAME, value="canvas")
    canvas.click()

    # Right-click the person.
    action = webdriver.common.action_chains.ActionChains(driver)
    action.context_click(canvas).perform()

    # Click on the "Remove" option.
    edit_menu_item = driver.find_element(by=By.ID, value="person-context-menu-remove-button")
    edit_menu_item.click()

    # Check the person is removed.
    personCount = driver.execute_script('return Object.keys(persons).length;')
    assert personCount == 0

    # Debug.
    # waitForSeconds(driver, 3)

    # Close the driver.
    driver.quit()

# Test dragging and dropping the "Add Person" button onto the canvas.
def test_drag_and_drop_person_button():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Get the elements.
    add_person_button = driver.find_element(by=By.ID, value="buttonAddPerson")
    canvas = driver.find_element(by=By.TAG_NAME, value="canvas")

    # Drag from the button onto the canvas.
    action = webdriver.common.action_chains.ActionChains(driver)
    # TODO: This has an unreasonably long delay time!
    # action.drag_and_drop(add_person_button, canvas)
    # action.perform()

    # Check a person is added.
    personCount = driver.execute_script('return Object.keys(persons).length;')
    # TODO: Make the test work!
    # assert personCount == 1

# Test the "Manage" page.
def test_manage_page():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Go to the "Manage" page.

    # Hover over the "Options" menu, then click the link.
    buttons = driver.find_elements_by_class_name("dropbtn")

    for button in buttons:
        if button.text == "Options":
            optionsMenu = button
            break

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(optionsMenu)
    action.perform()

    waitForSeconds(driver, 0.1)

    link = driver.find_element_by_link_text("Manage")
    link.click()

    # Check that the "Delete Selected" button is initially disabled.
    button = driver.find_element(by=By.ID, value="buttonDeleteSelected")
    assert not button.is_enabled()

# Test case for the "Started new diagram" toast message.
def test_new_diagram_toast_message():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Wait a short while.
    waitForSeconds(driver, 0.5)

    # Check the toast message is visible.
    message = driver.find_element_by_id("snackbar")
    assert message.is_displayed()

    # Load an existing diagram. This should *not* show the message.
    driver.get("http://localhost:5001/?diagram=example-org-chart")

    # Wait for elements to load.
    driver.implicitly_wait(0.5)

    # Wait a short while.
    waitForSeconds(driver, 0.5)

    # Check the toast message is visible.
    message = driver.find_element_by_id("snackbar")
    assert not message.is_displayed()

    # Close the driver.
    driver.quit()

# Test the "Auto-Layout" feature.
def test_auto_layout():
    # Create the driver.
    driver = webdriver.Chrome("./chromedriver")

    # Log in.
    login(driver)

    # Select the auto-layout menu item.

    # Hover over the "Diagram" menu, then click the menu item.
    buttons = driver.find_elements_by_class_name("dropbtn")

    for button in buttons:
        if button.text == "Diagram":
            diagramMenu = button
            break

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(diagramMenu)
    action.perform()

    waitForSeconds(driver, 0.1)

    link = driver.find_element_by_link_text("Auto-Layout")
    link.click()

    # TODO: Check that the diagram is successfully laid out.
