import time

import pytest
import docker
from selenium import webdriver
from docker.models.containers import Container
from _pytest.fixtures import SubRequest
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


IMAGE_NAME = 'gitea/gitea:1.15.2'


@pytest.fixture(scope="session")
def docker_container() -> Container:
    client = docker.from_env()
    client.images.pull(IMAGE_NAME)
    container: Container = client.containers.run(
        IMAGE_NAME,
        name='test-gitea',
        ports={'3000/tcp': 3000},
        detach=True)
    container.reload()
    time.sleep(1)
    yield container

    container.stop()
    container.remove()


@pytest.fixture(scope="class")
def driver_init(request: SubRequest, docker_container: Container) -> None:
    driver = webdriver.Chrome()

    request.cls.driver = driver
    yield
    driver.quit()


@pytest.mark.usefixtures("driver_init")
class TestGitea:
    driver: webdriver.Chrome

    def test_webpage_available(self):
        target_text = 'Installation - Gitea: Git with a cup of tea'
        target_selectors = ['a', '*', 'p']

        self.driver.get("http://localhost:3000/")
        assert self.driver.execute_script("return document.readyState") == 'complete'
        assert self.driver.title == target_text

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for s in target_selectors:
            assert len(soup.select(s)) >= 1

    def test_register_new_user(self):

        target_username = 'foo'
        user_password = 'bar'
        user_email = 'example@mail.com'

        self.driver.get("http://localhost:3000/")

        admin_section_name = "/html/body/div/div/div/div/div/form/details[3]"
        login_section = self.driver.find_element(By.XPATH, admin_section_name)
        ActionChains(self.driver).move_to_element(login_section).click(login_section).perform()

        input_username = self.driver.find_element(By.NAME, "admin_name")
        ActionChains(self.driver).move_to_element(input_username).click(input_username).perform()
        input_username.send_keys(target_username)

        input_email = self.driver.find_element(By.NAME, "admin_passwd")
        input_email.send_keys(user_password)

        input_password = self.driver.find_element(By.NAME, "admin_confirm_passwd")
        input_password.send_keys(user_password)

        input_confirm_password = self.driver.find_element(By.NAME, "admin_email")
        input_confirm_password.send_keys(user_email)

        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Install Gitea')]").click()
        time.sleep(5)
        self.driver.refresh()
        time.sleep(5)

        assert self.driver.find_element(By.CLASS_NAME, "truncated-item-name").text == target_username

    def test_create_new_repo(self):
        new_repo_button = "/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/h4/a"
        name = "new_template"

        self.driver.find_element(By.XPATH, f"{new_repo_button}").click()
        repo_name = self.driver.find_element(By.NAME, "repo_name")
        repo_name.send_keys(name)
        init_repo = "/html/body/div/div[2]/div/div/form/div/div[7]/div[6]"
        self.driver.find_element(By.XPATH, init_repo).click()
        self.driver.find_element(By.CLASS_NAME, 'ui.green.button').click()

        assert self.driver.current_url == "http://localhost:3000/foo/{}".format(name)

    def test_commit_file(self):
        new_file = "/html/body/div/div[2]/div[2]/div[5]/div[3]/div/a[1]"
        self.driver.find_element(By.XPATH, new_file).click()

        input_file_name = "/html/body/div[1]/div[2]/div[2]/form/div[1]/div/div/input[1]"
        file_name = "file.txt"
        file_text = "The file was created"
        self.driver.find_element(By.XPATH, input_file_name).send_keys(file_name)
        input_file_text = "/html/body/div[1]/div[2]/div[2]/form/div[2]/div[2]/div/div/div[1]/textarea"
        self.driver.find_element(By.XPATH, input_file_text).send_keys(file_text)
        self.driver.find_element(By.CSS_SELECTOR, 'button.ui.green.button').click()

        target_url = "http://localhost:3000/foo/new_template/src/branch/master/{}".format(file_name)
        assert self.driver.current_url == target_url

    def test_verify_file_contents(self) -> None:
        self.driver.get("http://localhost:3000/")

        my_repo = "/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div[2]/ul/li/a"
        self.driver.find_element(By.XPATH, my_repo).click()

        file_name = "/html/body/div/div[2]/div[2]/table/tbody/tr[2]/td[1]/span/a"
        self.driver.find_element(By.XPATH, file_name).click()

        file_text = "/html/body/div/div[2]/div[2]/div[6]/div/div/table/tbody/tr/td[2]/code"
        assert self.driver.find_element(By.XPATH, file_text).text == "The file was created"
