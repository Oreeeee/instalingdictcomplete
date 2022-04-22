from selenium import webdriver

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


def main():
    while True:
        login = input("Podaj login do konta ucznia: ")
        password = input("Podaj haslo: ")
        if instaling_login(login, password) == True:
            print("Zalogowano!")
            break
        else:
            print("Nie udalo sie zalogowac!")


if __name__ == '__main__':
    main()
