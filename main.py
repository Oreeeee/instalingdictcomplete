from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SeleniumEx
from json.decoder import JSONDecodeError
from time import sleep
import json
import os
import platform
import random

# Detect OS
user_os = platform.system()

# Initialize webdriver
firefox_options = webdriver.FirefoxOptions()
firefox_profile = webdriver.FirefoxProfile()
firefox_options.add_argument("-headless")
firefox_profile.set_preference("media.volume_scale", "0.0")
if user_os == "Windows":
    firefox_binary = FirefoxBinary(
        r"C:\Program Files\Mozilla Firefox\firefox.exe")
    driver = webdriver.Firefox(firefox_binary=firefox_binary,
                               options=firefox_options, firefox_profile=firefox_profile)
else:
    driver = webdriver.Firefox(
        options=firefox_options, firefox_profile=firefox_profile)


def import_dictionary(dictionary_file):
    imported_dictionary = json.load(open(dictionary_file))
    return imported_dictionary


def save_dictionary(dictionary_file, imported_dictionary):
    j = json.dumps(imported_dictionary)
    with open(dictionary_file, "w") as f:
        f.write(j)


def generate_delay(min_delay=0.1, max_delay=0.1):
    sleep(round(random.uniform(min_delay, max_delay), 3))


def instaling_login(login, password):
    driver.get("https://instaling.pl/teacher.php?page=login")
    driver.implicitly_wait(5)
    driver.find_element(By.ID, "log_email").send_keys(login)
    driver.find_element(By.ID, "log_password").send_keys(password)
    driver.find_element(By.CLASS_NAME, "mb-3").click()

    driver.implicitly_wait(5)

    if driver.current_url == "https://instaling.pl/teacher.php?page=login":
        return False
    else:
        return True


def start_session(session_count, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, dictionary_file, random_fail_percentage):
    done_sessions = 0
    fail_on_purpose = False
    while done_sessions < session_count:
        try:
            imported_dictionary = import_dictionary(
                dictionary_file)  # Load dictionary
        except FileNotFoundError:
            print("Podany plik słownika nie istnieje!")
            exit()
        except JSONDecodeError:
            print("Plik słownika jest uszkodzony!")
            exit()

        # Start session loop
        sleep(.5)
        driver.find_element(By.CLASS_NAME, "btn-session").click()
        sleep(.5)
        while True:
            try:
                try:
                    driver.find_element(By.ID, "start_session_button").click()
                    break
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    driver.find_element(
                        By.ID, "continue_session_button").click()
                    break
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                pass

        sleep(1)

        # Start a new session
        while True:
            # Check if session is done
            try:
                driver.find_element(By.ID, "return_mainpage").click()
                break
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                pass

            # Find answer field and submit the answer
            while True:
                polish_word = driver.find_element(
                    By.CLASS_NAME, "translations").text
                usage_example = driver.find_element(
                    By.CLASS_NAME, "usage_example").text

                if polish_word == "" or usage_example == "":
                    print("Nie wykryto słówka")
                else:
                    break

            print(f"Słowo: {polish_word}, Przykład użycia: {usage_example}")
            answer_field = driver.find_element(By.ID, "answer")

            generate_delay(min_delay=min_worddelay, max_delay=max_worddelay)

            # Fail on purpose
            if random.randint(1, 100) <= random_fail_percentage:
                try:
                    english_word = imported_dictionary[usage_example]
                    for letter in english_word:
                        generate_delay(min_delay=min_letterdelay,
                                       max_delay=max_letterdelay)
                        answer_field.send_keys(letter)
                except Exception:
                    pass

                fail_on_purpose == False

            else:
                print("Celowy brak odpowiedzi")
                fail_on_purpose == True

            while True:
                try:
                    driver.find_element(By.ID, "check").click()
                    break
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    print(
                        "Nie można sprawdzić odpowiedzi. Możliwy problem z InstaLingiem, internetem lub skryptem.")

            sleep(.5)
            # Check result
            try:
                driver.find_element(By.CLASS_NAME, "green")
                print("Poprawna odpowiedź")
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                try:
                    driver.find_element(By.CLASS_NAME, "red")
                    print("Niepoprawna odpowiedź")
                    english_word = driver.find_element(By.ID, "word").text
                    print(f"Poprawna odpowiedź: {english_word}")

                    # Only add correct answer to dictionary when not failed on purpose
                    if fail_on_purpose == False:
                        imported_dictionary[usage_example] = english_word
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    try:
                        driver.find_element(By.CLASS_NAME, "blue")
                        print("Literowka/Synonim")
                    except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                        print("Nie udało się znaleźć wyniku odpowiedzi.")

            while True:
                try:
                    driver.find_element(By.ID, "nextword").click()
                    break
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    print(
                        "Nie można sprawdzić odpowiedzi. Możliwy problem z InstaLingiem, internetem lub skryptem.")

            sleep(.25)

        try:
            # Save dictionary
            save_dictionary(dictionary_file, imported_dictionary)
        except FileNotFoundError:
            print("Podany słownik nie istnieje! Ignorowanie błędu.")
            pass

        done_sessions += 1
    return imported_dictionary


if __name__ == '__main__':
    german_alphabet = "äöüßÄÖÜ"

    # Log into the website
    while True:
        login = input("Podaj login do konta ucznia: ")
        password = input("Podaj hasło: ")
        if instaling_login(login, password) == True:
            print("Zalogowano!")
            driver.implicitly_wait(5)
            break
        else:
            print("Nie udało się zalogować!")

    while True:
        session_count = int(input("Ile sesji wykonać?: "))

        min_letterdelay = float(
            input("Podaj minimalne opóźnienie pomiędzy literami: "))
        max_letterdelay = float(
            input("Podaj maksymalne opóźnienie pomiędzy literami: "))

        min_worddelay = float(
            input("Podaj minimalne opóźnienie pomiędzy słowami: "))
        max_worddelay = float(
            input("Podaj maksymalne opóźnienie pomiędzy słowami: "))

        random_fail_percentage = int(
            input("Ile procent odpowiedzi ma być poprawnych?: "))

        dictionary_file = input("Z jakiego pliku słownika skorzystać?: ")
        start_session(session_count, min_letterdelay, max_letterdelay,
                      min_worddelay, max_worddelay, dictionary_file, random_fail_percentage)
