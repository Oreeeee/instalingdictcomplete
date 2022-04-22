from selenium import webdriver
from time import sleep

# Initialize webdriver
driver = webdriver.Firefox()


def instaling_login(login, password):
    driver.get("https://instaling.pl/teacher.php?page=login")
    driver.implicitly_wait(5)
    driver.find_element_by_id("log_email").send_keys(login)
    driver.find_element_by_id("log_password").send_keys(password)
    driver.find_element_by_class_name("mb-3").click()

    driver.implicitly_wait(5)

    print(driver.current_url)

    if driver.current_url == "https://instaling.pl/teacher.php?page=login":
        return False
    else:
        return True


def start_session(word_count, session_count, word_delay):

    done_sessions = 0
    done_words = 0
    while done_sessions <= session_count:
        driver.find_element_by_class_name("btn-session").click()
        driver.implicitly_wait(5)
        try:
            driver.find_element_by_class_name("big_button").click()
        except:
            driver.find_element_by_id("continue_session_button").click()

        while done_words <= word_count:
            driver.find_element_by_id("answer").send_keys(input("Odpowiedz: "))
            driver.find_element_by_id("check").click()
            sleep(word_delay)
            try:
                driver.find_element_by_id("nextword").click()
            except:
                pass
            try:
                driver.find_element_by_id("return_mainpage").click()
            except:
                pass
            done_words += 1
    done_sessions += 1


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
        word_count = int(input("Ile slow ma sesja?: "))
        session_count = int(input("Ile sesji wykonac?: "))
        word_delay = int(input("Jakie ma byc opoznienie pomiedzy slowami? (sek.): "))
        # word_delay = 0  # Temp value
        start_session(word_count, session_count, word_delay)


if __name__ == '__main__':
    main()
