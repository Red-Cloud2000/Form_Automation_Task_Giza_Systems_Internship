import csv
import inspect
import os

from pytest_selenium import driver
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from tenacity import sleep
from selenium.webdriver.common.keys import Keys

def log_error_to_csv(error_message, class_name, function_name, input_data, expected_result, platform):
    file_path = "error_log.csv"
    error_count = 1

    # Use the error message as the Actual Result
    actual_result = error_message.strip()

    # Check if the file exists and determine the error number
    if os.path.exists(file_path):
        with open(file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) > 1:
                last_row = rows[-1]
                # Extract the number from the last error number (Bug_x)
                last_error_number = int(last_row[0].split('_')[1])
                error_count = last_error_number + 1

    # Append the error information to the CSV file
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write the header if it's the first error
        if error_count == 1:
            writer.writerow([
                "Error Number", "Test Suite", "Test Title", "First Name", "Last Name", "Gender", "Hobbies",
                "Department / Office", "Username", "Password", "Confirm Password", "E-Mail", "Contact No.",
                "Additional Info", "Expected Result", "Actual Result", "Platform"
            ])
        # Write the error entry with "Bug_" prefix for the error number
        writer.writerow([
            f"Bug_{error_count}", class_name, function_name, input_data.get("first_name"), input_data.get("last_name"),
            input_data.get("gender"), input_data.get("hobbies"), input_data.get("department_office"),
            input_data.get("username"), input_data.get("password"), input_data.get("confirm_password"),
            input_data.get("email"), input_data.get("contact_no"), input_data.get("additional_info"),
            expected_result, actual_result, platform
        ])

    print("Error logged to CSV")

# Initialize driver
def initialize_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

# Bypass SSL
def bypass_ssl_warnings(driver):
    driver.find_element(By.ID, "details-button").click()
    driver.find_element(By.ID, "proceed-link").click()


# Global variables to hold form values
first_name = ""
last_name = ""
gender = ""
selected_hobbies = []
department = ""
username = ""
password = ""
confirm_password = ""
email = ""
contact_no = ""
additional_info = ""

result = ""

def get_fields_value(driver):
    global first_name, last_name, gender, selected_hobbies, department, username, password, confirm_password, email, contact_no, additional_info

    # Find the form elements and retrieve their values
    first_name = driver.find_element(By.NAME, 'first_name').get_attribute('value')
    last_name = driver.find_element(By.NAME, 'last_name').get_attribute('value')

    # Gender (radio buttons)
    gender_male = driver.find_element(By.ID, 'inlineRadioMale').is_selected()
    gender_female = driver.find_element(By.ID, 'inlineRadioFemale').is_selected()
    gender = "Male" if gender_male else "Female" if gender_female else ""

    # Hobbies (multi-select dropdown)
    hobbies_element = driver.find_element(By.ID, 'exampleFormControlSelect2')
    selected_hobbies = [option.text for option in hobbies_element.find_elements(By.TAG_NAME, 'option') if option.is_selected()]
    if not selected_hobbies:
        selected_hobbies = None

    # Department / Office (dropdown)
    department_element = Select(driver.find_element(By.NAME, 'department'))
    department = department_element.first_selected_option.text
    if department == "Select your Department/Office":
        department = None

    # Username
    username = driver.find_element(By.NAME, 'user_name').get_attribute('value')

    # Password (use .get_attribute('value') carefully for passwords in a secure environment)
    password = driver.find_element(By.NAME, 'user_password').get_attribute('value')
    confirm_password = driver.find_element(By.NAME, 'confirm_password').get_attribute('value')

    # E-Mail
    email = driver.find_element(By.NAME, 'email').get_attribute('value')

    # Contact No.
    contact_no = driver.find_element(By.NAME, 'contact_no').get_attribute('value')

    # Additional Info
    additional_info = driver.find_element(By.ID, 'exampleFormControlTextarea1').get_attribute('value')


