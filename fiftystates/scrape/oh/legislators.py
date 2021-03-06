import re

from fiftystates.scrape import NoDataForPeriod
from fiftystates.scrape.legislators import LegislatorScraper, Legislator

import lxml.etree


class OHLegislatorScraper(LegislatorScraper):
    state = 'oh'

    def scrape(self, chamber, term):
        if term != '2011-2012':
            raise NoDataForPeriod(term)

        if chamber == 'upper':
            self.scrape_senators(chamber, term)
        else:
            self.scrape_reps(chamber, term)

    def scrape_reps(self, chamber, term):
        # There are 99 House districts
        for district in xrange(1, 100):
            rep_url = ('http://www.house.state.oh.us/components/'
                       'com_displaymembers/page.php?district=%d' % district)

            with self.urlopen(rep_url) as page:
                root = lxml.etree.fromstring(page, lxml.etree.HTMLParser())

                for el in root.xpath('//table[@class="page"]'):
                    rep_link = el.xpath('tr/td/title')[0]
                    full_name = rep_link.text
                    party = full_name[-2]
                    full_name = full_name[0:-3]

                    if party == "D":
                        party = "Democratic"
                    elif party == "R":
                        party = "Republican"

                    leg = Legislator(term, chamber, str(district),
                                     full_name, '', '', '', party)
                    leg.add_source(rep_url)

                self.save_legislator(leg)

    def scrape_senators(self, chamber, term):
        sen_url = 'http://www.ohiosenate.gov/directory.html'
        with self.urlopen(sen_url) as page:
            root = lxml.etree.fromstring(page, lxml.etree.HTMLParser())

            for el in root.xpath('//table[@class="fullWidth"]/tr/td'):
                sen_link = el.xpath('a[@class="senatorLN"]')[1]

                full_name = sen_link.text
                full_name = full_name[0:-2]
                if full_name == 'To Be Announced':
                    continue

                district = el.xpath('string(h3)').split()[1]

                party = el.xpath('string(a[@class="senatorLN"]/span)')

                if party == "D":
                    party = "Democrat"
                elif party == "R":
                    party = "Republican"

                leg = Legislator(term, chamber, district, full_name,
                        '', '', '', party)
                leg.add_source(sen_url)

                self.save_legislator(leg)
