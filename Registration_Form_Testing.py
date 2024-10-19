# Import necessary libraries and modules
import csv
import inspect
import os
import pytest
from pytest_selenium import driver
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

# Constants for file paths and selectors
ERROR_LOG_FILE = "error_log.csv"  # File where error logs will be saved


# Function to log errors to a CSV file for tracking
def log_error_to_csv(
    error_message, class_name, function_name, input_data, expected_result, platform
):
    file_path = ERROR_LOG_FILE
    error_count = 1

    # Use the error message as the Actual Result
    actual_result = error_message.strip()

    # Check if the file exists and determine the error number
    if os.path.exists(file_path):
        with open(file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) > 1:  # Check if file contains any errors
                last_row = rows[-1]
                # Extract the number from the last error number (Bug_x format)
                last_error_number = int(last_row[0].split("_")[1])
                error_count = last_error_number + 1

    # Append the error information to the CSV file
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write the header if it's the first error
        if error_count == 1:
            writer.writerow(
                [
                    "Error Number",
                    "Test Suite",
                    "Test Title",
                    "First Name",
                    "Last Name",
                    "Gender",
                    "Hobbies",
                    "Department / Office",
                    "Username",
                    "Password",
                    "Confirm Password",
                    "E-Mail",
                    "Contact No.",
                    "Additional Info",
                    "Expected Result",
                    "Actual Result",
                    "Platform",
                ]
            )
        # Write the error entry with "Bug_" prefix for the error number
        writer.writerow(
            [
                f"Bug_{error_count}",
                class_name,
                function_name,
                input_data.get("first_name"),
                input_data.get("last_name"),
                input_data.get("gender"),
                input_data.get("hobbies"),
                input_data.get("department_office"),
                input_data.get("username"),
                input_data.get("password"),
                input_data.get("confirm_password"),
                input_data.get("email"),
                input_data.get("contact_no"),
                input_data.get("additional_info"),
                expected_result,
                actual_result,
                platform,
            ]
        )

    print("Error logged to CSV")


# Fixture to initialize and manage WebDriver instance
@pytest.fixture(scope="class")
def driver():
    driver = webdriver.Chrome()  # Using Chrome WebDriver
    driver.maximize_window()  # Maximize window for better visibility
    yield driver
    driver.quit()  # Close the browser once done


# Fixture to navigate to the site before running tests
@pytest.fixture
def navigateToSite(driver):
    driver.get(
        "http://mytestingthoughts.com/Sample/home.html"
    )  # URL of the sample site


# Class to hold the form data values for retrieval
class FormData:
    """Class to hold form data."""

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


# To store success message text after form submission
result = ""


# Locators for form fields, using By for clear identification
class FormLocators:
    FIRST_NAME_FIELD = (By.NAME, "first_name")
    LAST_NAME_FIELD = (By.NAME, "last_name")
    Male_Radi_Button_Filed = (By.ID, "inlineRadioMale")
    Female_Radi_Button_Filed = (By.ID, "inlineRadioFemale")
    Hobbies_Field = (By.ID, "exampleFormControlSelect2")
    Hobbies_Field_Options = (By.TAG_NAME, "option")
    Department_Field = (By.NAME, "department")
    Username_Field = (By.NAME, "user_name")
    Password_Field = (By.NAME, "user_password")
    Confirm_Password_Field = (By.NAME, "confirm_password")
    Email_Field = (By.NAME, "email")
    Contact_No_Field = (By.NAME, "contact_no")
    Additional_Info_Field = (By.ID, "exampleFormControlTextarea1")
    Submit_Button = (By.XPATH, "/html/body/div[1]/form/fieldset/div[13]/div/button")


# Function to retrieve and save form field values into FormData class
def get_fields_value(driver):
    """Retrieve values from form fields."""
    # Retrieve text values from input fields
    FormData.first_name = driver.find_element(
        *FormLocators.FIRST_NAME_FIELD
    ).get_attribute("value")
    FormData.last_name = driver.find_element(
        *FormLocators.LAST_NAME_FIELD
    ).get_attribute("value")

    # Retrieve gender from selected radio buttons
    gender_male = driver.find_element(
        *FormLocators.Male_Radi_Button_Filed
    ).is_selected()
    gender_female = driver.find_element(
        *FormLocators.Female_Radi_Button_Filed
    ).is_selected()
    FormData.gender = "Male" if gender_male else "Female" if gender_female else ""

    # Retrieve hobbies from multi-select dropdown
    hobbies_element = driver.find_element(*FormLocators.Hobbies_Field)
    FormData.selected_hobbies = [
        option.text
        for option in hobbies_element.find_elements(*FormLocators.Hobbies_Field_Options)
        if option.is_selected()
    ]
    if not FormData.selected_hobbies:
        FormData.selected_hobbies = None

    # Retrieve selected department from dropdown
    department_element = Select(driver.find_element(*FormLocators.Department_Field))
    FormData.department = department_element.first_selected_option.text
    if FormData.department == "Select your Department/Office":
        FormData.department = None

    # Retrieve username and password values
    FormData.username = driver.find_element(*FormLocators.Username_Field).get_attribute(
        "value"
    )
    FormData.password = driver.find_element(*FormLocators.Password_Field).get_attribute(
        "value"
    )
    FormData.confirm_password = driver.find_element(
        *FormLocators.Confirm_Password_Field
    ).get_attribute("value")

    # Retrieve email, contact number, and additional info
    FormData.email = driver.find_element(*FormLocators.Email_Field).get_attribute(
        "value"
    )
    FormData.contact_no = driver.find_element(
        *FormLocators.Contact_No_Field
    ).get_attribute("value")
    FormData.additional_info = driver.find_element(
        *FormLocators.Additional_Info_Field
    ).get_attribute("value")


