from json.decoder import JSONDecodeError
from time import sleep
from urllib import response
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
    j = json.dumps(imported_dictionary, indent=4)
    with open(dictionary_file, "w") as f:
        f.write(j)


def generate_delay(min_delay=0.0, max_delay=0.0):
    sleep(round(random.uniform(min_delay, max_delay)))


def instaling_login(login, password):
    instaling_login = requests_session.post("https://instaling.pl/teacher.php?page=teacherActions", data={
        "action": "login",
        "from": "",
        "log_email": login,
        "log_password": password,
    }, headers=ua)

    # Search for UserID, sorry for my Regex skills
    try:
        instaling_id = re.findall(
            "\/ling2\/html_app\/app.php\?child_id=\d\d\d\d\d\d\d", instaling_login.text)
        instaling_id = instaling_id[0].strip(
            "/ling2/html_app/app.php?child_id=")
    except IndexError:
        return None

    login_data = []
    login_data.append(instaling_id)
    login_data.append(requests_session.cookies.get_dict())
    return login_data


def start_session(session_count, min_letterdelay, max_letterdelay, min_worddelay, max_worddelay, dictionary_file, random_fail_percentage):
    for session_number in range(session_count):
        # Import dictionary
        imported_dictionary = import_dictionary(dictionary_file)

        while True:
            # Reset answer variable
            word_answer = ""

            # Get next word
            instaling_word = requests.post("https://instaling.pl/ling2/server/actions/generate_next_word.php", data={
                "child_id": instaling_id,
                "date": time.time() * 1000
            }, headers=ua, cookies=instaling_cookies)

            polish_word = instaling_word.json()["translations"]
            usage_example = instaling_word.json()["usage_example"]
            word_id = instaling_word.json()["id"]

            print(
                f"Słowo: {polish_word}. Przykład użycia: {usage_example}. ID: {word_id}")

            # Don't submit answer if answer is marked as fail on purpose
            if random.randint(1, 100) <= random_fail_percentage:
                try:
                    english_word = imported_dictionary[usage_example]
                    for letter in english_word:
                        generate_delay(min_delay=min_letterdelay,
                                       max_delay=max_letterdelay)
                        word_answer = word_answer + letter
                except KeyError:
                    print("Nie znaleziono słowa w słowniku")
                    exit()

                fail_on_purpose = False
            else:
                print("Celowy brak odpowiedzi")
                fail_on_purpose = True

            # Submit answer
            instaling_answer = requests.post("https://instaling.pl/ling2/server/actions/save_answer.php", data={
                "child_id": instaling_id,
                "word_id": word_id,
                "answer": word_answer,
            }, headers=ua, cookies=instaling_cookies)

            english_word = instaling_answer.json()["word"]

            # Check if answer is correct
            try:
                if english_word == word_answer:
                    print("Poprawna odpowiedź.")
                else:
                    print(f"Niepoprawna odpowiedź. - Poprawna odpowiedź to: {english_word}")

                    if fail_on_purpose == False:
                        # Add word to dictionary
                        imported_dictionary[usage_example] = english_word
            except KeyError:
                # End session
                print(f"Zakończono sesję {session_number}")
                break

    # Save dictionary
    save_dictionary(dictionary_file, imported_dictionary)


if __name__ == '__main__':
    requests_session = requests.Session()

    ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }

    # Log into the website
    while True:
        login = input("Podaj login do konta ucznia: ")
        password = input("Podaj hasło: ")
        login_data = instaling_login(login, password)

        # Parse the data that instaling_login() returns
        if login_data == None:
            print("Nie udało się zalogować.")
        else:
            instaling_id = login_data[0]
            instaling_cookies = login_data[1]
            break

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
