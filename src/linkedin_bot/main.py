from __future__ import annotations

from typing import List

from pylenium.driver import Pylenium
from pylenium.config import PyleniumConfig

import json
from pathlib import Path
from rich import print
import sys
from time import sleep
from textwrap import dedent
import yaml

import os


from constants import DEFAULT_COOKIES_FPATH, PYLENIUM_CONFIG_YAML_FPATH, logger
from messaged_people import MessagedPerson, load_messaged_people
from pages import InvitationManager, Login


def read_pylenium_config() -> PyleniumConfig:
    config_txt: str = PYLENIUM_CONFIG_YAML_FPATH.read_text()
    config_json: dict = yaml.safe_load(config_txt)
    return PyleniumConfig(**config_json)


def save_cookies(py: Pylenium, cookies_fpath: Path = DEFAULT_COOKIES_FPATH):
    logger.info(f"Saving cookies to {str(cookies_fpath)}.")
    cookies = py.webdriver.get_cookies()
    with open(cookies_fpath, "w") as file:
        json.dump(cookies, file, indent=4)


def load_cookies(py: Pylenium, cookies_fpath: Path = DEFAULT_COOKIES_FPATH) -> bool:
    """Return whether cookies were loaded."""
    if not cookies_fpath.exists():
        logger.warning(f"No file found at {str(cookies_fpath)}. Skipping loading cookies.")
        return False
    
    logger.info(f"Loading cookies from {str(cookies_fpath)}.")
    logger.info("Navigating to linkedin.com so we can set cookies.")
    py.visit("https://www.linkedin.com")

    # parse the cookies from the json array file
    cookies: List[dict] = json.loads(cookies_fpath.read_text())

    # add each linkedin cookie to the webdriver
    for cookie in cookies:
        if "linkedin.com" in cookie["domain"]:
            logger.debug(f"Adding cookie for {cookie}")
            py.webdriver.add_cookie(cookie)

    return True


def make_pylenium() -> Pylenium:
    logger.info("Initializing pylenium...")
    config: PyleniumConfig = read_pylenium_config()
    py = Pylenium(config)
    return py

def login(py: Pylenium):
    login_page = Login(py=py)
        
    logger.info("Navigating to login page")
    login_page.init()
    sleep(1.5)

    logger.info("Logging in...")
    login_page.login(
        username=os.environ["LINKEDIN_EMAIL"], 
        password=os.environ["LINKEDIN_PASSWORD"]
    )
    sleep(1.5)

def main():
    py: Pylenium = make_pylenium()
    
    # log in if we haven't already
    if not load_cookies(py=py):
        login(py=py)

    # save our logged in session
    save_cookies(py=py)

    # find people to skip
    p: MessagedPerson
    names_to_skip = [p.name.lower().strip() for p in load_messaged_people()]
    
    invitation_manager_page = InvitationManager(py=py)
    invitation_manager_page.init()
    invitation_manager_page.message_people(skip_names=names_to_skip)


    


if __name__ == "__main__":
    main()