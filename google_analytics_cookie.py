########################################################################################
#
# PYTHON GOOGLE ANALYTICS COOKIE PARSER
#
# Copyright (c) 2010, Ryan McKillen <@RyOnLife>.
# All Rights Reserved.
#
# Originally written for use on http://www.ubercab.com and inspired by the
# PHP Google Analytics Parser Class published by Joao Correia at
# http://joaocorreia.pt/google-analytics-scripts/google-analytics-php-cookie-parser/.
#
# This software is subject to the provisions of the GNU LGPL v3 license at
# http://www.gnu.org/licenses/lgpl-3.0.txt. A copy of the license should accompany this
# distribution. THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
########################################################################################

import re
import unittest
from datetime import datetime

class GoogleAnalyticsCookie():
    """ Parses the utma (visitor) and utmz (referral) Google Analytics cookies """
    utmz = dict(
        domain_hash = None,
        timestamp = None,
        session_counter = None,
        campaign_number = None,
        campaign_data = dict(
            source = None,
            name = None,
            medium = None,
            term = None,
            content = None
        )
    )       
    utma = dict(
        domain_hash = None,
        random_id = None,
        first_visit_at = None,
        previous_visit_at = None,
        current_visit_at = None,
        session_counter = None
    )     
    
          
    def __init__(self, utmz=None, utma=None):
        self.utmz = dict(
            domain_hash = None,
            timestamp = None,
            session_counter = None,
            campaign_number = None,
            campaign_data = dict(
                source = None,
                name = None,
                medium = None,
                term = None,
                content = None
            )
        )        
        
        self.utma = dict(
            domain_hash = None,
            random_id = None,
            first_visit_at = None,
            previous_visit_at = None,
            current_visit_at = None,
            session_counter = None
        )        
        if utmz:
            self.utmz = self.__parse_utmz(utmz)
        if utma:
            self.utma = self.__parse_utma(utma)
        
    def __parse_utmz(self, cookie):
        """ Parses the utmz cookie for visitor information """
        parsed = cookie.split('.')
        if len(parsed) < 5:
            return self.utmz 
        
        #rejoin when src or cct might have a dot i.e. utmscr=example.com
        parsed[4] = ".".join(parsed[4:])    
        
        translations = dict(
            utmcsr = 'source',
            utmccn = 'name',
            utmcmd = 'medium',
            utmctr = 'term',
            utmcct = 'content'
        )
        
        parsed_campaign_data = self.utmz['campaign_data']
        
        for params in parsed[4].split('|'):
            key_value = params.split('=')
            if translations.has_key(key_value[0]):
                parsed_campaign_data[translations[key_value[0]]] = key_value[1]
        
        # Override campaign data when visitor comes from Google AdWords    
        if re.search('gclid=', cookie):
            parsed_campaign_data = dict(
                source = 'google',
                name = None,
                medium = 'cpc',
                content = None,
                term = parsed_campaign_data['term']
            )
                
        return dict(
            domain_hash = parsed[0],
            timestamp = parsed[1],
            session_counter = parsed[2],
            campaign_number = parsed[3],
            campaign_data = parsed_campaign_data
        )
        
    def __parse_utma(self, cookie):
        """ Parses the utma cookie for referral information """
        parsed = cookie.split('.')
        if len(parsed) != 6:
            return self.utma
        
        return dict(
            domain_hash = parsed[0],
            random_id = parsed[1],
            first_visit_at = datetime.fromtimestamp(float(parsed[2])),
            previous_visit_at = datetime.fromtimestamp(float(parsed[3])),
            current_visit_at = datetime.fromtimestamp(float(parsed[4])),
            session_counter = parsed[5]
        )
        
