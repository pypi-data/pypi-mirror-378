from .imports import *
from .functions import *
class UserAgentManager:
    def __init__(self,
                 operating_system=None,
                 browser=None,
                 version=None,
                 user_agent=None,
                 randomAll=False,
                 randomOperatingSystem=False,
                 randomBrowser=False):
        self.randomAll = randomAll
        self.randomOperatingSystem = randomOperatingSystem
        self.randomBrowser = randomBrowser
        self.operating_system = pickUserAgentVars(
            operating_system,
            OPERATING_SYSTEMS
            )
        self.browser = pickUserAgentVars(
            browser,
            BROWSERS
            )
        self.version = version or '42.0'
        self.user_agent = user_agent or self.get_user_agent()
        self.header = {"user-agent": self.user_agent}

    @staticmethod
    def user_agent_db():
        return BIG_USER_AGENT_DICT
    def get_random_choice(self,operating_system=False,browser=False):
        if self.randomAll or self.randomOperatingSystem or (isinstance(operating_system,bool) and operating_system == True):
            self.operating_system = randomChoice(OPERATING_SYSTEMS)
        if self.randomAll or self.randomBrowser or (isinstance(browser,bool) and browser == True):
            self.browser = randomChoice(BROWSERS)
        return self.operating_system,self.browser
    def get_user_agent(self):
        ua_db = self.user_agent_db()
        self.get_random_choice()
        os_db = getRandomValues(ua_db,self.operating_system)
        br_db = getRandomValues(os_db,self.browser)
        if self.version in br_db:
            return br_db[self.version]
        return randomChoice(br_db)


