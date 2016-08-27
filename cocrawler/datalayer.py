# datalayer, naieve implemenetion.
# all in-process-memory

#database layer spec

# host database
#   counters: urls seen, ...
# url database
#   surt url, last-crawl-date, ranking counters
# per-host crawl frontiers ordered by rank
#   lossy? refresh by iterating over url database
#   python Queue is single-process and not ranked
# robots cache, with timeout
# path to seed - naive or accurate?

import pickle
#import sortedcontainers - I wish!
import cachetools.ttl

class Datalayer:
    def __init__(self, config):
        self.config = config
        self.seen_urls = set()

        robots_size = config.get('Robots', {}).get('RobotsCacheSize')
        robots_ttl = config.get('Robots', {}).get('RobotsCacheTimeout')
        self.robots = cachetools.ttl.TTLCache(robots_size, robots_ttl)

    # This is the minimum url database:
    # as part of a "should we add this url to the queue?" process,
    # we need to remember all queued urls.

    def add_seen_url(self, url):
        self.seen_urls.add(url)

    # optionally stick a bloom filter in front of this
    # user specifies size at start
    # monitor false positive rate
    def seen_url(self, url):
        return url in self.seen_urls

    # collections.TTLCache is built on collections.OrderedDict and not sortedcontainers :-(
    # so it may need replacing if someone wants to do a survey crawl
    # XXX may need to become async so other implemtations can do an outcall?

    def cache_robots(self, schemenetloc, contents):
        self.robots[schemenetloc] = contents

    def read_robots_cache(self, schemenetloc):
        return self.robots[schemenetloc]

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.seen_urls, f)
            # don't save robots cache

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.seen_urls = pickle.load(f)
