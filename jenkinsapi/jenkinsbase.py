"""
Module for JenkinsBase class
"""

import logging
import datetime
from jenkinsapi import config
from jenkinsapi.custom_exceptions import JenkinsAPIException
log = logging.getLogger(__name__)


class JenkinsBase(object):
    """
    This appears to be the base object that all other jenkins objects are inherited from
    """
    RETRY_ATTEMPTS = 1

    def __repr__(self):
        return """<%s.%s %s>""" % (self.__class__.__module__,
                                   self.__class__.__name__,
                                   str(self))

    def __str__(self):
        raise NotImplementedError

    def __init__(self, baseurl, poll=True, poll_cache_timeout=0):
        """
        Initialize a jenkins connection
        """
        self._data = None
        self.baseurl = self.strip_trailing_slash(baseurl)
        self.poll_cache_timeout = poll_cache_timeout
        self.poll_cache_expires = None
        if poll:
            self.poll()

    def get_jenkins_obj(self):
        raise NotImplementedError('Please implement this method on %s' % self.__class__.__name__)

    def __eq__(self, other):
        """
        Return true if the other object represents a connection to the same server
        """
        if not isinstance(other, self.__class__):
            return False
        if not other.baseurl == self.baseurl:
            return False
        return True

    @classmethod
    def strip_trailing_slash(cls, url):
        while url.endswith('/'):
            url = url[:-1]
        return url

    def poll(self, force=False):
        now = datetime.datetime.now()
        if force or not self.poll_cache_expires or now > self.poll_cache_expires:
            self._data = self._poll()
            if self.poll_cache_timeout:
                dt = datetime.timedelta(seconds=self.poll_cache_timeout)
                self.poll_cache_expires = now + dt

    def _poll(self):
        url = self.python_api_url(self.baseurl)
        return self.get_data(url)

    def get_data(self, url, params=None):
        requester = self.get_jenkins_obj().requester
        response = requester.get_url(url, params)
        try:
            return eval(response.text)
        except Exception:
            log.exception('Inappropriate content found at %s', url)
            raise JenkinsAPIException('Cannot parse %s' % response.content)

    @classmethod
    def python_api_url(cls, url):
        if url.endswith(config.JENKINS_API):
            return url
        else:
            if url.endswith(r"/"):
                fmt = "%s%s"
            else:
                fmt = "%s/%s"
            return fmt % (url, config.JENKINS_API)
