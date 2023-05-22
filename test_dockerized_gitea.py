import time

import pytest
import docker
import requests
from selenium import webdriver
from docker.models.containers import Container
from _pytest.fixtures import SubRequest
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


IMAGE_NAME = 'gitea/gitea:1.15.2'
PORT = 3000
URL = "http://localhost:{}/".format(PORT)


@pytest.fixture(scope="session")
def docker_container() -> Container:
    """
    Launching Docker container with Gitea image and checking if the container is running and responding to requests
    before returning it. The container is stopped and removed after fixture has been used.
    """

    client = docker.from_env()
    client.images.pull(IMAGE_NAME)
    container: Container = client.containers.run(
        IMAGE_NAME,
        name='test-gitea',
        ports={'3000/tcp': PORT},
        detach=True)

    while True:
        container.reload()
        log = container.logs().decode('utf-8')
        if 'Server listening on' in log and container.status == 'running':
            if requests.get(URL).status_code == 200:
                break
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
    user_name = 'foo'
    user_password = 'bar'
    user_email = 'example@mail.com'
    repo_name = 'repo'
    file_name = 'file.txt'
    file_content = 'The file was created'
    url_commit_file = f"{URL}{user_name}/{repo_name}/src/branch/master/{file_name}"

    def test_webpage_available(self):
        target_text = 'Installation - Gitea: Git with a cup of tea'
        target_selectors = ['a', '*', 'p']

        self.driver.get(URL)
        assert self.driver.execute_script("return document.readyState") == 'complete'
        assert self.driver.title == target_text

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for s in target_selectors:
            assert len(soup.select(s)) >= 1

    def test_register_new_user(self):
        self.driver.get(URL)

        login_section = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Administrator Account Settings')]")
        login_section.click()

        input_username = self.driver.find_element(By.NAME, "admin_name")
        input_username.click()
        input_username.send_keys(self.user_name)

        input_email = self.driver.find_element(By.NAME, "admin_passwd")
        input_email.send_keys(self.user_password)

        input_password = self.driver.find_element(By.NAME, "admin_confirm_passwd")
        input_password.send_keys(self.user_password)

        input_confirm_password = self.driver.find_element(By.NAME, "admin_email")
        input_confirm_password.send_keys(self.user_email)

        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Install Gitea')]").click()

        # TODO: investigate 'page is not working'
        # after the registartion the webpage with the message above sometimes appears
        # to fix it we need to reload the webpage

        time.sleep(5)
        self.driver.refresh()

        assert self.driver.find_element(By.XPATH, "//span[@class='truncated-item-name']").text == self.user_name

    def test_create_new_repo(self):
        self.driver.find_element(By.XPATH, "//a[@class='poping up']").click()
        repo_name = self.driver.find_element(By.NAME, "repo_name")
        repo_name.send_keys(self.repo_name)

        init_repo = "/html/body/div/div[2]/div/div/form/div/div[7]/div[6]"

        self.driver.find_element(By.XPATH, "//div[@id='auto-init']").click()

        self.driver.find_element(By.CLASS_NAME, 'ui.green.button').click()

        assert self.driver.current_url == f"{URL}{self.user_name}/{self.repo_name}"

    def test_commit_file(self):
        self.driver.find_element(By.XPATH, "//a[@class='ui button']").click()

        self.driver.find_element(By.ID, "file-name").send_keys(self.file_name)
        self.driver.find_element(
            By.XPATH,
            "//textarea[@class='inputarea monaco-mouse-cursor-text']"
        ).send_keys(self.file_content)
        self.driver.find_element(By.CSS_SELECTOR, 'button.ui.green.button').click()

        assert self.driver.current_url == self.url_commit_file

    def test_verify_file_contents(self) -> None:
        self.driver.get(URL)

        self.driver.find_element(By.XPATH, "//a[@class='repo-list-link df ac sb']").click()
        self.driver.find_element(By.XPATH, f"//a[@title='{self.file_name}']").click()

        assert self.driver.find_element(By.XPATH, "//code[@class='code-inner']").text == self.file_content