# Test class for form submission test cases
class TestFormSubmission:

    # Method to fill the form fields with test data
    @staticmethod
    def fill_form(driver):
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(
            *FormLocators.Male_Radi_Button_Filed
        ).click()  # Selecting gender
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")  # Selecting hobby
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text(
            "Department of Agriculture"
        )  # Selecting department
        driver.find_element(*FormLocators.Username_Field).send_keys("abdo1234")
        user_pass = "45454545"
        driver.find_element(*FormLocators.Password_Field).send_keys(user_pass)
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(user_pass)
        driver.find_element(*FormLocators.Email_Field).send_keys("joker@aaa.com")
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("201015421458")
        driver.find_element(*FormLocators.Additional_Info_Field).send_keys(
            "I'm a SW Tester :)"
        )

    # Method to validate the success message after submission
    @staticmethod
    def validate_success_message(driver):
        success_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "success_message"))
        )
        assert (
            "Success" in success_element.text
        ), f"Expected 'Success' but got: '{success_element.text}'"
        print(
            f"Form submitted successfully and '{success_element.text}' message validated."
        )
        return success_element.text

    # Test case for form submission when the form is empty
    def test_form_empty_form_submission(self, driver, navigateToSite):
        # Get current form field values
        get_fields_value(driver)

        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if submit_button.is_enabled():
            # Log error if the submit button is enabled when the form is empty
            log_error_to_csv(
                error_message="Form is empty but the submit button was enabled",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Submit button is disabled",
                platform="Web - Chrome",
            )
            raise AssertionError(
                "Form is empty but the submit button was enabled, test failed."
            )
        else:
            print("Test passed: Submit button is disabled as expected.")

    # Test case for filling and submitting the form
    def test_form_filling(self, driver, navigateToSite):
        global result
        try:
            driver.get("http://mytestingthoughts.com/Sample/home.html")
            self.fill_form(driver)
            # Get current form field values
            get_fields_value(driver)

            # Click on the submit button
            driver.find_element(*FormLocators.Submit_Button).click()
            result = self.validate_success_message(driver)

        except Exception as e:
            error_message = str(e)
            # Get current form field values
            get_fields_value(driver)
            # Log error if an exception occurs during form submission
            log_error_to_csv(
                error_message=error_message,
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"Form submitted successfully and '{result}' message is displayed",
                platform="Web - Chrome",
            )


# Class for input validation tests
class TestFirstAndLastNameValidation:  # Mandatory field validation for first and last name

    # Test case to verify that single-character inputs are not accepted
    def test_first_and_last_name_single_character(self, driver, navigateToSite):
        # Enter a single character in both first and last name fields
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("A")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("H")
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is displayed for both fields
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[1]'
            ).is_displayed()
            and driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the single character is accepted
            log_error_to_csv(
                error_message="The first and last name accepts a single character input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The first and last name don't accept a single character input",
                platform="Web - Chrome",
            )
            # Raise an assertion error if the test fails
            raise AssertionError(
                "The first and last name accepts a single character input, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The first and last name don't accept a single character input as expected."
            )

    # Test case to verify that numbers are not accepted in first and last names
    def test_first_and_last_name_has_a_number(self, driver, navigateToSite):
        # Enter names containing numbers
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("1Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hashim44")

        # Verify if the validation error message is displayed for both fields
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[1]'
            ).is_displayed()
            and driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[1]'
            ).is_displayed()
        ):
            # Get current form field values
            get_fields_value(driver)
            # Log error if numbers are accepted
            log_error_to_csv(
                error_message="The first and last name accept having a number",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The first and last name don't accept having a number",
                platform="Web - Chrome",
            )
            # Raise an assertion error if the test fails
            raise AssertionError(
                "The first and last name accept having a number, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The first and last name don't accept having a number as expected."
            )

    # Test case to verify the behavior when fields are cleared after being filled
    def test_first_and_last_name_clearing_after_filling(self, driver, navigateToSite):
        # Fill first and last name fields with valid data
        first_name_field = driver.find_element(*FormLocators.FIRST_NAME_FIELD)
        first_name_field.send_keys("Ahmed")
        last_name_field = driver.find_element(*FormLocators.LAST_NAME_FIELD)
        last_name_field.send_keys("Hashim")

        # Get current form field values
        get_fields_value(driver)

        # Clear the first and last name fields using backspace
        for _ in range(len("Ahmed")):
            first_name_field.send_keys(Keys.BACKSPACE)
        for _ in range(len("Hashim")):
            last_name_field.send_keys(Keys.BACKSPACE)

        # Capture error messages displayed after clearing the fields
        first_name_error_message = driver.find_element(
            By.XPATH, "/html/body/div/form/fieldset/div[1]/div/small[2]"
        )
        first_name_error_message_text = first_name_error_message.get_attribute(
            "textContent"
        ).strip()

        last_name_error_message = driver.find_element(
            By.CSS_SELECTOR,
            "#contact_form > fieldset > div:nth-child(4) > div > small:nth-child(3)",
        )
        last_name_error_message_text = last_name_error_message.get_attribute(
            "textContent"
        ).strip()

        # Check if both error messages are displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[2]'
            ).is_displayed()
            and driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[2]'
            ).is_displayed()
        ):
            # Log the error if validation messages aren't shown
            log_error_to_csv(
                error_message=f"The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages aren't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages are displayed",
                platform="Web - Chrome",
            )
            # Raise an assertion error if the test fails
            raise AssertionError(
                f"The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages aren't displayed, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                f"Test passed: The '{first_name_error_message_text}' and '{last_name_error_message_text}' error messages are displayed as expected."
            )

    # Test case to verify that special characters are not accepted
    def test_first_and_last_name_with_special_characters(self, driver, navigateToSite):
        # Fill in the first and last names with special characters
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("#Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hashim%")

        # Get current form field values
        get_fields_value(driver)

        # Verify if validation error messages are displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[1]/div/small[1]'
            ).is_displayed()
            and driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[2]/div/small[1]'
            ).is_displayed()
        ):
            # Log the error if special characters are accepted
            log_error_to_csv(
                error_message="The first and last name accept having special characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The first and last name don't accept having special characters",
                platform="Web - Chrome",
            )
            # Raise an assertion error if the test fails
            raise AssertionError(
                "The first and last name accept having special characters, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The first and last name don't accept having special characters as expected."
            )

    # Test case to verify form submission with invalid first and last name inputs
    def test_first_and_last_name_submit_form_with_invalid_data(
        self, driver, navigateToSite
    ):
        # Fill in the first and last names with invalid data (too short)
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("A")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("H")

        # Get current form field values
        get_fields_value(driver)

        # Check if the submit button is enabled (should not be clickable with invalid data)
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if not submit_button.is_enabled():
            # If the submit button is disabled, the test passes
            print(
                "Test passed: The form is not submitted with invalid first and last names."
            )
        else:
            # Log error if the form is submitted despite invalid data
            log_error_to_csv(
                error_message="The form accepts submitting invalid first and last names",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The form does not submit with invalid first and last names",
                platform="Web - Chrome",
            )
            # Raise an assertion error if the test fails
            raise AssertionError(
                "The form accepts submitting invalid first and last names, test failed."
            )


