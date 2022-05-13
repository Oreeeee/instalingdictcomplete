from json.decoder import JSONDecodeError
import requests
import random
import json
import time
import os
import re


def import_dictionary(dictionary_file):
    imported_dictionary = json.load(open(dictionary_file))
    return imported_dictionary


def save_dictionary(dictionary_file, imported_dictionary):
    os.remove(dictionary_file)
    j = json.dumps(imported_dictionary)
    with(open(dictionary_file, "w")) as f:
        f.write(j)


def generate_delay(delay_type, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay):
    if delay_type == "letter":
        delay = round(random.uniform(min_letterdelay, max_letterdelay), 3)
    elif delay_type == "word":
        delay = round(random.uniform(min_worddelay, max_worddelay), 3)

    return delay


def instaling_login(login, password):
    instaling_login = requests_session.post("https://instaling.pl/teacher.php?page=teacherActions", data={
        "action": "login",
        "from": "",
        "log_email": login,
        "log_password": password,
    })

    print(instaling_login.text)

    # return instaling_login.cookies.get_dict()


def click_on_german_letter(letter):
    # This is an example of violation of DRY rule. Don't do this!
    letters = {
        "ä": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[2]').click()",
        "ö": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[3]').click()",
        "ü": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[4]').click()",
        "ß": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[5]').click()",
        "Ä": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[6]').click()",
        "Ö": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[7]').click()",
        "Ü": "driver.find_element(By.XPATH, '/html/body/div/div[8]/div[2]/div[2]/div[8]').click()"
    }

    exec(letters[letter])


def start_session(session_count, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, dictionary_file, random_fail_percentage):
    done_sessions = 0
    fail_on_purpose = False
    german_alphabet = "äöüßÄÖÜ"
    is_german = False
    checked_language = False
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
        if checked_language == False:
            try:
                driver.find_element(By.CLASS_NAME, "special_character_button")
                print("Wykryto jezyk niemiecki")
                is_german = True
                checked_language = True
            except Exception:
                print("Wykryto jezyk angielski")
                is_german = False
                checked_language = True

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
                        if letter in german_alphabet:
                            click_on_german_letter(letter)
                        else:
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
    requests_session = requests.Session()

    # Log into the website
    login = input("Podaj login do konta ucznia: ")
    password = input("Podaj hasło: ")
    instaling_login(login, password)

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
