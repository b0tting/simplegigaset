import logging
import datetime
import requests

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class SimpleGigaset:
    """A KISS object to manage your Gigaset system state.

    Currently limited to the following functionality:
    - Get systems mnode, state and events
    - Set a mode

    Args:
        email (str): The loginname you use for my.gigaset-elements.com
        password (str): The password you use for my.gigaset-elements.com

    """
    # This list of URLs was copied from the Gigaset elements CLI project:
    # https://github.com/dynasticorpheus/gigasetelements-cli
    URL_IDENTITY = "https://im.gigaset-elements.de/identity/api/v1/user/login"
    URL_AUTH = "https://api.gigaset-elements.de/api/v1/auth/openid/begin?op=gigaset"
    URL_EVENTS = 'https://api.gigaset-elements.de/api/v2/me/events'
    URL_BASE = 'https://api.gigaset-elements.de/api/v1/me/basestations'
    URL_CAMERA = 'https://api.gigaset-elements.de/api/v1/me/cameras'
    URL_HEALTH = 'https://api.gigaset-elements.de/api/v2/me/health'
    URL_CHANNEL = 'https://api.gigaset-elements.de/api/v1/me/notifications/users/channels'

    MODE_HOME = "home"
    MODE_AWAY = "away"
    MODE_CUSTOM = "custom"
    MODES = [MODE_HOME, MODE_AWAY, MODE_CUSTOM]

    STATE_OK = "ok"
    STATE_INTRUSION = "intrusion"

    def __init__(self, email, password, timeout=30):
        self.session = requests.Session()
        self.basestation = False
        self.timeout = timeout
        self.login = {"password": password, "email": email}

        self._login()
        jsonresponse = self._run_request(SimpleGigaset.URL_BASE)

        if "id" not in jsonresponse[0]:
            logger.error("Could not find a basestation ID. Did you register your basestation succesfully?")
        else:
            logger.info("Basestation ID according to the Gigaset Elements site is " + jsonresponse[0]["id"])
        self.basestation = jsonresponse[0]["id"]

    @staticmethod
    def _ts_to_datestring(ts):
        return datetime.datetime.fromtimestamp(int(ts[:10])).strftime('%H:%M')

    # Load session object with auth headers
    def _login(self):
        try:
            logger.debug("Trying to log in " + SimpleGigaset.URL_IDENTITY + ", credentials " + str(self.login))
            self.session.post(SimpleGigaset.URL_IDENTITY, data=self.login, timeout=self.timeout)
            self.session.get(SimpleGigaset.URL_AUTH, timeout=self.timeout)
        except Exception as e:
            # Rethrowing the exception without further handling
            raise e

    def _run_request(self, url, payload=False):
        if payload:
            logger.debug("Trying to POST to " + url + " with payload " + str(payload))
            response = self.session.post(url, timeout=self.timeout, data=payload)
        else:
            logger.debug("Trying to GET " + url)
            response = self.session.get(url, timeout=self.timeout, data=payload)

        if response.status_code == 401:
            logger.info("URL threw HTTP 401 error, session probably timedout. Logging in first.")
            # Since we got a 401, first login then rerun the request
            self._login()
            if payload:
                logger.debug("Trying to post to " + url + " with payload " + str(payload))
                response = self.session.post(url, timeout=self.timeout, data=payload)
            else:
                logger.debug("Trying to GET " + url)
                response = self.session.get(url, timeout=self.timeout, data=payload)
        logger.debug("Response text was: " + response.text)
        return response.json()

    def get_current_state(self):
        """Fetches a system overview object with the last few events, current state and mode

         Returns:
             dict: A dictionary object with "state", "mode" and "events[]"

        """
        jsonresponse = self._run_request(SimpleGigaset.URL_EVENTS + "?limit=3")
        state = {"state": jsonresponse["home_state"],
                 "mode": self.get_mode(),
                 "events": [SimpleGigaset._ts_to_datestring(event["ts"]) + " - " + event["type"] for event in jsonresponse["events"]]}
        return state

    def set_mode(self, mode):
        """Sets the Gigaset Elements System mode: home, away or custom. This is a fire-and-forget function,
        you do not need to handle the return value.

        Args:
            mode (str): One of three: SimpleGigaset.HOME, SimpleGigaset.AWAY, SimpleGigaset.CUSTOM

        Returns:
            bool: True if the mode successfully set
        """
        logger.debug("Attempting to set mode " + mode)
        if mode not in SimpleGigaset.MODES:
            raise ValueError("Suggested mode " + mode + " is not in the list of accepted modes: " +
                             str(SimpleGigaset.MODES))
        payload = '{"intrusion_settings": {"active_mode": "'+mode+'"}}'
        jsonresponse = self._run_request(SimpleGigaset.URL_BASE + "/" + self.basestation, payload)
        return "_id" in jsonresponse

    def is_alarmed(self):
        """Checks if the system is in an alared state. Note that this has to reach over the internet
        to the Gigaset site, do not overuse this! The highest I've seen this go without error
        is 1 request / second.

        Returns:
            bool: True if the system has the "intrusion" state, or False if anything else.

        """
        state = self.get_current_state()
        logger.debug("Attempting to get alarm state from " + str(state))
        if "state" not in state:
            logger.error("Could not find a valid system state in response!")
            return False
        else:
            return state["state"] == SimpleGigaset.STATE_INTRUSION

    def get_mode(self):
        """Returns the current mode of the Gigaset Elements system. This is the state you
        set in the app.

        Returns:
            mode (str): One of three: SimpleGigaset.HOME, SimpleGigaset.AWAY, SimpleGigaset.CUSTOM

        """
        jsonresponse = self._run_request(SimpleGigaset.URL_BASE)
        logger.info("Got system mode " + jsonresponse[0]["intrusion_settings"]["active_mode"])
        return jsonresponse[0]["intrusion_settings"]["active_mode"]