# Class for gender radio button validation tests
class TestGenderRadioButtonValidation:  # Mandatory

    def test_gender_no_option_is_selected_by_default(self, driver, navigateToSite):

        # Capture form field values immediately after opening the page
        get_fields_value(driver)

        # Check if any gender radio button is pre-selected
        if (
            driver.find_element(*FormLocators.Male_Radi_Button_Filed).is_selected()
            or driver.find_element(*FormLocators.Female_Radi_Button_Filed).is_selected()
        ):
            log_error_to_csv(
                error_message="The Male/Female radio button is pre-selected when the page loads",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The Male/Female radio button is not pre-selected when the page loads",
                platform="Web - Chrome",
            )

            raise AssertionError(
                "The Male/Female radio button is pre-selected when the page loads, test failed."
            )
        else:
            print(
                "Test passed: The Male/Female radio button is not pre-selected when the page loads as expected."
            )

    def test_gender_single_selection(self, driver, navigateToSite):

        # Select Male and then Female radio buttons
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        driver.find_element(*FormLocators.Female_Radi_Button_Filed).click()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if both options are selected (shouldn't be possible)
        if driver.find_element(*FormLocators.Male_Radi_Button_Filed).is_selected():
            log_error_to_csv(
                error_message="More than one option can be selected at a time",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Only one option can be selected at a time",
                platform="Web - Chrome",
            )

            raise AssertionError(
                "More than one option can be selected at a time, test failed."
            )
        else:
            print("Test passed: Only one option can be selected at a time as expected.")

    def test_gender_selected_option_assertion(self, driver, navigateToSite):

        # Select Male and then Female radio buttons
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        is_male_selected = driver.find_element(
            *FormLocators.Male_Radi_Button_Filed
        ).is_selected()
        driver.find_element(*FormLocators.Female_Radi_Button_Filed).click()
        is_female_selected = driver.find_element(
            *FormLocators.Female_Radi_Button_Filed
        ).is_selected()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if the selected options are asserted properly
        if not (is_male_selected and is_female_selected):
            log_error_to_csv(
                error_message="The Male/Female radio button is not successfully selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The Male/Female radio button is successfully selected",
                platform="Web - Chrome",
            )

            raise AssertionError(
                "The Male/Female radio button is not successfully selected, test failed."
            )
        else:
            print(
                "Test passed: The Male/Female radio button is successfully selected as expected."
            )

    def test_gender_submit_form_without_gender_selection(self, driver, navigateToSite):

        # Fill in first and last names, but leave gender unselected
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hashim")

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Check if the submit button is enabled (shouldn't be clickable without gender selection)
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if submit_button.is_enabled():
            log_error_to_csv(
                error_message="The submit button is clickable when gender field is unselected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The submit button is not clickable when gender field is unselected",
                platform="Web - Chrome",
            )

            raise AssertionError(
                "The submit button is clickable when gender field is unselected, test failed."
            )
        else:
            print(
                "Test passed: The submit button is not clickable when gender field is unselected as expected."
            )


# Class for hobbies form group validation tests
class TestHobbiesFormGroupValidation:

    # Test case to ensure no hobby options are pre-selected when the page loads
    def test_hobby_default_no_selection(self, driver, navigateToSite):
        # Locate the hobbies dropdown
        dropdown = driver.find_element(*FormLocators.Hobbies_Field)

        # Get all options within the dropdown
        options = dropdown.find_elements(*FormLocators.Hobbies_Field_Options)

        # Capture form field values immediately after loading the page
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        # Validate that no options are pre-selected when the page loads
        if selected_options:
            log_error_to_csv(
                error_message=f"The {', '.join(selected_options)} option is pre-selected when the page loads.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="No options are selected when the page loads.",
                platform="Web - Chrome",
            )
            # Raise an error if options are pre-selected
            raise AssertionError(
                f"The {', '.join(selected_options)} option is pre-selected when the page loads, test failed."
            )
        else:
            # Print success message if no options are selected
            print(
                "Test passed: No options are selected when the page loads as expected."
            )

    # Test case to ensure multiple hobby options can be selected simultaneously
    def test_hobby_multiple_selection(self, driver, navigateToSite):
        # Select multiple hobbies (Running and Reading)
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Reading")

        # Capture form field values immediately after selecting hobbies
        get_fields_value(driver)

        # Verify if multiple selections are allowed
        if not driver.find_element(
            By.XPATH, '//*[@id="exampleFormControlSelect2"]/option[4]'
        ).is_selected():
            # Log error if multiple selections aren't allowed
            log_error_to_csv(
                error_message="Only one option can be selected at a time",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="More than one option can be selected at a time",
                platform="Web - Chrome",
            )
            # Raise an error if the test fails
            raise AssertionError(
                "Only one option can be selected at a time, test failed."
            )
        else:
            # Print success message if multiple selections are allowed
            print(
                "Test passed: More than one option can be selected at a time as expected."
            )

    # Test case to validate that the selected hobby matches the one chosen by the user
    def test_hobby_selected_option_assertion(self, driver, navigateToSite):
        # Expected hobby to be selected
        to_selected = driver.find_element(
            By.XPATH, '//*[@id="exampleFormControlSelect2"]/option[4]'
        ).text

        # Select the hobby "Running"
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")

        # Locate the hobbies dropdown again
        dropdown = driver.find_element(*FormLocators.Hobbies_Field)

        # Get all options within the dropdown
        options = dropdown.find_elements(*FormLocators.Hobbies_Field_Options)

        # Capture form field values immediately after selecting hobbies
        get_fields_value(driver)

        # Check which options are selected
        selected_options = [option.text for option in options if option.is_selected()]

        # Assert that the selected option matches the expected option
        if not (to_selected == selected_options[0]):
            # Log error if the selected option does not match the chosen option
            log_error_to_csv(
                error_message=f"{to_selected} option was chosen but '{', '.join(selected_options)}' option is selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"{to_selected} option should be selected as expected.",
                platform="Web - Chrome",
            )
            # Raise an error if the test fails
            raise AssertionError(
                f"{to_selected} option was chosen but '{', '.join(selected_options)}' option is selected, test failed."
            )
        else:
            # Print success message if the selected option matches the chosen option
            print(
                f"'{to_selected}' option was chosen and '{', '.join(selected_options)}' option is successfully selected as expected."
            )

    # Test case to verify that the form cannot be submitted if no hobby is selected
    def test_hobby_submit_form_without_hobby_selection(self, driver, navigateToSite):
        # Fill in the first name, last name, and select gender, but leave hobbies unselected
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hashim")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Verify if the submit button is enabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if not submit_button.is_enabled():
            # Log error if the submit button is not clickable when hobbies are unselected
            log_error_to_csv(
                error_message="The submit button is not clickable when hobby field is unselected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The submit button should not be clickable when hobby field is unselected",
                platform="Web - Chrome",
            )
            # Raise an error if the test fails
            raise AssertionError(
                "The submit button is not clickable when hobby field is unselected, test failed."
            )
        else:
            # Print success message if the submit button is clickable as expected
            print(
                "Test passed: The submit button is not clickable when hobby field is unselected as expected."
            )


# Class for validating department dropdown functionality
class TestDepartmentDropDownValidation:

    # Test case to ensure no department options are pre-selected when the page loads
    def test_department_default_no_selection(self, driver, navigateToSite):
        # Locate the default selected option in the department dropdown
        default_selection = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[1]'
        ).text

        # Locate the department dropdown
        dropdown = driver.find_element(*FormLocators.Department_Field)

        # Get all options within the dropdown
        options = dropdown.find_elements(*FormLocators.Hobbies_Field_Options)

        # Capture form field values immediately after loading the page
        get_fields_value(driver)

        # Check which options are currently selected
        selected_options = [option.text for option in options if option.is_selected()]

        # Verify that the default selection matches the first selected option
        if not (default_selection == selected_options[0]):
            # Log error if the default selection is incorrect
            log_error_to_csv(
                error_message=f"The {', '.join(selected_options)} option is pre-selected when the page loads.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="No options are selected when the page loads.",
                platform="Web - Chrome",
            )

            # Raise an error if the default selection is not as expected
            raise AssertionError(
                f"The {', '.join(selected_options)} option is pre-selected when the page loads, test failed."
            )
        else:
            # Print success message if no options are pre-selected
            print(
                "Test passed: No options are selected when the page loads as expected."
            )

    # Test case to ensure multiple department options can be selected simultaneously
    def test_department_multiple_selection(self, driver, navigateToSite):
        # Select multiple departments (Department of Engineering and Accounting Office)
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Engineering")
        selector.select_by_visible_text("Accounting Office")

        # Capture form field values immediately after selecting departments
        get_fields_value(driver)

        # Verify if multiple selections are allowed by checking the second option
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[2]'
        ).is_selected():
            # Log error if more than one option can be selected
            log_error_to_csv(
                error_message="More than one option can be selected at a time.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Only one option can be selected at a time.",
                platform="Web - Chrome",
            )

            # Raise an error if multiple options are selected
            raise AssertionError(
                "More than one option can be selected at a time, test failed."
            )
        else:
            # Print success message if only one option can be selected
            print("Test passed: Only one option can be selected at a time as expected.")

    # Test case to validate that the selected department matches the one chosen by the user
    def test_department_selected_option_assertion(self, driver, navigateToSite):
        # Expected department to be selected
        to_selected = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[5]/div/div/select/option[2]'
        ).text

        # Select the department "Department of Engineering"
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Engineering")

        # Locate the department dropdown again
        dropdown = driver.find_element(*FormLocators.Department_Field)

        # Get all options within the dropdown
        options = dropdown.find_elements(*FormLocators.Hobbies_Field_Options)

        # Capture form field values immediately after selecting the department
        get_fields_value(driver)

        # Check which options are currently selected
        selected_options = [option.text for option in options if option.is_selected()]

        # Assert that the selected option matches the expected option
        if not (to_selected == selected_options[0]):
            # Log error if the selected option does not match the chosen option
            log_error_to_csv(
                error_message=f"'{to_selected}' option was chosen but '{', '.join(selected_options)}' option is selected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"'{to_selected}' option should be selected as expected.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                f"'{to_selected}' option was chosen but '{', '.join(selected_options)}' option is selected, test failed."
            )
        else:
            # Print success message if the selected option matches the chosen option
            print(
                f"'{to_selected}' option was chosen and '{', '.join(selected_options)}' option is successfully selected as expected."
            )

    # Test case to verify that the form cannot be submitted if no department is selected
    def test_department_submit_form_without_selection(self, driver, navigateToSite):
        # Fill in the first name, last name, and select gender, but leave department unselected
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hashim")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()

        # Capture form field values immediately after filling the form
        get_fields_value(driver)

        # Verify if the submit button is enabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if submit_button.is_enabled():
            # Log error if the submit button is clickable when department field is unselected
            log_error_to_csv(
                error_message="The submit button is clickable when department field is unselected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The submit button should not be clickable when department field is unselected.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "The submit button is clickable when department field is unselected, test failed."
            )
        else:
            # Print success message if the submit button is not clickable as expected
            print(
                "Test passed: The submit button is not clickable when department field is unselected as expected."
            )


