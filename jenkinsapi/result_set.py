"""
Module for jenkinsapi ResultSet
"""

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.result import Result


class ResultSet(JenkinsBase):
    """
    Represents a result from a completed Jenkins run.
    """
    def __init__(self, url, build, poll_cache_timeout=0):
        """
        Init a resultset
        :param url: url for a build, str
        :param build: build obj
        """
        self.build = build
        JenkinsBase.__init__(self, url, poll_cache_timeout=poll_cache_timeout)

    def get_jenkins_obj(self):
        return self.build.job.get_jenkins_obj()

    def __str__(self):
        return "Test Result for %s" % str(self.build)

    @property
    def name(self):
        return str(self)

    def keys(self):
        return [a[0] for a in self.iteritems()]

    def items(self):
        return [a for a in self.iteritems()]

    def iteritems(self):
        for suite in self._data.get("suites", []):
            for case in suite["cases"]:
                result = Result(**case)
                yield result.identifier(), result

        for report_set in self._data.get("childReports", []):
            for suite in report_set["result"]["suites"]:
                for case in suite["cases"]:
                    result = Result(**case)
                    yield result.identifier(), result

    def __len__(self):
        return len(self.items())

    def __getitem__(self, key):
        self_as_dict = dict(self.iteritems())
        return self_as_dict[key]