class TestGoogleAnalyticsCookie(unittest.TestCase):
    
    utmz_test = '174403709.1285179976.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)|utmctr=test'
    utmz_test2 = '81516565.1309300431.44.5.utmcsr=stumbleupon.com|utmccn=(referral)|utmcmd=referral|utmcct=/refer.php'
    utma = '174403709.475482016.1285179976.1285179976.1285179976.1'
    
    def test_parse_utmz(self):
        """ Should properly parse utmz cookie data """
        gac = GoogleAnalyticsCookie(utmz=self.utmz_test)
        self.assertEqual(gac.utmz['domain_hash'], '174403709')
        self.assertEqual(gac.utmz['timestamp'], '1285179976')
        self.assertEqual(gac.utmz['session_counter'], '1')
        self.assertEqual(gac.utmz['campaign_number'], '1')
        
        self.assertEqual(gac.utmz['campaign_data']['source'], '(direct)')
        self.assertEqual(gac.utmz['campaign_data']['name'], '(direct)')
        self.assertEqual(gac.utmz['campaign_data']['medium'], '(none)')
        self.assertEqual(gac.utmz['campaign_data']['term'], 'test')
        self.assertEqual(gac.utmz['campaign_data']['content'], None)

    def test_parse_utmz_referral_url(self):
        """ Should properly parse utmz cookie data when there are periods in the src and in the content"""
        gac = GoogleAnalyticsCookie(utmz=self.utmz_test2)
        self.assertEqual(gac.utmz['domain_hash'], '81516565')
        self.assertEqual(gac.utmz['timestamp'], '1309300431')
        self.assertEqual(gac.utmz['session_counter'], '44')
        self.assertEqual(gac.utmz['campaign_number'], '5')
        
        self.assertEqual(gac.utmz['campaign_data']['source'], 'stumbleupon.com')
        self.assertEqual(gac.utmz['campaign_data']['name'], '(referral)')
        self.assertEqual(gac.utmz['campaign_data']['medium'], 'referral')
        self.assertEqual(gac.utmz['campaign_data']['term'], None)
        self.assertEqual(gac.utmz['campaign_data']['content'], '/refer.php')
    
            
    def test_parse_utmz_gclid(self):
        """ Should override normal campaign parsing when a Google Adwords click is involved """
        gac = GoogleAnalyticsCookie(utmz=self.utmz_test + '|gclid=123')
        self.assertEqual(gac.utmz['campaign_data']['source'], 'google')
        self.assertEqual(gac.utmz['campaign_data']['name'], None)
        self.assertEqual(gac.utmz['campaign_data']['medium'], 'cpc')
        self.assertEqual(gac.utmz['campaign_data']['term'], 'test')
        self.assertEqual(gac.utmz['campaign_data']['content'], None)
        
    def test_parse_utma(self):
        """ Should properly parse utma cookie data """
        gac = GoogleAnalyticsCookie(utma=self.utma)
        self.assertEqual(gac.utma['domain_hash'], '174403709')
        self.assertEqual(gac.utma['random_id'], '475482016')
        self.assertEqual(gac.utma['first_visit_at'], datetime.fromtimestamp(1285179976))
        self.assertEqual(gac.utma['previous_visit_at'], datetime.fromtimestamp(1285179976))
        self.assertEqual(gac.utma['current_visit_at'], datetime.fromtimestamp(1285179976))
        self.assertEqual(gac.utma['session_counter'], '1')
        
    def test_parse_no_cookie(self):
        """ Should key dictionaries with None values when cookies are is missing """
        gac = GoogleAnalyticsCookie()
        self.assertEqual(gac.utmz['domain_hash'], None)
        self.assertEqual(gac.utmz['timestamp'], None)
        self.assertEqual(gac.utmz['session_counter'], None)
        self.assertEqual(gac.utmz['campaign_number'], None)
        self.assertEqual(gac.utmz['campaign_data']['source'], None)
        self.assertEqual(gac.utmz['campaign_data']['name'], None)
        self.assertEqual(gac.utmz['campaign_data']['medium'], None)
        self.assertEqual(gac.utmz['campaign_data']['term'], None)
        self.assertEqual(gac.utmz['campaign_data']['content'], None)
        self.assertEqual(gac.utma['domain_hash'], None)
        self.assertEqual(gac.utma['random_id'], None)
        self.assertEqual(gac.utma['first_visit_at'], None)
        self.assertEqual(gac.utma['previous_visit_at'], None)
        self.assertEqual(gac.utma['current_visit_at'], None)
        self.assertEqual(gac.utma['session_counter'], None)
        
    def test_parse_bad_cookie(self):
        """ Should key dictionaries with None values when cookies have bad data """
        gac = GoogleAnalyticsCookie(utmz='-', utma='-')
        self.assertEqual(gac.utmz['domain_hash'], None)
        self.assertEqual(gac.utmz['timestamp'], None)
        self.assertEqual(gac.utmz['session_counter'], None)
        self.assertEqual(gac.utmz['campaign_number'], None)
        self.assertEqual(gac.utmz['campaign_data']['source'], None)
        self.assertEqual(gac.utmz['campaign_data']['name'], None)
        self.assertEqual(gac.utmz['campaign_data']['medium'], None)
        self.assertEqual(gac.utmz['campaign_data']['term'], None)
        self.assertEqual(gac.utmz['campaign_data']['content'], None)
        self.assertEqual(gac.utma['domain_hash'], None)
        self.assertEqual(gac.utma['random_id'], None)
        self.assertEqual(gac.utma['first_visit_at'], None)
        self.assertEqual(gac.utma['previous_visit_at'], None)
        self.assertEqual(gac.utma['current_visit_at'], None)
        self.assertEqual(gac.utma['session_counter'], None)

if __name__ == '__main__':
    unittest.main()