# Class for validating Username field
class TestUsernameValidation:

    # Test case to verify that single-character usernames are not accepted
    def test_username_single_character(self, driver, navigateToSite):
        # Enter a single character in the username field
        driver.find_element(*FormLocators.Username_Field).send_keys("a")
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the single character is accepted
            log_error_to_csv(
                error_message="The username accepts a single character input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username doesn't accept a single character input",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The username accepts a single character input, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The username doesn't accept a single character input as expected."
            )

    # Test case to verify the minimum length requirement for usernames
    def test_username_min_length(self, driver, navigateToSite):
        # Enter a username shorter than the minimum length (8 characters)
        driver.find_element(*FormLocators.Username_Field).send_keys("ahmed12")
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the short username is accepted
            log_error_to_csv(
                error_message="The username accepts a minimum length less than 8 characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username accepts a minimum length of 8 characters",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The username accepts a minimum length less than 8 characters, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The username accepts a minimum length of 8 characters as expected."
            )

    # Test case to verify the maximum length requirement for usernames
    def test_username_max_length(self, driver, navigateToSite):
        # Enter a username longer than the maximum length (30 characters)
        driver.find_element(*FormLocators.Username_Field).send_keys(
            "a123456789123456789123456789123"
        )
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the long username is accepted
            log_error_to_csv(
                error_message="The username accepts a maximum length more than 30 characters",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username accepts a maximum length of 30 characters",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The username accepts a maximum length more than 30 characters, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The username accepts a maximum length of 30 characters as expected."
            )

    # Test case to verify that usernames starting with a number are not accepted
    def test_username_starting_with_a_number(self, driver, navigateToSite):
        # Enter a username starting with a number
        driver.find_element(*FormLocators.Username_Field).send_keys("1ahmed12")
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the username starting with a number is accepted
            log_error_to_csv(
                error_message="The username accepts starting with a number",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username doesn't accept starting with a number",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The username accepts starting with a number, test failed."
            )
        else:
            # Print success message if the validation works
            print(
                "Test passed: The username doesn't accept starting with a number as expected."
            )

    # Test case to verify that usernames can contain underscores
    def test_username_having_an_underscore(self, driver, navigateToSite):
        # Enter a username containing an underscore
        driver.find_element(*FormLocators.Username_Field).send_keys("_ahmed_12")
        # Get current form field values
        get_fields_value(driver)

        # Verify if the validation error message is not displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
        ).is_displayed():
            # Log error if the username with underscore is not accepted
            log_error_to_csv(
                error_message="The username doesn't accept having an underscore",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username accepts having an underscore",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The username doesn't accept having an underscore, test failed."
            )
        else:
            # Print success message if the validation works
            print("Test passed: The username accepts having an underscore as expected.")

    # Test case to verify that the username doesn't accept special characters other than underscore
    def test_username_having_a_special_char_other_than_underscore(
        self, driver, navigateToSite
    ):
        # Enter a username with a special character other than underscore
        driver.find_element(*FormLocators.Username_Field).send_keys("_ahmed&12")

        # Capture form field values after entering the username
        get_fields_value(driver)

        # Check if the error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[1]'
            ).is_displayed()
        ):
            # Log error if the username accepts a special character other than underscore
            log_error_to_csv(
                error_message="The username accepts having a special character other than an underscore",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The username doesn't accept having a special character other than an underscore",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "The username accepts having a special character other than an underscore, test failed."
            )
        else:
            # Print success message if the test passes
            print(
                "Test passed: The username doesn't accept having a special character other than an underscore as expected."
            )

    # Test case to verify the behavior when username field is cleared after filling
    def test_username_clearing_after_filling(self, driver, navigateToSite):
        # Enter a valid username
        username_field = driver.find_element(*FormLocators.Username_Field)
        username_field.send_keys("ahmed_123")

        # Capture form field values after entering the username
        get_fields_value(driver)

        # Clear the username field
        for _ in range(len("ahmed_123")):
            username_field.send_keys(Keys.BACKSPACE)

        # Get the error message text
        error_message = driver.find_element(
            By.XPATH, "/html/body/div/form/fieldset/div[6]/div/small[2]"
        )
        error_message_text = error_message.get_attribute("textContent").strip()

        # Check if the error message is displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[6]/div/small[2]'
            ).is_displayed()
        ):
            # Log error if the error message isn't displayed
            log_error_to_csv(
                error_message=f"The '{error_message_text}' error message isn't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"The '{error_message_text}' error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                f"The '{error_message_text}' error message isn't displayed, test failed."
            )
        else:
            # Print success message if the test passes
            print(
                f"Test passed: The '{error_message_text}' error message is displayed as expected."
            )

    # Test case to verify that the form cannot be submitted with an invalid username
    def test_username_submit_form_with_invalid_username(self, driver, navigateToSite):
        # Enter an invalid username
        driver.find_element(*FormLocators.Username_Field).send_keys("a")

        # Capture form field values after entering the username
        get_fields_value(driver)

        # Check if the submit button is enabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if submit_button.is_enabled():
            # Log error if the submit button is clickable with invalid username
            log_error_to_csv(
                error_message="The submit button is clickable with invalid Username input",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The submit button is not clickable with invalid Username input",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "The submit button is clickable with invalid Username input, test failed."
            )
        else:
            # Print success message if the test passes
            print(
                "Test passed: The submit button is not clickable with invalid Username input as expected."
            )


