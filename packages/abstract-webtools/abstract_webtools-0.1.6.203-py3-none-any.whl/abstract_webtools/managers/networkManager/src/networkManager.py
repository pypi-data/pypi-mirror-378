from .imports import *
from .functions import *
class NetworkManager:
    def __init__(self, user_agent_manager=None,user_agent=None, tls_adapter=None,ssl_manager=None, proxies=None, cookies=None,
                 ciphers=None, certification: Optional[str]=None, ssl_options: Optional[List[str]]=None):
        self.ua_mgr = user_agent_manager or UserAgentManager()
        self.ciphers = ciphers or CipherManager().ciphers_string
        self.ssl_mgr = ssl_manager or SSLManager(
            ciphers=self.ciphers or CipherManager().ciphers_string,
            ssl_options=ssl_options,
            certification=certification
        )
        self.certification = self.ssl_mgr.certification
        self.ssl_options = self.ssl_mgr.ssl_options
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or self.ua_mgr.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        })
        self.tls_adapter = tls_adapter or TLSAdapter(self.ssl_mgr)
        self.session.mount("https://", self.tls_adapter)
        self.session.mount("http://", HTTPAdapter())

        if proxies:
            self.session.proxies = proxies
        self.proxies = self.session.proxies
        if cookies:
            if isinstance(cookies, requests.cookies.RequestsCookieJar):
                self.session.cookies = cookies
            elif isinstance(cookies, dict):
                jar = requests.cookies.RequestsCookieJar()
                for k,v in cookies.items(): jar.set(k,v)
                self.session.cookies = jar
            # if string: up to you—parse or ignore
        self.cookies = self.session.cookies
        # retries (optional)
        from requests.adapters import Retry
        self.session.adapters['https://'].max_retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
        # Normalize cookies on init
        self.cookies = self._normalize_cookies(cookies)
    def _normalize_cookies(self, cookies):
        """Ensure cookies are always a dict of str->str"""
        if not cookies:
            return {}

        # Already a dict
        if isinstance(cookies, dict):
            return {k: str(v) for k, v in cookies.items() if isinstance(v, (str, bytes))}

        # If a RequestsCookieJar, flatten it into a dict
        if isinstance(cookies, requests.cookies.RequestsCookieJar):
            return {c.name: str(c.value) for c in cookies if isinstance(c.value, (str, bytes))}

        logging.warning(f"Dropping invalid cookies object: {cookies!r}")
        return {}
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self._ssl_context
        return super().init_poolmanager(*args, **kwargs)
