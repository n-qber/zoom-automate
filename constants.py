WEBDRIVER_PATH = "./chromedriver.exe"
EXTENSION_PATH = "./src/5.0.4283.419_0.crx"
EXTENSION_ID = "hmbjbjdpkobdjplfobhljndfdfdipjhg"

ZOOM_WEB_ELEMENTS = {
    'CSS_SELECTOR': {
        'ZOOM_APP_ELEMENT': f"#{EXTENSION_ID} > div > div",
        'MEETING_ID_INPUT': '#join-confno',
        'SCREEN_NAME_INPUT': '#join-username',
        'CONNECT_AUDIO_CHECKBOX': '#join-form > div.checkbox.box-audio > label',
        'TURN_OFF_VIDEO_CHECKBOX': '#join-form > div.checkbox.box-video > label',
        'JOIN_BUTTON': '#btnSubmit',

        'PASSWORD_INPUT': '#password-value',
        'PASSWORD_JOIN_BUTTON': '#password-submit'
    }
}