# Class for password validation tests
class TestPasswordValidation:

    # Test case to verify that passwords match
    def test_password_matching(self, driver, navigateToSite):
        # Enter matching passwords in both fields
        driver.find_element(*FormLocators.Password_Field).send_keys("Password123")
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(
            "Password123"
        )

        # Capture form field values
        get_fields_value(driver)

        # Check if the confirmation message is displayed
        if driver.find_element(
            By.CSS_SELECTOR,
            "#contact_form > fieldset > div:nth-child(10) > div > div > i",
        ).is_displayed():
            print("Test passed: Matching passwords confirmed as expected.")
        else:
            # Log error if confirmation message is not displayed
            log_error_to_csv(
                error_message="The passwords are matching but no confirmation message is displayed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Matching passwords confirmed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The passwords are matching but no confirmation message is displayed, test failed."
            )

    # Test case to verify that non-matching passwords are detected
    def test_password_non_matching(self, driver, navigateToSite):
        # Enter non-matching passwords
        driver.find_element(*FormLocators.Password_Field).send_keys("Password123")
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(
            "Password321"
        )

        # Capture form field values
        get_fields_value(driver)

        # Check if the error message is displayed for non-matching passwords
        if driver.find_element(
            By.CSS_SELECTOR,
            "#contact_form > fieldset > div:nth-child(10) > div > div > i",
        ).is_displayed():
            # Log error if no error message is displayed for non-matching passwords
            log_error_to_csv(
                error_message="The passwords are not matching but no error message is displayed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Non-matching passwords error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "The passwords are not matching but no error message is displayed, test failed."
            )
        else:
            print(
                "Test passed: Non-matching passwords error message is displayed as expected."
            )

    # Test case to verify minimum password length requirement
    def test_password_minimum_length(self, driver, navigateToSite):
        # Enter a password shorter than the minimum length
        driver.find_element(*FormLocators.Password_Field).send_keys("Pass1")

        # Capture form field values
        get_fields_value(driver)

        # Check if the error message for minimum length is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[1]'
        ).is_displayed():
            print(
                "Test passed: Minimum length requirement error message is displayed as expected."
            )
        else:
            # Log error if the minimum length requirement is not enforced
            log_error_to_csv(
                error_message="Password less than required minimum length is accepted.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Minimum length requirement error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Password less than required minimum length is accepted, test failed."
            )

    # Test case to verify maximum password length requirement
    def test_password_maximum_length(self, driver, navigateToSite):
        # Create a password longer than the maximum allowed length
        long_password = "P" * 31  # Assuming max length is 30 characters
        driver.find_element(*FormLocators.Password_Field).send_keys(long_password)

        # Capture form field values
        get_fields_value(driver)

        # Check if the error message for maximum length is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[1]'
        ).is_displayed():
            print(
                "Test passed: Maximum length requirement error message is displayed as expected."
            )
        else:
            # Log error if the maximum length requirement is not enforced
            log_error_to_csv(
                error_message="Password more than required maximum length is accepted.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Maximum length requirement error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Password more than required maximum length is accepted, test failed."
            )

    # Test case to verify form submission with empty password fields
    def test_password_empty_fields(self, driver, navigateToSite):
        # Fill in other form fields
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hamed")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(*FormLocators.Username_Field).send_keys("abdo1234")

        # Leave password fields empty
        driver.find_element(*FormLocators.Password_Field).send_keys("")
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys("")

        # Get current form field values
        get_fields_value(driver)

        # Locate the submit button
        submit_button = driver.find_element(*FormLocators.Submit_Button)

        # Check if the submit button is disabled
        if not submit_button.is_enabled():
            print(
                "Test passed: Submit button is disabled when password fields are empty as expected."
            )
        else:
            # Log error if the submit button is enabled with empty password fields
            log_error_to_csv(
                error_message="Submit button is enabled with empty password fields.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Submit button should be disabled with empty password fields",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Submit button is enabled with empty password fields, test failed."
            )

    # Test case to verify error messages when clearing password fields after filling
    def test_password_clearing_after_filling(self, driver, navigateToSite):
        # Fill in password fields
        password_field = driver.find_element(*FormLocators.Password_Field)
        password_field.send_keys("Password123")
        confirm_password_field = driver.find_element(
            *FormLocators.Confirm_Password_Field
        )
        confirm_password_field.send_keys("Password123")

        # Clear password fields
        for _ in range(len("Password123")):
            password_field.send_keys(Keys.BACKSPACE)
            confirm_password_field.send_keys(Keys.BACKSPACE)

        # Get error message elements
        password_error_message = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[2]'
        )
        confirm_password_error_message = driver.find_element(
            By.CSS_SELECTOR,
            "#contact_form > fieldset > div:nth-child(10) > div > small:nth-child(3)",
        )

        # Get error message texts
        password_error_message_text = password_error_message.get_attribute(
            "textContent"
        ).strip()
        confirm_password_error_message_text = (
            confirm_password_error_message.get_attribute("textContent").strip()
        )

        # Capture form field values
        get_fields_value(driver)

        # Check if both error messages are displayed
        if not (
            driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[7]/div/small[2]'
            ).is_displayed()
            and driver.find_element(
                By.XPATH, '//*[@id="contact_form"]/fieldset/div[8]/div/small[2]'
            ).is_displayed()
        ):
            # Log error if error messages are not displayed
            log_error_to_csv(
                error_message=f"The '{password_error_message_text}' and '{confirm_password_error_message_text}' error messages aren't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="The error messages are displayed as expected",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                f"The '{password_error_message_text}' and '{confirm_password_error_message_text}' error messages aren't displayed, test failed."
            )
        else:
            print(
                f"Test passed: The '{password_error_message_text}' and '{confirm_password_error_message_text}' error messages are displayed as expected."
            )

    # Test case to verify password input masking
    def test_password_input_masking(self, driver, navigateToSite):
        # Get the current field types
        password_field_type = driver.find_element(
            *FormLocators.Password_Field
        ).get_attribute("type")
        confirm_password_field_type = driver.find_element(
            *FormLocators.Confirm_Password_Field
        ).get_attribute("type")

        # Get current form field values
        get_fields_value(driver)

        # Check if both password fields are of type "password"
        if (
            password_field_type == "password"
            and confirm_password_field_type == "password"
        ):
            print("Test passed: Password fields are masked correctly.")
        else:
            # Log error if password fields are not masked
            log_error_to_csv(
                error_message="Password fields are not masked.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Password fields are masked",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError("Password fields are not masked, test failed.")

    # Test case to verify copy-paste prevention in password field
    def test_password_copy_paste_prevention(self, driver, navigateToSite):
        # Enter a password
        password_field = driver.find_element(*FormLocators.Password_Field)
        password_field.send_keys("Password123")

        # Get current form field values
        get_fields_value(driver)

        # Attempt to copy and paste the password
        password_field.send_keys(Keys.CONTROL, "a")  # Select all
        password_field.send_keys(Keys.CONTROL, "c")  # Copy
        password_field.clear()  # Clear the password field
        password_field.send_keys(Keys.CONTROL, "v")  # Paste

        # Check if the password field is empty after paste attempt
        if password_field.get_attribute("value") == "":
            print(
                "Test passed: Copy and paste are disabled in the password field as expected."
            )
        else:
            # Log error if copy-paste is allowed in the password field
            log_error_to_csv(
                error_message="Password was pasted into the password field.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Password field should not accept pasted input",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Password was pasted into the password field, test failed."
            )


# Class for email validation tests
class TestEmailValidation:

    # Test case to verify form submission with an empty email field
    def test_email_empty_field(self, driver, navigateToSite):
        # Fill in other required fields
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hamed")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")
        selector.select_by_visible_text("Reading")
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(*FormLocators.Username_Field).send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(*FormLocators.Password_Field).send_keys(user_password)
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(
            user_password
        )

        # Leave email field empty
        driver.find_element(*FormLocators.Email_Field).send_keys("")

        # Capture form field values
        get_fields_value(driver)

        # Check if submit button is disabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if not submit_button.is_enabled():
            print(
                "Test passed: Submit button is disabled when email field is empty as expected."
            )
        else:
            # Log error if submit button is enabled with empty email field
            log_error_to_csv(
                error_message="Submit button is enabled with an empty email field",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Submit button is disabled when email field is empty",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Submit button is enabled with an empty email field, test failed."
            )

    # Test case to verify rejection of invalid email format
    def test_email_invalid_format(self, driver, navigateToSite):
        # Enter an invalid email format
        driver.find_element(*FormLocators.Email_Field).send_keys("test@example@com")

        # Capture form field values
        get_fields_value(driver)

        # Check if error message for invalid email format is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[2]'
        ).is_displayed():
            print(
                "Test passed: Invalid email format error message is displayed as expected."
            )
        else:
            # Log error if invalid email format is accepted
            log_error_to_csv(
                error_message="Invalid email format is accepted without error",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Invalid email format error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Invalid email format is accepted without error, test failed."
            )

    # Test case to verify acceptance of valid email format
    def test_email_valid_format(self, driver, navigateToSite):
        # Enter a valid email format
        driver.find_element(*FormLocators.Email_Field).send_keys("test@example.com")

        # Capture form field values
        get_fields_value(driver)

        # Check if no error message is displayed for valid email
        if not driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[2]'
        ).is_displayed():
            print("Test passed: Valid email is accepted as expected.")
        else:
            # Log error if valid email is rejected
            log_error_to_csv(
                error_message="Valid email is rejected",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Valid email is accepted",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError("Valid email is rejected, test failed.")

    # Test case to verify correct input type for email field
    def test_email_input_type(self, driver, navigateToSite):
        # Get the input type of the email field
        email_field_type = driver.find_element(*FormLocators.Email_Field).get_attribute(
            "type"
        )

        # Capture form field values
        get_fields_value(driver)

        # Check if email field type is correct
        if email_field_type == "email":
            print(
                f"Test passed: E-mail field type is correct as expected. Email field type is: '{email_field_type}'."
            )
        else:
            # Log error if email field type is incorrect
            log_error_to_csv(
                error_message=f"E-mail field input type is incorrect. E-mail field type is '{email_field_type}'",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"E-mail field type is '{email_field_type}'",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                f"E-mail field input type is '{email_field_type}', test failed."
            )

    # Test case to verify error message when clearing email field after filling
    def test_email_clearing_after_filling(self, driver, navigateToSite):
        # Fill in the email field
        email_field = driver.find_element(*FormLocators.Email_Field)
        email_field.send_keys("test@example.com")

        # Capture form field values
        get_fields_value(driver)

        # Clear the email field
        for _ in range(len("test@example.com")):
            email_field.send_keys(Keys.BACKSPACE)

        # Get the error message element
        email_error_message = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[1]'
        )
        email_error_message_text = email_error_message.get_attribute(
            "textContent"
        ).strip()

        # Check if the error message is displayed
        if not driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[9]/div/small[1]'
        ).is_displayed():
            # Log error if error message is not displayed
            log_error_to_csv(
                error_message=f"The '{email_error_message_text}' error message isn't displayed",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"The '{email_error_message_text}' error message is displayed",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                f"The '{email_error_message_text}' error message isn't displayed, test failed."
            )
        else:
            print(
                f"Test passed: The '{email_error_message_text}' error message is displayed as expected."
            )


