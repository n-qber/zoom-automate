from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Chrome, ChromeOptions
from typing import Union
from constants import *
from json import dumps


class ZoomClient:
    def __init__(self,
                 webdriver_path: str = WEBDRIVER_PATH,
                 extension_path: str = EXTENSION_PATH):

        self._APP_CONTEXT = "NOT_STARTED"

        self.webdriver_options = ChromeOptions()
        self.webdriver_options.add_argument('user-agent=Mozilla/5.0 (X11; CrOS x86_64 13816.55.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.86 Safari/537.36')
        self.webdriver_options.add_extension(extension_path)
        self.webdriver = Chrome(webdriver_path, options=self.webdriver_options)

    def _switch_to_zoom_window(self):
        # Wait for the Zoom window to load
        while len(self.webdriver.window_handles) != 2:
            continue

        self.webdriver.close()  # closes the "apps" section
        self.webdriver.switch_to.window(self.webdriver.window_handles[0])  # switches context to zoom app itself :)

    def _webdriver_wait_element(self, by, value, debug=True) -> WebElement:
        while True:
            try:
                return self.webdriver.find_element(by, value)
            except Exception as ex:
                if debug:
                    print(ex)

    def _enter_join_room(self):
        self.webdriver.get("chrome://apps")  # enters "apps" section

        # click to open zoom app
        self._webdriver_wait_element('css selector', ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['ZOOM_APP_ELEMENT']).click()

        # new zoom window will popup, focus on it
        self._switch_to_zoom_window()

    def _execute(self, data):
        print("""

        common.postMessageToNaCl(%s)
        
        """ % dumps(data))
        self.webdriver.execute_script("""

        common.postMessageToNaCl(%s)
        
        """ % dumps(data))

    def enter_join_room(self):
        self.webdriver.get("chrome://apps")  # enters "apps" section

        # click to open zoom app
        self._webdriver_wait_element('css selector', ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['ZOOM_APP_ELEMENT']).click()

        # new zoom window will popup, focus on it
        self._switch_to_zoom_window()

    def _join_by_link(self, invite_link: str):
        if self._APP_CONTEXT == "JOIN_ROOM":
            # get out of zoom application to get to the invite url
            self.webdriver.execute_script(f'''window.open("{invite_link}", "_blank");''')
        else:
            self.webdriver.get(invite_link)

        # new zoom window will popup, focus on it
        self._switch_to_zoom_window()
        self._APP_CONTEXT = "JOIN_ROOM"
        return  # it should return inside de join() function joining a meeting

    def join(self,
             screen_name: str,
             meeting_id: Union[int, str] = None,
             invite_link: str = None,
             meeting_password: str = None,
             connect_to_audio: bool = True,
             turn_off_video: bool = True):

        if invite_link:
            self._join_by_link(invite_link)
            invite_link = ""

        if not self._APP_CONTEXT == "JOIN_ROOM":
            self.enter_join_room()

        # setting the values passed through the arguments
        if meeting_id:
            self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['MEETING_ID_INPUT']). \
                send_keys(meeting_id)
        self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['SCREEN_NAME_INPUT']). \
            send_keys(screen_name)
        if not connect_to_audio:
            self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['CONNECT_AUDIO_CHECKBOX']). \
                click()
        if turn_off_video:
            self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['TURN_OFF_VIDEO_CHECKBOX']). \
                click()

        # press join button
        self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['JOIN_BUTTON']).click()

        # check if needs a password or not
        if meeting_password:

            # wait for input element to load
            password_input = self._webdriver_wait_element('css selector',
                                                         ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['PASSWORD_INPUT'])
            while not password_input.is_displayed():
                continue
            password_input.send_keys(meeting_password)

            self.webdriver.find_element_by_css_selector(ZOOM_WEB_ELEMENTS['CSS_SELECTOR']['PASSWORD_JOIN_BUTTON']). \
                click()

    def get_participants(self):
        return self.webdriver.execute_script("return mainAppHtmlWindow.attendeeList;")

    def get_context(self):  # doesn't exist yet
        return

    @property
    def loaded(self):
        return [x is not None and not x for x in [self.webdriver.execute_script("""
                return g.getMeetingStatusObj().isInWaitingRoom;
                """)]][0]

    def wait_loaded(self):
        while not self.loaded:
            pass  # might add a sleep

    def send_message_to_participant(self, participant_id, message):

        if not self.can_chat_with_participant(participant_id):  # Chat disabled for this participant
            return -1

        self.webdriver.execute_script("""
        
        mainAppHtmlWindow.common.postMessageToNaCl({
                        type: "chat",
                        command: "chat.sendChatTo",
                        receiver: Number('%d'),
                        toAllPanelists: Number(mainAppHtmlWindow.chatObject.curToAllPanelist),
                        content: "%s",
                        attendeeChatPriviledge: mainAppHtmlWindow.chatObject.attendeeChatPriviledge
                    })
        """ % (int(participant_id), message))

    def can_chat_with_participant(self, participant_id):
        return self.webdriver.execute_script("""
        let e = mainAppHtmlWindow.chatObject.attendeeChatPriviledge;
        let t = '%d';
        
        if (mainAppHtmlWindow.chatObject.isHost || mainAppHtmlWindow.myStatusObject.isCoHost) return !0;
        switch (e) {
            case "CHAT_PRIVILEDGE_HOST":
                if (mainAppHtmlWindow.g.getMeetingStatusObj().hostId == t || d(t, mainAppHtmlWindow.g.getMeetingStatusObj().coHost)) return !0;
                break;
            case "CHAT_PRIVILEDGE_HOST_PUBLIC":
                if (0 === parseInt(t)) return !0;
                if (mainAppHtmlWindow.g.getMeetingStatusObj().hostId == t || d(t, mainAppHtmlWindow.g.getMeetingStatusObj().coHost)) return !0;
                break;
            case "CHAT_PRIVILEDGE_ALL":
                return !0;
            case "CHAT_PRIVILEDGE_DISABLE_ATTENDEE_CHAT":
                return !(!mainAppHtmlWindow.g.getMeetingStatusObj().isWebinar || mainAppHtmlWindow.g.getMeetingStatusObj().meetingIsViewOnly);
            case "CHAT_PRIVILEDGE_ALL_PANELIST":
                return !mainAppHtmlWindow.g.getMeetingStatusObj().isWebinar || !mainAppHtmlWindow.g.getMeetingStatusObj().meetingIsViewOnly || 0 == mainAppHtmlWindow.chatObject.curReceiverID && 1 == mainAppHtmlWindow.chatObject.curToAllPanelist;
            default:
                return !1;
        }
        """ % int(participant_id))

    def login(self,   # TODO =======================
              name: str = None,
              password: str = None,
              token: str = None):

        if token is None:
            self.webdriver.execute_script("""
                common.postMessageToNaCl({
                    type: "user",
                    command: "user.login",
                    name: '%s',
                    password: '%s',
                    keepLogin: false
                })
            """ % (name, password))
            return
        self.webdriver.execute_script("""
            common.postMessageToNaCl({
                type: "user",
                command: "user.loginWithToken",
                token: e
            })
            """ % token)

    @property
    def id(self):
        # TODO ====== SOLVE THIS ID GET THING GRUHRGH
        return self.webdriver.execute_script("""
        return mainAppHtmlWindow.attendeeList.filter(x => x.isMyself)[0].id;
        """)

    def raise_hand(self, user_id: str = None):

        data = f"'{user_id or self.id}'"

        self.webdriver.execute_script("""
        inmeeting.raiseHand(%s);
        """ % data)

    def lower_hand(self, user_id: str = None):

        data = f"'{user_id or self.id}'"

        self.webdriver.execute_script("""
        inmeeting.lowerHand(%s);
        """ % data)


if __name__ == '__main__':
    zoom_client = ZoomClient()
    zoom_client.join(meeting_id="123456789",
                     meeting_password="0aBcdef",
                     screen_name="Im amazing")
