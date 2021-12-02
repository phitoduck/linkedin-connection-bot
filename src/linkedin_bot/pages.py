from __future__ import annotations

from rich import print
from typing import List, Optional
from pylenium.driver import Pylenium
from pylenium.element import Element
from time import sleep
from selenium.common.exceptions import TimeoutException


from constants import logger, BOT_MESSAGE
from messaged_people import MessagedPerson, save_messaged_person


############################
# --- Helper Functions --- #
############################

def click_element(py: Pylenium, el: Element):
    py.scroll_to(x=el.webelement.location["x"], y=el.webelement.location["y"] - 150)
    el.hover()
    el.click()
    

def close_all_conversations(py: Pylenium):
    while close_far_left_conversation(py=py):
        ...

def close_far_left_conversation(py: Pylenium) -> bool:
    """Returns whether a conversation was closed."""
    logger.debug("Closing the far left conversation")
    all_close_buttons_selector = "header.msg-overlay-conversation-bubble--header:last-of-type > section > button:last-of-type"

    close_btn: Optional[Element] = None
    try:
        close_btn: Element = py.get(all_close_buttons_selector)
    except TimeoutException:
        ...

    if close_btn is not None:
        try:
            click_element(py=py, el=close_btn)
            close_confirm_discard_modal(py=py)
        except Exception as e:
            logger.error(f"Error when closing far left conversation {e}")
            return False
        return True
    else:
        return False

def close_confirm_discard_modal(py: Pylenium):
    try:
        discard_btn: Element = py.get("div.artdeco-modal > div:last-of-type > button:last-of-type")
        click_element(py=py, el=discard_btn)
    except TimeoutException:
        ...



##############################
# --- Page Object Models --- #
##############################

class Page:

    URL: Optional[str] = None

    def __init__(self, py: Pylenium):
        self.py: Pylenium = py

    def assert_on_correct_page(self):
        current_url: str = self.py.webdriver.current_url
        if current_url.strip("/") != self.URL.strip("/"):
            error_msg = f"Browser is at {current_url} but should be at {self.URL}."
            logger.error(error_msg)
            raise Exception(error_msg)

    def init(self):
        if self.URL:
            self.py.visit(self.URL)
            self.assert_on_correct_page()


class Login(Page):

    URL = "https://www.linkedin.com/"

    def __init__(self, py: Pylenium):
        super().__init__(py=py)

    def init(self):
        super().init()
        self.username_input: Element = self.py.get("#session_key")
        self.password_input: Element = self.py.get("#session_password")

    def login(self, username: str, password: str):
        self.username_input.type(username)
        self.password_input.type(password).submit()


class Conversation:

    def __init__(self, convo: Element, py: Pylenium):
        self.convo: Element = convo
        self.py: Pylenium = py

        # lazy loaded properties
        self._message_box: Optional[Element] = None
        self._send_button: Optional[Element] = None
        self._message_window_close_button: Optional[Element] = None
        self._name: Optional[str] = None

    @staticmethod
    def find_by_name(py: Pylenium, name: str) -> Optional[Conversation]:
        all_convos: List[Conversation] = Conversation.find_all_conversations(py=py)
        matched_convos = [convo for convo in all_convos if convo.name.lower() == name.lower()]
        if len(matched_convos) > 0:
            return matched_convos[0]
        return None
    
    @staticmethod
    def find_all_conversations(py: Pylenium) -> List[Conversation]:
        conversation_elems: List[Element] = py.find("div.msg-convo-wrapper")
        conversations: List[Conversation] = [
            Conversation(convo=convo, py=py) for convo in conversation_elems
        ]
        return conversations

    @property
    def name(self) -> str:
        if not self._name:
            self._name = self.convo.get("span.artdeco-pill__text").text()
        return self._name

    @property
    def message_box(self) -> Element:
        if not self._message_box:
            self._message_box = self.convo.get("div.msg-form__contenteditable")
        return self._message_box

    @property
    def send_button(self) -> Element:
        if not self._send_button:
            self._send_button = self.convo.get("button.msg-form__send-button")
        return self._send_button


    def set_message(self, msg: str):
        click_element(py=self.py, el=self.message_box)
        self.message_box.type(msg)

    def send_message(self):
        click_element(py=self.py, el=self.send_button)


class InvitationCard:
    def __init__(self, card: Element, py: Pylenium):
        self.card = card
        self.py = py

        self._message_button: Optional[Element] = None

    @property
    def name(self) -> Optional[str]:
        logger.debug(f"Looking for name on {self.card.text()}")
        spans: Element = self.card.find("span", timeout=0.5)
        return spans[1].text()

    @property
    def message_button(self) -> Element:
        if not self._message_button:
            self._message_button = self.card.get("button.message-anywhere-button")
        return self._message_button

    def open_message_dialogue(self):
        click_element(py=self.py, el=self.message_button)


class InvitationManager(Page):

    URL = "https://www.linkedin.com/mynetwork/invitation-manager/?invitationType=ALL"

    def __init__(self, py: Pylenium):
        super().__init__(py=py)

    @staticmethod
    def find_invitation_cards(py: Pylenium) -> List[InvitationCard]:
        py.scroll_to(x=0, y=100_000)
        sleep(5)
        cards: List[Element] = py.find("li.invitation-card")
        return [InvitationCard(card, py=py) for card in cards]

    def message_people(self, skip_names: List[str]):
        """Message all connection-requesters who are not to be skipped."""
        invitation_cards: List[InvitationCard] = InvitationManager.find_invitation_cards(py=self.py)
        for invite_card in invitation_cards:
            if invite_card.name.lower().strip() not in skip_names:
                logger.info(f"Messaging {invite_card.name}...")
                InvitationManager.message_person(py=self.py, invitation_card=invite_card)
            else:
                logger.info(f"Skipped {invite_card.name}.")

    @staticmethod
    def message_person(py: Pylenium, invitation_card: InvitationCard, message: str = BOT_MESSAGE):
        
        close_all_conversations(py=py)

        # open a message dialogue for the person
        invitation_card.open_message_dialogue()

        # find the message dialogue and set the message
        person_name: str = invitation_card.name
        convo: Optional[Conversation] = Conversation.find_by_name(py=py, name=person_name)
        if convo is not None:
            if convo.name != "Kameron Lightheart":
                raise Exception(f"Nooooo! {convo.name}")
            convo.set_message(message)
            convo.send_message()
            
            # record that we messaged this person so we don't message them again
            save_messaged_person(MessagedPerson(name=person_name))