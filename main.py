from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from time import sleep
import json
import os
import platform
import random

# Detect OS
user_os = platform.system()

# Initialize webdriver
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("-headless")
if user_os == "Windows":
    firefox_binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")
    driver = webdriver.Firefox(firefox_binary=firefox_binary, options=firefox_options)
else:
    driver = webdriver.Firefox(options=firefox_options)


def import_dictionary(dictionary_file):
    imported_dictionary = json.load(open(dictionary_file))
    return imported_dictionary


def save_dictionary(dictionary_file, imported_dictionary):
    os.remove(dictionary_file)
    j = json.dumps(imported_dictionary)
    with(open(dictionary_file, "w")) as f:
        f.write(j)
        f.close()


def generate_delay(delay_type, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay):
    if delay_type == "letter":
        delay = round(random.uniform(min_letterdelay, max_letterdelay), 3)
    elif delay_type == "word":
        delay = round(random.uniform(min_worddelay, max_worddelay), 3)

    return delay


def instaling_login(login, password):
    driver.get("https://instaling.pl/teacher.php?page=login")
    driver.implicitly_wait(5)
    driver.find_element_by_id("log_email").send_keys(login)
    driver.find_element_by_id("log_password").send_keys(password)
    driver.find_element_by_class_name("mb-3").click()

    driver.implicitly_wait(5)

    if driver.current_url == "https://instaling.pl/teacher.php?page=login":
        return False
    else:
        return True


def start_session(session_count, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, dictionary_file, random_fail_percentage):
    done_sessions = 0
    fail_on_purpose = False
    while done_sessions < session_count:
        imported_dictionary = import_dictionary(dictionary_file)  # Load dictionary

        # Start session loop
        sleep(.5)
        driver.find_element_by_class_name("btn-session").click()
        sleep(.5)
        while True:
            try:
                try:
                    driver.find_element_by_id("start_session_button").click()
                    break
                except:
                    driver.find_element_by_id("continue_session_button").click()
                    break
            except:
                pass

        # Start a new session
        while True:
            # Check if session is done
            try:
                driver.find_element_by_id("return_mainpage").click()
                break
            except:
                pass

            # Find answer field and submit the answer
            polish_word = driver.find_element_by_class_name("translations").text
            usage_example = driver.find_element_by_class_name("usage_example").text
            print(f"Slowo: {polish_word}, Przyklad uzycia: {usage_example}")
            answer_field = driver.find_element_by_id("answer")

            delay_type = "word"
            sleep(generate_delay(delay_type, min_letterdelay,
                  max_letterdelay, min_worddelay, max_worddelay))

            # Fail on purpose
            if random.randint(1, 100) <= random_fail_percentage:
                try:
                    english_word = imported_dictionary[usage_example]
                    for letter in english_word:
                        delay_type = "letter"
                        sleep(generate_delay(delay_type, min_letterdelay,
                              max_letterdelay, min_worddelay, max_worddelay))
                        answer_field.send_keys(letter)
                except:
                    pass

                fail_on_purpose == False

            else:
                print("Celowy brak odpowiedzi")
                fail_on_purpose == True

            while True:
                try:
                    driver.find_element_by_id("check").click()
                    break
                except:
                    pass
            sleep(.5)
            # Check result
            try:
                driver.find_element_by_class_name("green")
                print("Poprawna odpowiedz")
            except:
                try:
                    driver.find_element_by_class_name("red")
                    print("Niepoprawna odpowiedz")
                    english_word = driver.find_element_by_id("word").text
                    print(f"Poprawna odpowiedz: {english_word}")

                    # Only add correct answer to dictionary when not failed on purpose
                    if fail_on_purpose == False:
                        imported_dictionary[usage_example] = english_word
                except:
                    try:
                        driver.find_element_by_class_name("blue")
                        print("Literowka/Synonim")
                    except:
                        pass

            while True:
                try:
                    driver.find_element_by_id("nextword").click()
                    break
                except:
                    pass

            sleep(.25)

        save_dictionary(dictionary_file, imported_dictionary)  # Save dictionary
        done_sessions += 1
    return imported_dictionary


def main():
    # Log into the website
    while True:
        login = input("Podaj login do konta ucznia: ")
        password = input("Podaj haslo: ")
        if instaling_login(login, password) == True:
            print("Zalogowano!")
            driver.implicitly_wait(5)
            break
        else:
            print("Nie udalo sie zalogowac!")

    while True:
        session_count = int(input("Ile sesji wykonac?: "))

        min_letterdelay = float(input("Podaj minimalne opoznienie pomiedzy literami: "))
        max_letterdelay = float(input("Podaj maksymalne opoznienie pomiedzy literami: "))

        min_worddelay = float(input("Podaj minimalne opoznienie pomiedzy slowami: "))
        max_worddelay = float(input("Podaj maksymalne opoznienie pomiedzy slowami: "))

        random_fail_percentage = int(input("Ile procent odpowiedzi ma byc poprawnych?: "))

        dictionary_file = input("Z jakiego pliku slownika skorzystac?: ")
        start_session(session_count, min_letterdelay, max_letterdelay,
                      min_worddelay, max_worddelay, dictionary_file, random_fail_percentage)


if __name__ == '__main__':
    main()
