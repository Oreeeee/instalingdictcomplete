from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SeleniumEx
from json.decoder import JSONDecodeError
from time import sleep
import platform
import requests
import random
import json

SCRIPT_VERSION = 14

def import_dictionary(dictionary_file):
    try:
        imported_dictionary = json.load(open(dictionary_file))
    except FileNotFoundError:
        print("Podany plik słownika nie istnieje!")
        exit()
    except JSONDecodeError:
        print("Plik słownika jest uszkodzony!")
        exit()
    return imported_dictionary


def save_dictionary(dictionary_file, imported_dictionary):
    j = json.dumps(imported_dictionary, indent=4)
    with open(dictionary_file, "w") as f:
        f.write(j)


def generate_delay(min_delay=0.1, max_delay=0.1):
    sleep(round(random.uniform(min_delay, max_delay), 3))


class InstalingAPI:

    def login(self, login, password):
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

    def do_sessions(self, session_count, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, random_fail_percentage, dictionary_file=None):
        for session in range(session_count):
            # Load dictionary
            if dictionary_file != None:
                imported_dictionary = import_dictionary(dictionary_file)

            # Start session
            self.start_session()

            # Session loop
            while True:
                usage_example = self.find_word()
                fail_on_purpose = self.submit_answer(
                    usage_example, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, random_fail_percentage, imported_dictionary)
                answer_result = self.check_answer()
                if type(answer_result) == str:
                    if fail_on_purpose == False:
                        self.add_word_to_dictionary(
                            usage_example, answer_result[1], dictionary_file, imported_dictionary)
                if self.is_session_done() == True:
                    break
                else:
                    self.next_word()

    def start_session(self):
        driver.find_element(By.CLASS_NAME, "btn-session").click()
        sleep(.5)
        while True:
            try:
                try:
                    driver.find_element(
                        By.ID, "start_session_button").click()
                    break
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    driver.find_element(
                        By.ID, "continue_session_button").click()
                    break
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                pass

    def find_word(self):
        while True:
            polish_word = driver.find_element(
                By.CLASS_NAME, "translations").text
            usage_example = driver.find_element(
                By.CLASS_NAME, "usage_example").text

            if polish_word == "" or usage_example == "":
                print("Nie wykryto słówka")
            else:
                break

        print(
            f"Słowo: {polish_word}, Przykład użycia: {usage_example}")

        return usage_example

    def submit_answer(self, usage_example, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, random_fail_percentage, imported_dictionary):
        generate_delay(min_delay=min_worddelay, max_delay=max_worddelay)

        fail_on_purpose = False
        answer_field = driver.find_element(By.ID, "answer")
        # Fail on purpose
        if random.randint(1, 100) <= random_fail_percentage:
            english_word = imported_dictionary[usage_example]
            for letter in english_word:
                generate_delay(min_delay=min_letterdelay,
                               max_delay=max_letterdelay)
                answer_field.send_keys(letter)

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

        return fail_on_purpose

    def check_answer(self):
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

                return english_word
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                try:
                    driver.find_element(By.CLASS_NAME, "blue")
                    print("Literowka/Synonim")
                except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                    print("Nie udało się znaleźć wyniku odpowiedzi.")

    def add_word_to_dictionary(self, usage_example, english_word, dictionary_file, imported_dictionary):
        imported_dictionary[usage_example] = english_word
        save_dictionary(dictionary_file, imported_dictionary)

    def next_word(self):
        while True:
            try:
                driver.find_element(By.ID, "nextword").click()
                break
            except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
                print(
                    "Nie można sprawdzić odpowiedzi. Możliwy problem z InstaLingiem, internetem lub skryptem.")

    def is_session_done(self):
        try:
            driver.find_element(By.ID, "return_mainpage").click()
            return True
        except (SeleniumEx.ElementNotInteractableException, SeleniumEx.NoSuchElementException):
            return False


def check_for_updates():
    if requests.get("https://raw.githubusercontent.com/Oreeeee/instalingdictcomplete/master/current_version.txt").text > SCRIPT_VERSION:
        print("Nowsza wersja skryptu jest dostępna! Pobierz ją z https://github.com/Oreeeee/instalingdictcomplete/releases")

def initialize_driver():
    global driver

    # Detect OS
    user_os = platform.system()

    # Initialize webdriver
    firefox_options = webdriver.FirefoxOptions()
    firefox_profile = webdriver.FirefoxProfile()
    # firefox_options.add_argument("-headless")
    firefox_profile.set_preference("media.volume_scale", "0.0")
    if user_os == "Windows":
        firefox_binary = FirefoxBinary(
            r"C:\Program Files\Mozilla Firefox\firefox.exe")
        driver = webdriver.Firefox(firefox_binary=firefox_binary,
                                   options=firefox_options, firefox_profile=firefox_profile)
    else:
        driver = webdriver.Firefox(
            options=firefox_options, firefox_profile=firefox_profile)


def instaling_login_form(instaling):
    # Log into the website
    while True:
        login = input("Podaj login do konta ucznia: ")
        password = input("Podaj hasło: ")

        if instaling.login(login, password) == True:
            print("Zalogowano!")
            driver.implicitly_wait(5)
            break
        else:
            print("Nie udało się zalogować!")


def main():
    check_for_updates()

    initialize_driver()

    # Initialize Instaling class
    instaling = InstalingAPI()

    # Log in
    instaling_login_form(instaling)

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

        instaling.do_sessions(session_count, min_letterdelay, max_letterdelay,
                              min_worddelay, max_worddelay, random_fail_percentage, dictionary_file=dictionary_file)


if __name__ == '__main__':
    main()
