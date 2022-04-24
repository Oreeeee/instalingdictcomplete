from selenium import webdriver
from time import sleep
import json
import os

# Initialize webdriver
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("-headless")
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


def start_session(session_count, word_delay, imported_dictionary):
    done_sessions = 0
    while done_sessions < session_count:
        # Start session loop
        driver.implicitly_wait(5)
        driver.find_element_by_class_name("btn-session").click()
        driver.implicitly_wait(5)
        try:
            driver.find_element_by_id("start_session_button").click()
        except:
            driver.find_element_by_id("continue_session_button").click()

        # Start a new session
        while True:
            # Check if session is done
            try:
                driver.find_element_by_id("return_mainpage").click()
                sleep(.5)
                break
            except:
                pass

            # Find answer field and submit the answer
            polish_word = driver.find_element_by_class_name("translations").text
            usage_example = driver.find_element_by_class_name("usage_example").text
            print(f"Slowo: {polish_word}, Przyklad uzycia: {usage_example}")
            answer_field = driver.find_element_by_id("answer")
            try:
                answer_field.send_keys(imported_dictionary[usage_example])
            except:
                pass

            sleep(word_delay)

            driver.find_element_by_id("check").click()
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
                    imported_dictionary[usage_example] = english_word
                except:
                    try:
                        driver.find_element_by_class_name("blue")
                        print("Literowka/Synonim")
                    except:
                        pass

            driver.find_element_by_id("nextword").click()

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
        word_delay = int(input("Jakie ma byc opoznienie pomiedzy slowami? (sek.): "))
        dictionary_file = input("Z jakiego pliku slownika skorzystac?: ")
        imported_dictionary = import_dictionary(dictionary_file)
        imported_dictionary = start_session(session_count, word_delay, imported_dictionary)
        save_dictionary(dictionary_file, imported_dictionary)


if __name__ == '__main__':
    main()