# Class for contact number validation tests
class TestContactNumberValidation:

    # Test case to verify form submission with an empty contact number field
    def test_contact_number_empty_field(self, driver, navigateToSite):
        # Fill in other required fields
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hamed")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(*FormLocators.Username_Field).send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(*FormLocators.Password_Field).send_keys(user_password)
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(
            user_password
        )
        driver.find_element(*FormLocators.Email_Field).send_keys("test@example.com")

        # Leave contact number field empty
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("")

        # Capture form field values
        get_fields_value(driver)

        # Check if submit button is disabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)
        if not submit_button.is_enabled():
            print(
                "Test passed: Submit button is disabled when contact number field is empty as expected."
            )
        else:
            # Log error if submit button is enabled with empty contact number field
            log_error_to_csv(
                error_message="Submit button is enabled with an empty contact number field",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Submit button is disabled when contact number field is empty",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Submit button is enabled with an empty contact number field, test failed."
            )

    # Test case to verify rejection of invalid contact number format
    def test_contact_number_invalid_format(self, driver, navigateToSite):
        # Enter an invalid contact number format
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("abc12345621!")

        # Capture form field values
        get_fields_value(driver)

        # Check if error message for invalid contact number format is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).is_displayed():
            print(
                "Test passed: Invalid contact number format error message is displayed as expected."
            )
        else:
            # Log error if invalid contact number format is accepted
            log_error_to_csv(
                error_message="Invalid contact number format is accepted without error.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Invalid contact number format error message is displayed.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Invalid contact number format is accepted without error, test failed."
            )

    # Test case to verify acceptance of valid contact number format
    def test_contact_number_valid_format(self, driver, navigateToSite):
        # Enter a valid contact number format
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("201056789123")

        # Capture form field values
        get_fields_value(driver)

        # Check if no error message is displayed for valid contact number
        if not driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).is_displayed():
            print("Test passed: Valid contact number is accepted as expected.")
        else:
            # Log error if valid contact number is rejected
            log_error_to_csv(
                error_message="Valid contact number is rejected.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Valid contact number is accepted.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError("Valid contact number is rejected, test failed.")

    # Test case to verify correct input type for contact number field
    def test_contact_number_input_type(self, driver, navigateToSite):
        # Get the input type of the contact number field
        contact_no_field_type = driver.find_element(
            *FormLocators.Contact_No_Field
        ).get_attribute("type")

        # Capture form field values
        get_fields_value(driver)

        # Check if contact number field type is correct
        if contact_no_field_type == "tel":
            print(
                f"Test passed: Contact number field input type is correct as expected. Contact number field type is: '{contact_no_field_type}'."
            )
        else:
            # Log error if contact number field type is incorrect
            log_error_to_csv(
                f"Contact number field input type is incorrect. Contact number field type is '{contact_no_field_type}' and must be 'tel'.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Contact number field input type is 'tel'.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                f"Contact number field input type is '{contact_no_field_type}', test failed."
            )

    # Test case to verify error message when clearing contact number field after filling
    def test_contact_number_clearing_after_filling(self, driver, navigateToSite):
        # Fill in the contact number field
        contact_no_field = driver.find_element(*FormLocators.Contact_No_Field)
        contact_no_field.send_keys("201056789123")

        # Capture form field values
        get_fields_value(driver)

        # Clear the contact number field
        for _ in range(len("201056789123")):
            contact_no_field.send_keys(Keys.BACKSPACE)

        # Check if the error message is displayed
        contact_no_error_message_text = "Please enter your Contact No."
        if driver.find_element(
            By.CSS_SELECTOR,
            "#contact_form > fieldset > div.form-group.has-feedback.has-success > div > div > i",
        ).is_displayed():
            # Log error if error message is not displayed
            log_error_to_csv(
                f"The '{contact_no_error_message_text}' error message isn't displayed.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result=f"The '{contact_no_error_message_text}' error message is displayed.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                f"The '{contact_no_error_message_text}' error message isn't displayed, test failed."
            )
        else:
            print(
                f"Test passed: The '{contact_no_error_message_text}' error message is displayed as expected."
            )

    # Test case to verify minimum length requirement for contact number
    def test_contact_number_minimum_length(self, driver, navigateToSite):
        # Enter a contact number shorter than the minimum length
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("2010567891")
        error_message = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).text

        # Capture form field values
        get_fields_value(driver)

        # Check if error message for minimum length is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).is_displayed():
            print(
                f"Test passed: '{error_message}' error message is displayed for contact number shorter than 12 characters as expected."
            )
        else:
            # Log error if contact number shorter than minimum length is accepted
            log_error_to_csv(
                "Contact number shorter than 12 characters is accepted without error.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Error message for contact number shorter than 12 characters is displayed.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Contact number shorter than 12 characters is accepted without error, test failed."
            )

    # Test case to verify maximum length requirement for contact number
    def test_contact_number_maximum_length(self, driver, navigateToSite):
        # Enter a contact number longer than the maximum length
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("20105678912345")
        error_message = driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).text

        # Capture form field values
        get_fields_value(driver)

        # Check if error message for maximum length is displayed
        if driver.find_element(
            By.XPATH, '//*[@id="contact_form"]/fieldset/div[10]/div/small'
        ).is_displayed():
            print(
                f"Test passed: '{error_message}' error message is displayed for contact number longer than 12 characters as expected."
            )
        else:
            # Log error if contact number longer than maximum length is accepted
            log_error_to_csv(
                "Contact number longer than 12 characters is accepted without error.",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Error message for contact number longer than 12 characters is displayed.",
                platform="Web - Chrome",
            )

            # Raise an assertion error if the test fails
            raise AssertionError(
                "Contact number longer than 12 characters is accepted without error, test failed."
            )