# Class for form tests
class TestFormSubmission:

    @staticmethod
    def fill_form(driver):
        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Ahmed")
        driver.find_element(By.ID, "inlineRadioMale").click()
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(By.NAME, "user_name").send_keys("abdo1234")
        user_pass = "45454545"
        driver.find_element(By.NAME, "user_password").send_keys(user_pass)
        driver.find_element(By.NAME, "confirm_password").send_keys(user_pass)
        driver.find_element(By.NAME, "email").send_keys("joker@aaa.com")
        driver.find_element(By.NAME, "contact_no").send_keys("201015421458")
        driver.find_element(By.ID, "exampleFormControlTextarea1").send_keys("I'm a SW Tester :)")

    @staticmethod
    def validate_success_message(driver):
        success_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "success_message"))
        )
        assert "Success" in success_element.text, f"Expected 'Success' but got: '{success_element.text}'"
        print(f"Form submitted successfully and '{success_element.text}' message validated.")
        return success_element.text

    def test_form_empty_form_submission(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if submit_button.is_enabled():
            log_error_to_csv(
                error_message="Form is empty but the submit button was enabled",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Submit button is disabled",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Form is empty but the submit button was enabled, test failed.")
        else:
            print("Test passed: Submit button is disabled as expected.")
        driver.quit()

    def test_form_filling(self):
        global result
        driver = initialize_driver()
        try:
            driver.get("https://mytestingthoughts.com/Sample/home.html")
            bypass_ssl_warnings(driver)
            self.fill_form(driver)
            get_fields_value(driver)

            #click on the submit button
            driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button").click()
            result = self.validate_success_message(driver)

        except Exception as e:
            error_message = str(e)
            get_fields_value(driver)
            log_error_to_csv(
                error_message=error_message,
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"Form submitted successfully and '{result}' message is displayed",
                platform="Web - Chrome"
            )
        finally:
            driver.quit()

# Class for input validation tests
class TestFirstAndLastNameValidation:  #Mandatory

    def test_first_and_last_name_single_character(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "first_name").send_keys("A")
        driver.find_element(By.NAME, "last_name").send_keys("H")
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[1]').is_displayed() and
                driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[1]').is_displayed()):

            log_error_to_csv(
                error_message="The first and last name accepts a single character input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The first and last name don't accept a single character input",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The first and last name accepts a single character input, test failed.")
        else:
            print("Test passed: The first and last name don't accept a single character input as expected.")
        driver.quit()

    def test_first_and_last_name_has_a_number(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "first_name").send_keys("1Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hashim44")

        if not (driver.find_element(By.XPATH,'//*[@id="contact_form"]/fieldset/div[1]/div/small[1]').is_displayed() and
                driver.find_element(By.XPATH,'//*[@id="contact_form"]/fieldset/div[2]/div/small[1]').is_displayed()):
            get_fields_value(driver)
            log_error_to_csv(
                error_message="The first and last name accept having a number",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The first and last name don't accept having a number",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The first and last name accept having a number, test failed.")
        else:
            print("Test passed: The first and last name don't accept having a number as expected.")
        driver.quit()

    def test_first_and_last_name_clearing_after_filling(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill the first name and last name fields
        first_name_field = driver.find_element(By.NAME, "first_name")
        first_name_field.send_keys("Ahmed")

        last_name_field = driver.find_element(By.NAME, "last_name")
        last_name_field.send_keys("Hashim")

        get_fields_value(driver)
        sleep(2.0)

        # Clear the first name and last name fields
        for _ in range(len("Ahmed")):  # length of the string "Ahmed"
            first_name_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        for _ in range(len("Hashim")):  # length of the string "Hashim"
            last_name_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        # Find and extract error message text for both fields
        first_name_error_message = driver.find_element(By.XPATH, '/html/body/div/form/fieldset/div[1]/div/small[2]')
        first_name_error_message_text = first_name_error_message.get_attribute("textContent").strip()

        last_name_error_message = driver.find_element(By.CSS_SELECTOR,
                                                      '#contact_form > fieldset > div:nth-child(4) > div > small:nth-child(3)')
        last_name_error_message_text = last_name_error_message.get_attribute("textContent").strip()

        # Check if both error messages are displayed
        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[2]').is_displayed() and
                driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[2]').is_displayed()):


            # Log the error to the CSV file
            log_error_to_csv(
                error_message=f"The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages aren't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The '" + first_name_error_message_text + "' and '" + last_name_error_message_text + "' error messages are displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                f"The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages aren't displayed, test failed.")
        else:
            print(
                f"Test passed: The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages are displayed as expected.")

        driver.quit()

    def test_first_and_last_name_with_special_characters(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill in first and last names with special characters
        driver.find_element(By.NAME, "first_name").send_keys("#Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hashim%")

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if validation error messages are displayed
        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[1]').is_displayed() and
                driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[1]').is_displayed()):

            # Log the error to the CSV file
            log_error_to_csv(
                error_message="The first and last name accept having special characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The first and last name don't accept having special characters",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The first and last name accept having special characters, test failed.")
        else:
            print("Test passed: The first and last name don't accept having special characters as expected.")

        driver.quit()

    def test_first_and_last_name_submit_form_with_invalid_data(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill in first and last names with invalid data (too short)
        driver.find_element(By.NAME, "first_name").send_keys("A")
        driver.find_element(By.NAME, "last_name").send_keys("H")

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if the submit button is enabled
        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if submit_button.is_enabled():

            # Log the error to the CSV file
            log_error_to_csv(
                error_message="The submit button is clickable with invalid First and Last name input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The submit button is not clickable with invalid First and Last name input",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The submit button is clickable with invalid First and Last name input, test failed.")
        else:
            print("Test passed: The submit button is not clickable with invalid First and Last name input as expected.")

        driver.quit()

class TestGenderRadioButtonValidation:  #Mandatory

    def test_gender_no_option_is_selected_by_default(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Capture form field values immediately after opening the page
        get_fields_value(driver)

        # Check if any gender radio button is pre-selected
        if driver.find_element(By.ID, "inlineRadioMale").is_selected() or driver.find_element(By.ID,"inlineRadioFemale").is_selected():
            log_error_to_csv(
                error_message="The Male/Female radio button is pre-selected when the page loads",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The Male/Female radio button is not pre-selected when the page loads",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The Male/Female radio button is pre-selected when the page loads, test failed.")
        else:
            print("Test passed: The Male/Female radio button is not pre-selected when the page loads as expected.")

        driver.quit()

    def test_gender_single_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Select Male and then Female radio buttons
        driver.find_element(By.ID, "inlineRadioMale").click()
        sleep(3)
        driver.find_element(By.ID, "inlineRadioFemale").click()
        sleep(3)
        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if both options are selected (shouldn't be possible)
        if driver.find_element(By.ID, "inlineRadioMale").is_selected():
            log_error_to_csv(
                error_message="More than one option can be selected at a time",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Only one option can be selected at a time",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("More than one option can be selected at a time, test failed.")
        else:
            print("Test passed: Only one option can be selected at a time as expected.")

        driver.quit()

    def test_gender_selected_option_assertion(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Select Male and then Female radio buttons
        driver.find_element(By.ID, "inlineRadioMale").click()
        is_male_selected = driver.find_element(By.ID, "inlineRadioMale").is_selected()
        driver.find_element(By.ID, "inlineRadioFemale").click()
        is_female_selected = driver.find_element(By.ID, "inlineRadioFemale").is_selected()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if the selected options are asserted properly
        if not (is_male_selected and is_female_selected):
            log_error_to_csv(
                error_message="The Male/Female radio button is not successfully selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The Male/Female radio button is successfully selected",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The Male/Female radio button is not successfully selected, test failed.")
        else:
            print("Test passed: The Male/Female radio button is successfully selected as expected.")

        driver.quit()

    def test_gender_submit_form_without_gender_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill in first and last names, but leave gender unselected
        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hashim")

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if the submit button is enabled (shouldn't be clickable without gender selection)
        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if submit_button.is_enabled():
            log_error_to_csv(
                error_message="The submit button is clickable when gender field is unselected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The submit button is not clickable when gender field is unselected",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The submit button is clickable when gender field is unselected, test failed.")
        else:
            print("Test passed: The submit button is not clickable when gender field is unselected as expected.")

        driver.quit()

class TestHobbiesFormGroupValidation:

    def test_hobby_default_no_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        dropdown = driver.find_element(By.ID, "exampleFormControlSelect2")

        # Get all options within the dropdown
        options = dropdown.find_elements(By.TAG_NAME, 'option')

        # Capture form field values immediately after loading the page
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        if selected_options:
            log_error_to_csv(
                error_message=f"The {', '.join(selected_options)} option is pre-selected when the page loads.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="No options are selected when the page loads.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                f"The {', '.join(selected_options)} option is pre-selected when the page loads, test failed.")
        else:
            print("Test passed: No options are selected when the page loads as expected.")

        driver.quit()

    def test_hobby_multiple_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        sleep(3)
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Reading")
        sleep(3)

        # Capture form field values immediately after selecting hobbies
        get_fields_value(driver)

        if not driver.find_element(By.XPATH, '//*[@id="exampleFormControlSelect2"]/option[4]').is_selected():
            log_error_to_csv(
                error_message="Only one option can be selected at a time",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="More than one option can be selected at a time",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Only one option can be selected at a time, test failed.")
        else:
            print("Test passed: More than one option can be selected at a time as expected.")

        driver.quit()

    def test_hobby_selected_option_assertion(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        to_selected = driver.find_element(By.XPATH, '//*[@id="exampleFormControlSelect2"]/option[4]').text

        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")

        dropdown = driver.find_element(By.ID, "exampleFormControlSelect2")

        # Get all options within the dropdown
        options = dropdown.find_elements(By.TAG_NAME, 'option')

        # Capture form field values immediately after selecting hobbies
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        if not (to_selected == selected_options[0]):
            log_error_to_csv(
                error_message=f"{to_selected} option was chosen but '{', '.join(selected_options)}' option is selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"{to_selected} option should be selected as expected.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                f"{to_selected} option was chosen but '{', '.join(selected_options)}' option is selected, test failed.")
        else:
            print(
                f"'{to_selected}' option was chosen and '{', '.join(selected_options)}' option is successfully selected as expected.")

        driver.quit()

    def test_hobby_submit_form_without_hobby_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hashim")

        driver.find_element(By.ID, "inlineRadioMale").click()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if not submit_button.is_enabled():
            log_error_to_csv(
                error_message="The submit button is not clickable when hobby field is unselected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The submit button should not be clickable when hobby field is unselected",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The submit button is not clickable when hobby field is unselected, test failed.")
        else:
            print("Test passed: The submit button is clickable when hobby field is unselected as expected.")

        driver.quit()

class TestDepartmentDropDownValidation:

    def test_department_default_no_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        default_selection = driver.find_element(By.XPATH,
                                                '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[1]').text
        dropdown = driver.find_element(By.NAME, "department")

        # Get all options within the dropdown
        options = dropdown.find_elements(By.TAG_NAME, 'option')

        # Capture form field values immediately after loading the page
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        if not (default_selection == selected_options[0]):
            log_error_to_csv(
                error_message=f"The {', '.join(selected_options)} option is pre-selected when the page loads.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="No options are selected when the page loads.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                f"The {', '.join(selected_options)} option is pre-selected when the page loads, test failed.")
        else:
            print("Test passed: No options are selected when the page loads as expected.")

        driver.quit()

    def test_department_multiple_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Engineering")
        sleep(3)
        selector.select_by_visible_text("Accounting Office")
        sleep(3)

        # Capture form field values immediately after selecting departments
        get_fields_value(driver)

        if driver.find_element(By.XPATH,
                               '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[2]').is_selected():
            log_error_to_csv(
                error_message="More than one option can be selected at a time",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Only one option can be selected at a time.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("More than one option can be selected at a time, test failed.")
        else:
            print("Test passed: Only one option can be selected at a time as expected.")

        driver.quit()

    def test_department_selected_option_assertion(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        to_selected = driver.find_element(By.XPATH,
                                          '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[2]').text

        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Engineering")

        dropdown = driver.find_element(By.NAME, "department")

        # Get all options within the dropdown
        options = dropdown.find_elements(By.TAG_NAME, 'option')

        # Capture form field values immediately after selecting department
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        if not (to_selected == selected_options[0]):
            log_error_to_csv(
                error_message=f"'{to_selected}' option was chosen but '{', '.join(selected_options)}' option is selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"'{to_selected}' option should be selected as expected.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                f"'{to_selected}' option was chosen but '{', '.join(selected_options)}' option is selected, test failed.")
        else:
            print(
                f"'{to_selected}' option was chosen and '{', '.join(selected_options)}' option is successfully selected as expected.")

        driver.quit()

    def test_department_submit_form_without_selection(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hashim")
        driver.find_element(By.ID, "inlineRadioMale").click()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if submit_button.is_enabled():
            log_error_to_csv(
                error_message="The submit button is clickable when department field is unselected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The submit button should not be clickable when department field is unselected.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The submit button is clickable when department field is unselected, test failed.")
        else:
            print("Test passed: The submit button is not clickable when department field is unselected as expected.")

        driver.quit()

class TestUsernameValidation:

    def test_username_single_character(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("a")
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The username accepts a single character input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username doesn't accept a single character input",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The username accepts a single character input, test failed.")
        else:
            print("Test passed: The username doesn't accept a single character input as expected.")
        driver.quit()

    def test_username_min_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("ahmed12")  # Less than 8 chars and min username length is 8
        sleep(3)
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The username accepts a minimum length less than 8 characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username accepts a minimum length of 8 characters",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The username accepts a minimum length less than 8 characters, test failed.")
        else:
            print("Test passed: The username accepts a minimum length of 8 characters as expected.")
        driver.quit()

    def test_username_max_length(self):  # suppose the username can accept a max length of 30 characters
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys(
            "a123456789123456789123456789123")  # More than 30 chars and max username length is 30
        sleep(3)
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The username accepts a maximum length more than 30 characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username accepts a maximum length of 30 characters",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The username accepts a maximum length more than 30 characters, test failed.")
        else:
            print("Test passed: The username accepts a maximum length of 30 characters as expected.")
        driver.quit()

    def test_username_starting_with_a_number(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("1ahmed12")  # Must ensure username length is in range
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The username accepts starting with a number",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username doesn't accept starting with a number",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The username accepts starting with a number, test failed.")
        else:
            print("Test passed: The username doesn't accept starting with a number as expected.")
        driver.quit()

    def test_username_having_an_underscore(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("_ahmed_12")  # Ensure username length is in range
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed():
            log_error_to_csv(
                error_message="The username doesn't accept having an underscore",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username accepts having an underscore",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The username doesn't accept having an underscore, test failed.")
        else:
            print("Test passed: The username accepts having an underscore as expected.")
        driver.quit()

    def test_username_having_a_special_char_other_than_underscore(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("_ahmed&12")  # Ensure username length is in range
        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The username accepts having a special character other than an underscore",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The username doesn't accept having a special character other than an underscore",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                "The username accepts having a special character other than an underscore, test failed.")
        else:
            print(
                "Test passed: The username doesn't accept having a special character other than an underscore as expected.")
        driver.quit()

    def test_username_clearing_after_filling(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        username_field = driver.find_element(By.NAME, "user_name")
        username_field.send_keys("ahmed_123")
        get_fields_value(driver)

        sleep(2.0)

        for _ in range(len("ahmed_123")):  # Length of the string "ahmed_123"
            username_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        error_message = driver.find_element(By.XPATH, '/html/body/div/form/fieldset/div[6]/div/small[2]')
        error_message_text = error_message.get_attribute("textContent").strip()

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[2]').is_displayed()):
            log_error_to_csv(
                error_message=f"The '{error_message_text}' error message isn't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"The '{error_message_text}' error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(f"The '{error_message_text}' error message isn't displayed, test failed.")
        else:
            print(f"Test passed: The '{error_message_text}' error message is displayed as expected.")
        driver.quit()

    def test_username_submit_form_with_invalid_username(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_name").send_keys("a")
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if submit_button.is_enabled():
            log_error_to_csv(
                error_message="The submit button is clickable with invalid Username input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The submit button is not clickable with invalid Username input",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The submit button is clickable with invalid Username input, test failed.")
        else:
            print("Test passed: The submit button is not clickable with invalid Username input as expected.")
        driver.quit()

class TestPasswordValidation:

    def test_password_matching(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_password").send_keys("Password123")
        driver.find_element(By.NAME, "confirm_password").send_keys("Password123")
        get_fields_value(driver)
        sleep(2)

        if driver.find_element(By.CSS_SELECTOR,
                               '#contact_form > fieldset > div:nth-child(10) > div > div > i').is_displayed():
            print("Test passed: Matching passwords confirmed as expected.")
        else:
            log_error_to_csv(
                error_message="The passwords are matching but no confirmation message is displayed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Matching passwords confirmed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The passwords are matching but no confirmation message is displayed, test failed.")
        driver.quit()

    def test_password_non_matching(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_password").send_keys("Password123")
        driver.find_element(By.NAME, "confirm_password").send_keys("Password321")
        get_fields_value(driver)
        sleep(2)

        if driver.find_element(By.CSS_SELECTOR,
                               '#contact_form > fieldset > div:nth-child(10) > div > div > i').is_displayed():
            log_error_to_csv(
                error_message="The passwords are not matching but no error message is displayed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Non-matching passwords error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The passwords are not matching but no error message is displayed, test failed.")
        else:
            print("Test passed: Non-matching passwords error message is displayed as expected.")
        driver.quit()

    def test_password_minimum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "user_password").send_keys("Pass1")
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[1]').is_displayed():
            print("Test passed: Minimum length requirement error message is displayed as expected.")
        else:
            log_error_to_csv(
                error_message="Password less than required minimum length is accepted.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Minimum length requirement error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Password less than required minimum length is accepted, test failed.")
        driver.quit()

    def test_password_maximum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        long_password = "P" * 31  # Assuming max length is 30 characters
        driver.find_element(By.NAME, "user_password").send_keys(long_password)
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[1]').is_displayed():
            print("Test passed: Maximum length requirement error message is displayed as expected.")
        else:
            log_error_to_csv(
                error_message="Password more than required maximum length is accepted.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Maximum length requirement error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Password more than required maximum length is accepted, test failed.")
        driver.quit()

    def test_password_empty_fields(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hamed")
        driver.find_element(By.ID, "inlineRadioMale").click()
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(By.NAME, "user_name").send_keys("abdo1234")

        driver.find_element(By.NAME, "user_password").send_keys("")
        driver.find_element(By.NAME, "confirm_password").send_keys("")
        sleep(3)
        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")

        if not submit_button.is_enabled():
            print("Test passed: Submit button is disabled when password fields are empty as expected.")
        else:
            log_error_to_csv(
                error_message="Submit button is enabled with empty password fields.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Submit button should be disabled with empty password fields",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Submit button is enabled with empty password fields, test failed.")
        driver.quit()

    def test_password_clearing_after_filling(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        password_field = driver.find_element(By.NAME, "user_password")
        password_field.send_keys("Password123")

        confirm_password_field = driver.find_element(By.NAME, "confirm_password")
        confirm_password_field.send_keys("Password123")

        sleep(2.0)

        for _ in range(len("Password123")):  # length of the string "Password123"
            password_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        for _ in range(len("Password123")):  # length of the string "Password123"
            confirm_password_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        password_error_message = driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[2]')
        password_error_message_text = password_error_message.get_attribute("textContent").strip()

        confirm_password_error_message = driver.find_element(By.CSS_SELECTOR,
                                                             '#contact_form > fieldset > div:nth-child(10) > div > small:nth-child(3)')
        confirm_password_error_message_text = confirm_password_error_message.get_attribute("textContent").strip()

        get_fields_value(driver)

        if not (driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[2]').is_displayed() and
                driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[8]/div/small[2]').is_displayed()):
            log_error_to_csv(
                error_message="The '" + password_error_message_text + "' and '" + confirm_password_error_message_text + "' error messages aren't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The error messages are displayed as expected",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(
                "The '" + password_error_message_text + "' and '" + confirm_password_error_message_text + "' error messages aren't displayed, test failed.")
        else:
            print(
                "Test passed: The '" + password_error_message_text + "' and '" + confirm_password_error_message_text + "' error messages are displayed as expected.")
        driver.quit()

    def test_password_input_masking(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Get the current field types
        password_field_type = driver.find_element(By.NAME, "user_password").get_attribute("type")
        confirm_password_field_type = driver.find_element(By.NAME, "confirm_password").get_attribute("type")

        if password_field_type == "password" and confirm_password_field_type == "password":
            print("Test passed: Password fields are masked correctly.")
        else:
            log_error_to_csv(
                error_message="Password fields are not masked.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Password fields are masked",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Password fields are not masked, test failed.")
        driver.quit()

    def test_password_copy_paste_prevention(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        password_field = driver.find_element(By.NAME, "user_password")
        password_field.send_keys("Password123")
        sleep(1)

        password_field.send_keys(Keys.CONTROL, 'a')  # Select all
        sleep(0.5)
        password_field.send_keys(Keys.CONTROL, 'c')  # Copy
        sleep(0.5)
        password_field.clear()  # Clear the password field
        sleep(0.5)
        password_field.send_keys(Keys.CONTROL, 'v')  # Paste

        sleep(1)  # Allow some time to see if it works

        if password_field.get_attribute("value") == "":
            print("Test passed: Copy and paste are disabled in the password field as expected.")
        else:
            log_error_to_csv(
                error_message="Password was pasted into the password field.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Password field should not accept pasted input",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Password was pasted into the password field, test failed.")
        driver.quit()

class TestEmailValidation:

    def test_email_empty_field(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill the form directly
        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hamed")
        driver.find_element(By.ID, "inlineRadioMale").click()
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(By.NAME, "user_name").send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(By.NAME, "user_password").send_keys(user_password)
        driver.find_element(By.NAME, "confirm_password").send_keys(user_password)

        driver.find_element(By.NAME, "email").send_keys("")  # Email is empty

        # Call to get_fields_value after filling the form
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if not submit_button.is_enabled():
            print("Test passed: Submit button is disabled when email field is empty as expected.")
        else:
            log_error_to_csv(
                error_message="Submit button is enabled with an empty email field",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Submit button is disabled when email field is empty",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Submit button is enabled with an empty email field, test failed.")

        driver.quit()

    def test_email_invalid_format(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill the form
        driver.find_element(By.NAME, "email").send_keys("test@example@com")

        # Call to get_fields_value after filling the form
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[2]').is_displayed():
            print("Test passed: Invalid email format error message is displayed as expected.")
        else:
            log_error_to_csv(
                error_message="Invalid email format is accepted without error",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Invalid email format error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Invalid email format is accepted without error, test failed.")

        driver.quit()

    def test_email_valid_format(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill the form
        driver.find_element(By.NAME, "email").send_keys("test@example.com")

        # Call to get_fields_value after filling the form
        get_fields_value(driver)

        if not driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[2]').is_displayed():
            print("Test passed: Valid email is accepted as expected.")
        else:
            log_error_to_csv(
                error_message="Valid email is rejected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Valid email is accepted",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Valid email is rejected, test failed.")

        driver.quit()

    def test_email_input_type(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Check email field type
        email_field_type = driver.find_element(By.NAME, "email").get_attribute("type")

        # Call to get_fields_value after filling the form
        get_fields_value(driver)

        if email_field_type == "email":
            print(f"Test passed: E-mail field type is correct as expected. Email field type is: '{email_field_type}'.")
        else:
            log_error_to_csv(
                error_message=f"E-mail field input type is in-correct. E-mail field type is '{email_field_type}'",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"E-mail field type is '{email_field_type}'",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(f"E-mail field input type is '{email_field_type}', test failed.")

        driver.quit()

    def test_email_clearing_after_filling(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        email_field = driver.find_element(By.NAME, "email")
        email_field.send_keys("test@example.com")
        get_fields_value(driver)

        sleep(2.0)

        for _ in range(len("test@example.com")):
            email_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        email_error_message = driver.find_element(By.XPATH,'//*[@id="contact_form"]/fieldset/div[9]/div/small[1]')
        email_error_message_text = email_error_message.get_attribute("textContent").strip()

        if not (driver.find_element(By.XPATH,'//*[@id="contact_form"]/fieldset/div[9]/div/small[1]').is_displayed()):
            log_error_to_csv(
                error_message="The '"     + email_error_message_text + "' error message isn't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="The '"   + email_error_message_text + "' error message is displayed",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("The '" + email_error_message_text + "' error message isn't displayed, test failed.")
        else:
            print("Test passed: The '"   + email_error_message_text + "' error message is displayed as expected.")
        driver.quit()

class TestContactNumberValidation: #Mandatory Field

    def test_contact_number_empty_field(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill form fields
        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hamed")
        driver.find_element(By.ID, "inlineRadioMale").click()
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(By.NAME, "user_name").send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(By.NAME, "user_password").send_keys(user_password)
        driver.find_element(By.NAME, "confirm_password").send_keys(user_password)
        driver.find_element(By.NAME, "email").send_keys("test@example.com")

        driver.find_element(By.NAME, "contact_no").send_keys("")

        # Get field values after filling the form
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")
        if not submit_button.is_enabled():
            print("Test passed: Submit button is disabled when contact number field is empty as expected.")
        else:
            log_error_to_csv(
                "Submit button is enabled with an empty contact number field.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Submit button is disabled when contact number field is empty.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Submit button is enabled with an empty contact number field, test failed.")
        driver.quit()

    def test_contact_number_invalid_format(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill contact number with invalid format
        driver.find_element(By.NAME, "contact_no").send_keys("abc12345621!")

        # Get field values after filling the form
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').is_displayed():
            print("Test passed: Invalid contact number format error message is displayed as expected.")
        else:
            log_error_to_csv(
                "Invalid contact number format is accepted without error.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Invalid contact number format error message is displayed.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Invalid contact number format is accepted without error, test failed.")
        driver.quit()

    def test_contact_number_valid_format(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill contact number with valid format
        driver.find_element(By.NAME, "contact_no").send_keys("201056789123")

        # Get field values after filling the form
        get_fields_value(driver)

        if not driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').is_displayed():
            print("Test passed: Valid contact number is accepted as expected.")
        else:
            log_error_to_csv(
                "Valid contact number is rejected.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Valid contact number is accepted.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Valid contact number is rejected, test failed.")
        driver.quit()

    def test_contact_number_input_type(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Check contact number field type
        contact_no_field_type = driver.find_element(By.NAME, "contact_no").get_attribute("type")

        # Get field values after filling the form
        get_fields_value(driver)

        if contact_no_field_type == "tel":
            print(
                f"Test passed: Contact number field input type is correct as expected. Contact number field type is: '{contact_no_field_type}'.")
        else:
            log_error_to_csv(
                f"Contact number field input type is incorrect. Contact number field type is '{contact_no_field_type}' and must be 'tel'.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Contact number field input type is 'tel'.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(f"Contact number field input type is '{contact_no_field_type}', test failed.")
        driver.quit()

    def test_contact_number_clearing_after_filling(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill the contact number field
        contact_no_field = driver.find_element(By.NAME, "contact_no")
        contact_no_field.send_keys("201056789123")

        # Get field values after filling the form
        get_fields_value(driver)

        sleep(2.0)

        # Clear the contact number field
        for _ in range(len("201056789123")):
            contact_no_field.send_keys(Keys.BACKSPACE)
            sleep(0.2)

        contact_no_error_message_text = "Please enter your Contact No."

        if driver.find_element(By.CSS_SELECTOR,
                               '#contact_form > fieldset > div.form-group.has-feedback.has-success > div > div > i').is_displayed():
            log_error_to_csv(
                f"The '{contact_no_error_message_text}' error message isn't displayed.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result=f"The '{contact_no_error_message_text}' error message is displayed.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError(f"The '{contact_no_error_message_text}' error message isn't displayed, test failed.")
        else:
            print(f"Test passed: The '{contact_no_error_message_text}' error message is displayed as expected.")
        driver.quit()

    def test_contact_number_minimum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill contact number with less than 12 characters
        driver.find_element(By.NAME, "contact_no").send_keys("2010567891")
        error_message = driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').text

        # Get field values after filling the form
        get_fields_value(driver)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').is_displayed():
            print(
                f"Test passed: '{error_message}' error message is displayed for contact number shorter than 12 characters as expected.")
        else:
            log_error_to_csv(
                "Contact number shorter than 12 characters is accepted without error.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Error message for contact number shorter than 12 characters is displayed.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Contact number shorter than 12 characters is accepted without error, test failed.")
        driver.quit()

    def test_contact_number_maximum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Fill contact number with more than 12 characters
        driver.find_element(By.NAME, "contact_no").send_keys("20105678912345")
        error_message = driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').text

        # Get field values after filling the form
        get_fields_value(driver)

        sleep(3)

        if driver.find_element(By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small').is_displayed():
            print(
                f"Test passed: '{error_message}' error message is displayed for contact number longer than 12 characters as expected.")
        else:
            log_error_to_csv(
                "Contact number longer than 12 characters is accepted without error.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Error message for contact number longer than 12 characters is displayed.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Contact number longer than 12 characters is accepted without error, test failed.")
        driver.quit()

class TestAdditionalInfoField:

    def test_additional_info_minimum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        additional_info_field.send_keys("A")  # Assuming 'A' is the minimum character for the field

        # Get field values after filling the form
        get_fields_value(driver)

        if len(additional_info_field.get_attribute('value')) >= 1:
            print("Test passed: Minimum length accepted as expected.")
        else:
            log_error_to_csv(
                "Minimum length is not enforced.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Minimum length should be accepted.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Test failed: Minimum length is not accepted.")
        driver.quit()

    def test_additional_info_maximum_length(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        max_length_text = "A" * 501  # Assuming max length is 500 characters
        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        additional_info_field.send_keys(max_length_text)

        # Get field values after filling the form
        get_fields_value(driver)

        if len(additional_info_field.get_attribute('value')) <= 500:
            print("Test passed: Maximum length restriction works as expected.")
        else:
            log_error_to_csv(
                "Maximum length restriction failed.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Maximum length should be enforced at 500 characters.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Test failed: Maximum length restriction is not enforced.")
        driver.quit()

    def test_additional_info_empty_field_submission(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        # Filling other required fields
        driver.find_element(By.NAME, "first_name").send_keys("Ahmed")
        driver.find_element(By.NAME, "last_name").send_keys("Hamed")
        driver.find_element(By.ID, "inlineRadioMale").click()
        selector = Select(driver.find_element(By.ID, "exampleFormControlSelect2"))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(By.NAME, "department"))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(By.NAME, "user_name").send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(By.NAME, "user_password").send_keys(user_password)
        driver.find_element(By.NAME, "confirm_password").send_keys(user_password)
        driver.find_element(By.NAME, "email").send_keys("joker@aaa.com")
        driver.find_element(By.NAME, "contact_no").send_keys("201015421458")

        driver.find_element(By.ID, "exampleFormControlTextarea1").send_keys("")  # Leaving Additional Info empty

        # Get field values after filling the form
        get_fields_value(driver)

        submit_button = driver.find_element(By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")

        if submit_button.is_enabled():
            print("Test passed: Submit button is enabled when Additional Info. field is empty as expected.")
        else:
            log_error_to_csv(
                "Submit button is disabled when Additional Info. field is empty.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": ""
                },
                expected_result="Submit button should be enabled when Additional Info. field is empty.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Submit button is disabled when Additional Info. field is empty.")
        driver.quit()

    def test_additional_info_input_format(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        special_characters = "!@#$%^&*()_+-={}[]:\";'<>?,./\\"
        additional_info_field.send_keys(special_characters)

        # Get field values after filling the form
        get_fields_value(driver)

        if additional_info_field.get_attribute('value') == special_characters:
            print("Test passed: Special characters are accepted as expected.")
        else:
            log_error_to_csv(
                "Special characters are not accepted.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Special characters should be accepted.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Test failed: Special characters are not accepted.")
        driver.quit()

    def test_additional_info_copy_paste_functionality(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        additional_info_field.send_keys("Test Content")

        # Simulate copying and pasting
        additional_info_field.send_keys(Keys.CONTROL, 'a')
        sleep(2)
        additional_info_field.send_keys(Keys.CONTROL, 'c')
        sleep(2)
        additional_info_field.send_keys(Keys.ARROW_RIGHT)
        sleep(2)
        additional_info_field.send_keys(Keys.CONTROL, 'v')
        sleep(2)

        # Get field values after copying and pasting
        get_fields_value(driver)

        if additional_info_field.get_attribute("value").count("Test Content") == 2:  # Should contain the pasted content twice
            print("Test passed: Copy-paste functionality works as expected.")
        else:
            log_error_to_csv(
                "Copy-paste functionality failed.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Copy-paste functionality should work.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Copy-paste functionality is not working.")
        driver.quit()

    def test_additional_info_truncation(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        long_text = "A" * 600  # Assuming the limit is 500 characters
        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        additional_info_field.send_keys(long_text)

        # Get field values after filling the form
        get_fields_value(driver)

        if len(additional_info_field.get_attribute("value")) == 500:  # Verify truncation to 500 chars
            print("Test passed: Input is truncated correctly after reaching max length as expected.")
        else:
            log_error_to_csv(
                "Truncation not enforced.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Input should be truncated to 500 characters.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Input truncation is not working.")
        driver.quit()

    def test_additional_info_field_resizing(self):
        driver = initialize_driver()
        driver.get("https://mytestingthoughts.com/Sample/home.html")
        bypass_ssl_warnings(driver)

        long_text = "A" * 500  # Fill the field with some text to test resizing
        additional_info_field = driver.find_element(By.XPATH, '//*[@id="exampleFormControlTextarea1"]')
        additional_info_field.send_keys(long_text)

        # Simulate resizing the field
        sleep(2)
        driver.execute_script("arguments[0].style.height = '500px';", additional_info_field)
        sleep(2)

        # Get field values after filling the form
        get_fields_value(driver)

        height = additional_info_field.get_attribute('style')

        if 'height: 500px' in height:
            print("Test passed: Text area resizes as expected.")
        else:
            log_error_to_csv(
                "Text area resizing failed.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "hobbies": selected_hobbies,
                    "department_office": department,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password,
                    "email": email,
                    "contact_no": contact_no,
                    "additional_info": additional_info
                },
                expected_result="Text area should resize as per the change.",
                platform="Web - Chrome"
            )
            driver.quit()
            raise AssertionError("Text area resizing is not working.")
        driver.quit()
