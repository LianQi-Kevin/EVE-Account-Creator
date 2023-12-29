import json
import logging
import os
import random
import string
import time
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def gen_password(length=13):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


def log_set(Log_level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(Log_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(Log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class AccountCreator(object):
    def __init__(self, YesCaptcha_path="YesCaptcha_Pro1.8", Log_level=logging.INFO, json_save_path="created_account"):
        """
        :param YesCaptcha_path: YesCaptcha plugin path
        :param Log_level: log display level
        :param json_save_path: Detailed json storage path
        """
        # chrome driver
        self.YesCaptcha_path = YesCaptcha_path
        self.driver = self._set_driver(headless=False)

        # set logging level
        log_set(Log_level=Log_level)

        # account json save
        self.json_path = json_save_path
        os.makedirs(self.json_path, exist_ok=True)

    # use undetected_chromedriver create driver
    def _set_driver(self, headless=False):
        assert os.path.exists(self.YesCaptcha_path), "YesCaptcha path not found"
        # Get abs path
        YesCaptcha_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.YesCaptcha_path)
        options = uc.ChromeOptions()
        # Load the captcha plugin
        options.add_argument('--load-extension={}'.format(YesCaptcha_path))
        # Disable password saving
        options.add_experimental_option("prefs", {"credentials_enable_service": False,
                                                  "profile.password_manager_enabled": False})
        return uc.Chrome(options=options, use_subprocess=True, advanced_elements=True, headless=headless)

    # json file
    def _create_json(self, signup_name, signup_pwd, signup_email):
        account_msg = dict(signup_name=signup_name, signup_pwd=signup_pwd, signup_email=signup_email)
        with open(os.path.join(self.json_path, "{}.json".format(signup_name)), "w") as json_f:
            json.dump(account_msg, json_f, indent=2, sort_keys=True, ensure_ascii=False)

    # txt log
    @staticmethod
    def _log_txt(mission_id, signup_name, signup_pwd, signup_email, status):
        with open(f"{mission_id}.txt", "a") as txt_f:
            txt_f.write(f"{signup_name} {signup_pwd} {signup_email} {status} \n")

    # account name creator
    @staticmethod
    def _name_creator(base_account):
        for index in range(300):
            yield "{}_{}".format(base_account, "%02d" % index)

    # create account
    def account_creator(self, signup_email, base_account=None, default_pwd=None, batch_num=5,
                        recruit_link="https://www.eveonline.com/signup?invc=816999af-7d4c-4075-ab8f-e2310dd302bd"):
        """
        :param signup_email: required field, The email that will be bound to the account.
        :param base_account: default None(random 10 chars).
        :param default_pwd: default None(random 13 chars).
        :param batch_num:
        :param recruit_link:
        """
        txt_mission_id = datetime.now().strftime("%y%m%d_%H%M%S")
        for i in range(batch_num):
            # open page
            self.driver.get(recruit_link)
            # create account name
            account_name = "{}_{}".format(gen_password(10) if base_account is None else base_account, "%02d" % i)
            # create password
            password = gen_password(13) if default_pwd is None else default_pwd
            # wait page load
            logging.info("loading page")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "signup-email")))

            # action
            self.driver.find_element(By.ID, "signup-email").send_keys(signup_email)
            self.driver.find_element(By.ID, "signup-username").send_keys(account_name)
            self.driver.find_element(By.ID, "signup-password").send_keys(password)
            self.driver.find_element(By.ID, "agree-terms").click()
            logging.info(f"signup-email: {signup_email}, signup-username: {account_name}, signup-password: {password}")
            time.sleep(1)
            # go reCaptcha
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            # verify signup_name availability
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div[class*="ErrorMsg_invalidFeedback"] > div'),
                                                     "Username is not available")
                )
                logging.warning(f"{account_name} is not available, jump over")
                self._log_txt(mission_id=txt_mission_id, signup_name=account_name, signup_pwd=password,
                              signup_email=signup_email, status="Not-Available")
            except:
                logging.info("Waiting recaptcha iframe")
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')))

                # wait Successful create
                logging.info("Waiting Successful page")
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Download_download__mKClU")))
                logging.info("Successful create account: {}".format(account_name))
                self._create_json(signup_name=account_name, signup_pwd=password, signup_email=signup_email)
                self._log_txt(mission_id=txt_mission_id, signup_name=account_name, signup_pwd=password,
                              signup_email=signup_email, status="Successful-Create")
                time.sleep(5)