# Class for validating the Additional Info field functionality
class TestAdditionalInfoField:

    # Test case to verify the minimum length requirement for the Additional Info field
    def test_additional_info_minimum_length(self, driver, navigateToSite):
        # Locate the Additional Info field and enter a single character
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        additional_info_field.send_keys(
            "A"
        )  # Assuming 'A' is the minimum character for the field

        # Get field values after filling the form
        get_fields_value(driver)

        # Verify that the minimum length is accepted
        if len(additional_info_field.get_attribute("value")) >= 1:
            print("Test passed: Minimum length accepted as expected.")
        else:
            # Log error if minimum length is not enforced
            log_error_to_csv(
                error_message="Minimum length is not enforced.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Minimum length should be accepted.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError("Minimum length is not accepted, test failed.")

    # Test case to verify the maximum length restriction for the Additional Info field
    def test_additional_info_maximum_length(self, driver, navigateToSite):
        # Create a string of 501 'A' characters (assuming max length is 500)
        max_length_text = "A" * 501
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        additional_info_field.send_keys(max_length_text)

        # Get field values after filling the form
        get_fields_value(driver)

        # Verify that the maximum length restriction is enforced
        if len(additional_info_field.get_attribute("value")) <= 500:
            print("Test passed: Maximum length restriction works as expected.")
        else:
            # Log error if maximum length restriction failed
            log_error_to_csv(
                error_message="Maximum length restriction failed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Maximum length should be enforced at 500 characters.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "Maximum length restriction is not enforced, test failed."
            )

    # Test case to verify form submission with an empty Additional Info field
    def test_additional_info_empty_field_submission(self, driver, navigateToSite):
        # Fill in other required fields
        driver.find_element(*FormLocators.FIRST_NAME_FIELD).send_keys("Ahmed")
        driver.find_element(*FormLocators.LAST_NAME_FIELD).send_keys("Hamed")
        driver.find_element(*FormLocators.Male_Radi_Button_Filed).click()
        selector = Select(driver.find_element(*FormLocators.Hobbies_Field))
        selector.select_by_visible_text("Running")
        selector = Select(driver.find_element(*FormLocators.Department_Field))
        selector.select_by_visible_text("Department of Agriculture")
        driver.find_element(*FormLocators.Username_Field).send_keys("abdo1234")
        user_password = "45454545"
        driver.find_element(*FormLocators.Password_Field).send_keys(user_password)
        driver.find_element(*FormLocators.Confirm_Password_Field).send_keys(
            user_password
        )
        driver.find_element(*FormLocators.Email_Field).send_keys("joker@aaa.com")
        driver.find_element(*FormLocators.Contact_No_Field).send_keys("201015421458")

        # Leave Additional Info field empty
        driver.find_element(*FormLocators.Additional_Info_Field).send_keys("")

        # Get field values after filling the form
        get_fields_value(driver)

        # Check if the submit button is enabled
        submit_button = driver.find_element(*FormLocators.Submit_Button)

        if submit_button.is_enabled():
            print(
                "Test passed: Submit button is enabled when Additional Info. field is empty as expected."
            )
        else:
            # Log error if submit button is disabled
            log_error_to_csv(
                error_message="Submit button is disabled when Additional Info. field is empty.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Submit button should be enabled when Additional Info. field is empty.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "Submit button is disabled when Additional Info. field is empty, test failed."
            )

    # Test case to verify input format acceptance in the Additional Info field
    def test_additional_info_input_format(self, driver, navigateToSite):
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        special_characters = "!@#$%^&*()_+-={}[]:\";'<>?,./\\"
        additional_info_field.send_keys(special_characters)

        # Get field values after filling the form
        get_fields_value(driver)

        # Verify that special characters are accepted
        if additional_info_field.get_attribute("value") == special_characters:
            print("Test passed: Special characters are accepted as expected.")
        else:
            # Log error if special characters are not accepted
            log_error_to_csv(
                error_message="Special characters are not accepted.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Special characters should be accepted.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError("Special characters are not accepted, test failed.")

    # Test case to verify copy-paste functionality in the Additional Info field
    def test_additional_info_copy_paste_functionality(self, driver, navigateToSite):
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        additional_info_field.send_keys("Test Content")

        # Simulate copying and pasting
        additional_info_field.send_keys(Keys.CONTROL, "a")
        additional_info_field.send_keys(Keys.CONTROL, "c")
        additional_info_field.send_keys(Keys.ARROW_RIGHT)
        additional_info_field.send_keys(Keys.CONTROL, "v")

        # Get field values after copying and pasting
        get_fields_value(driver)

        # Verify that the content is pasted correctly
        if additional_info_field.get_attribute("value").count("Test Content") == 2:
            print("Test passed: Copy-paste functionality works as expected.")
        else:
            # Log error if copy-paste functionality failed
            log_error_to_csv(
                error_message="Copy-paste functionality failed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Copy-paste functionality should work.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError(
                "Copy-paste functionality is not working, test failed."
            )

    # Test case to verify input truncation in the Additional Info field
    def test_additional_info_truncation(self, driver, navigateToSite):
        long_text = "A" * 600  # Assuming the limit is 500 characters
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        additional_info_field.send_keys(long_text)

        # Get field values after filling the form
        get_fields_value(driver)

        # Verify that the input is truncated to 500 characters
        if len(additional_info_field.get_attribute("value")) == 500:
            print(
                "Test passed: Input is truncated correctly after reaching max length as expected."
            )
        else:
            # Log error if truncation is not enforced
            log_error_to_csv(
                error_message="Truncation not enforced.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Input should be truncated to 500 characters.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError("Input truncation is not working, test failed.")

    # Test case to verify field resizing functionality for the Additional Info field
    def test_additional_info_field_resizing(self, driver, navigateToSite):
        long_text = "A" * 500  # Fill the field with some text to test resizing
        additional_info_field = driver.find_element(*FormLocators.Additional_Info_Field)
        additional_info_field.send_keys(long_text)

        # Simulate resizing the field
        driver.execute_script(
            "arguments[0].style.height = '500px';", additional_info_field
        )

        # Get field values after filling the form
        get_fields_value(driver)

        # Check if the height attribute has been changed
        height = additional_info_field.get_attribute("style")

        if "height: 500px" in height:
            print("Test passed: Text area resizes as expected.")
        else:
            # Log error if text area resizing failed
            log_error_to_csv(
                error_message="Text area resizing failed.",
                class_name=self.__class__.__name__,
                function_name=inspect.currentframe().f_code.co_name,
                input_data={
                    "first_name": FormData.first_name,
                    "last_name": FormData.last_name,
                    "gender": FormData.gender,
                    "hobbies": FormData.selected_hobbies,
                    "department_office": FormData.department,
                    "username": FormData.username,
                    "password": FormData.password,
                    "confirm_password": FormData.confirm_password,
                    "email": FormData.email,
                    "contact_no": FormData.contact_no,
                    "additional_info": FormData.additional_info,
                },
                expected_result="Text area should resize as per the change.",
                platform="Web - Chrome",
            )

            # Raise an error if the test fails
            raise AssertionError("Text area resizing is not working, test failed.")
