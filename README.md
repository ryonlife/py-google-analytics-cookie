Py Google Analytics Cookie Parser
=====================================

[Py Google Analytics Cookie](https://github.com/ryonlife/py-google-analytics-cookie) is a simple class for parsing useful visitor and referral data from a Google Analytics cookie.

Utilize it during your sign up process in order to permanently store informations about where your customers came from, which opens the door for all sorts of useful metrics...

Cookie Breakdown
----------------

[From utma to utmz](http://www.morevisibility.com/analyticsblog/from-__utma-to-__utmz-google-analytics-cookies.html) is a decent blog post that explains, at a high level, the various cookies Google Analytics uses to store data. The two most interesting (at least to me) are the utma and utmz cookies:

* utma is a persistent cookie that tracks the number of visits, and times of the first and last visit
* utmz keeps track of all the referral information, with useful nuggets like ad campaigns and referring domain or search engine

Usage
-----

Instantiate an object with two keyword arguments containing the strings contained in the two cookies. Here's an example that will work on Pylons:

    from path.to.google_analytics_cookie import GoogleAnalyticsCookie
    utmz = request.cookies['__utmz'] if 'utmz' in request.cookies else None
    utma = request.cookies['__utma'] if 'utma' in request.cookies else None
    gac = GoogleAnalyticsCookie(utmz=utmz, utma=utma)
    
Your object will have utma and utmz attributes that are dictionaries with the following keys:

    gac.utma['domain_hash']
    gac.utma['random_id']
    gac.utma['first_visit_at']
    gac.utma['previous_visit_at']
    gac.utma['current_visit_at']
    gac.utma['session_counter']

    gac.utmz['domain_hash']
    gac.utmz['timestamp']
    gac.utmz['session_counter']
    gac.utmz['campaign_number']
    gac.utmz['campaign_data']['source']
    gac.utmz['campaign_data']['name']
    gac.utmz['campaign_data']['medium']
    gac.utmz['campaign_data']['term']
    gac.utmz['campaign_data']['content']
