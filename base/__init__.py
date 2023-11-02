import os
import requests
import json
import time
import datetime
from types import SimpleNamespace
import regex
regex.DEFAULT_VERSION = regex.VERSION1
from bs4 import BeautifulSoup
import sys
import copy
import random
from threading import Thread
from collections.abc import Sequence
import six
import hashlib
import base64
import itertools
import pickle
import store
import logging

crt_cod = [{"name":"Afghanistan","code":"af"},{"name":"Albania","code":"al"},{"name":"Algeria","code":"dz"},{"name":"American Samoa","code":"as"},{"name":"Andorra","code":"ad"},{"name":"Angola","code":"ao"},{"name":"Anguilla","code":"ai"},{"name":"Antarctica","code":"aq"},{"name":"Antigua and Barbuda","code":"ag"},{"name":"Argentina","code":"ar"},{"name":"Armenia","code":"am"},{"name":"Aruba","code":"aw"},{"name":"Australia","code":"au"},{"name":"Austria","code":"at"},{"name":"Azerbaijan","code":"az"},{"name":"Bahamas","code":"bs"},{"name":"Bahrain","code":"bh"},{"name":"Bangladesh","code":"bd"},{"name":"Barbados","code":"bb"},{"name":"Belarus","code":"by"},{"name":"Belgium","code":"be"},{"name":"Belize","code":"bz"},{"name":"Benin","code":"bj"},{"name":"Bermuda","code":"bm"},{"name":"Bhutan","code":"bt"},{"name":"Bolivia, Plurinational State of","code":"bo"},{"name":"Bosnia and Herzegovina","code":"ba"},{"name":"Botswana","code":"bw"},{"name":"Bouvet Island","code":"bv"},{"name":"Brazil","code":"br"},{"name":"British Indian Ocean Territory","code":"io"},{"name":"Brunei Darussalam","code":"bn"},{"name":"Bulgaria","code":"bg"},{"name":"Burkina Faso","code":"bf"},{"name":"Burundi","code":"bi"},{"name":"Cabo Verde","code":"cv"},{"name":"Cambodia","code":"kh"},{"name":"Cameroon","code":"cm"},{"name":"Canada","code":"ca"},{"name":"Cayman Islands","code":"ky"},{"name":"Central African Republic","code":"cf"},{"name":"Chad","code":"td"},{"name":"Chile","code":"cl"},{"name":"China","code":"cn"},{"name":"Christmas Island","code":"cx"},{"name":"Colombia","code":"co"},{"name":"Comoros","code":"km"},{"name":"Congo","code":"cg"},{"name":"Congo, The Democratic Republic of the","code":"cd"},{"name":"Cook Islands","code":"ck"},{"name":"Costa Rica","code":"cr"},{"name":"Croatia","code":"hr"},{"name":"Cuba","code":"cu"},{"name":"Cyprus","code":"cy"},{"name":"Czechia","code":"cz"},{"name":"C\xc3\xb4te d\'Ivoire","code":"ci"},{"name":"Denmark","code":"dk"},{"name":"Djibouti","code":"dj"},{"name":"Dominica","code":"dm"},{"name":"Dominican Republic","code":"do"},{"name":"Ecuador","code":"ec"},{"name":"Egypt","code":"eg"},{"name":"El Salvador","code":"sv"},{"name":"Equatorial Guinea","code":"gq"},{"name":"Eritrea","code":"er"},{"name":"Estonia","code":"ee"},{"name":"Eswatini","code":"sz"},{"name":"Ethiopia","code":"et"},{"name":"Falkland Islands (Malvinas)","code":"fk"},{"name":"Faroe Islands","code":"fo"},{"name":"Fiji","code":"fj"},{"name":"Finland","code":"fi"},{"name":"France","code":"fr"},{"name":"French Guiana","code":"gf"},{"name":"French Polynesia","code":"pf"},{"name":"French Southern Territories","code":"tf"},{"name":"Gabon","code":"ga"},{"name":"Gambia","code":"gm"},{"name":"Georgia","code":"ge"},{"name":"Germany","code":"de"},{"name":"Ghana","code":"gh"},{"name":"Gibraltar","code":"gi"},{"name":"Greece","code":"gr"},{"name":"Greenland","code":"gl"},{"name":"Grenada","code":"gd"},{"name":"Guadeloupe","code":"gp"},{"name":"Guam","code":"gu"},{"name":"Guatemala","code":"gt"},{"name":"Guinea","code":"gn"},{"name":"Guinea-Bissau","code":"gw"},{"name":"Guyana","code":"gy"},{"name":"Haiti","code":"ht"},{"name":"Holy See (Vatican City State)","code":"va"},{"name":"Honduras","code":"hn"},{"name":"Hong Kong","code":"hk"},{"name":"Hungary","code":"hu"},{"name":"Iceland","code":"is"},{"name":"India","code":"in"},{"name":"Indonesia","code":"id"},{"name":"Iran, Islamic Republic of","code":"ir"},{"name":"Iraq","code":"iq"},{"name":"Ireland","code":"ie"},{"name":"Israel","code":"il"},{"name":"Italy","code":"it"},{"name":"Jamaica","code":"jm"},{"name":"Japan","code":"jp"},{"name":"Jordan","code":"jo"},{"name":"Kazakhstan","code":"kz"},{"name":"Kenya","code":"ke"},{"name":"Kiribati","code":"ki"},{"name":"Korea, Democratic People\'s Republic of","code":"kp"},{"name":"Korea, Republic of","code":"kr"},{"name":"Kuwait","code":"kw"},{"name":"Kyrgyzstan","code":"kg"},{"name":"Lao People\'s Democratic Republic","code":"la"},{"name":"Latvia","code":"lv"},{"name":"Lebanon","code":"lb"},{"name":"Lesotho","code":"ls"},{"name":"Liberia","code":"lr"},{"name":"Libya","code":"ly"},{"name":"Liechtenstein","code":"li"},{"name":"Lithuania","code":"lt"},{"name":"Luxembourg","code":"lu"},{"name":"Macao","code":"mo"},{"name":"Madagascar","code":"mg"},{"name":"Malawi","code":"mw"},{"name":"Malaysia","code":"my"},{"name":"Maldives","code":"mv"},{"name":"Mali","code":"ml"},{"name":"Malta","code":"mt"},{"name":"Marshall Islands","code":"mh"},{"name":"Martinique","code":"mq"},{"name":"Mauritania","code":"mr"},{"name":"Mauritius","code":"mu"},{"name":"Mayotte","code":"yt"},{"name":"Mexico","code":"mx"},{"name":"Micronesia, Federated States of","code":"fm"},{"name":"Moldova, Republic of","code":"md"},{"name":"Monaco","code":"mc"},{"name":"Mongolia","code":"mn"},{"name":"Montenegro","code":"me"},{"name":"Montserrat","code":"ms"},{"name":"Morocco","code":"ma"},{"name":"Mozambique","code":"mz"},{"name":"Myanmar","code":"mm"},{"name":"Namibia","code":"na"},{"name":"Nauru","code":"nr"},{"name":"Nepal","code":"np"},{"name":"Netherlands","code":"nl"},{"name":"New Caledonia","code":"nc"},{"name":"New Zealand","code":"nz"},{"name":"Nicaragua","code":"ni"},{"name":"Niger","code":"ne"},{"name":"Nigeria","code":"ng"},{"name":"Norfolk Island","code":"nf"},{"name":"North Macedonia","code":"mk"},{"name":"Northern Mariana Islands","code":"mp"},{"name":"Norway","code":"no"},{"name":"Oman","code":"om"},{"name":"Pakistan","code":"pk"},{"name":"Palau","code":"pw"},{"name":"Palestine, State of","code":"ps"},{"name":"Panama","code":"pa"},{"name":"Papua New Guinea","code":"pg"},{"name":"Paraguay","code":"py"},{"name":"Peru","code":"pe"},{"name":"Philippines","code":"ph"},{"name":"Pitcairn","code":"pn"},{"name":"Poland","code":"pl"},{"name":"Portugal","code":"pt"},{"name":"Puerto Rico","code":"pr"},{"name":"Qatar","code":"qa"},{"name":"Romania","code":"ro"},{"name":"Russia","code":"ru"},{"name":"Rwanda","code":"rw"},{"name":"R\xc3\xa9union","code":"re"},{"name":"Saint Helena, Ascension and Tristan da Cunha","code":"sh"},{"name":"Saint Kitts and Nevis","code":"kn"},{"name":"Saint Lucia","code":"lc"},{"name":"Saint Vincent and the Grenadines","code":"vc"},{"name":"Samoa","code":"ws"},{"name":"San Marino","code":"sm"},{"name":"Sao Tome and Principe","code":"st"},{"name":"Saudi Arabia","code":"sa"},{"name":"Senegal","code":"sn"},{"name":"Serbia","code":"rs"},{"name":"Seychelles","code":"sc"},{"name":"Sierra Leone","code":"sl"},{"name":"Singapore","code":"sg"},{"name":"Slovakia","code":"sk"},{"name":"Slovenia","code":"si"},{"name":"Solomon Islands","code":"sb"},{"name":"Somalia","code":"so"},{"name":"South Africa","code":"za"},{"name":"South Sudan","code":"ss"},{"name":"Spain","code":"es"},{"name":"Sri Lanka","code":"lk"},{"name":"Sudan","code":"sd"},{"name":"Suriname","code":"sr"},{"name":"Sweden","code":"se"},{"name":"Switzerland","code":"ch"},{"name":"Syrian Arab Republic","code":"sy"},{"name":"Taiwan","code":"tw"},{"name":"Tajikistan","code":"tj"},{"name":"Tanzania, United Republic of","code":"tz"},{"name":"Thailand","code":"th"},{"name":"Timor-Leste","code":"tl"},{"name":"Togo","code":"tg"},{"name":"Tokelau","code":"tk"},{"name":"Tonga","code":"to"},{"name":"Trinidad and Tobago","code":"tt"},{"name":"Tunisia","code":"tn"},{"name":"Turkey","code":"tr"},{"name":"Turkmenistan","code":"tm"},{"name":"Turks and Caicos Islands","code":"tc"},{"name":"Tuvalu","code":"tv"},{"name":"Uganda","code":"ug"},{"name":"Ukraine","code":"ua"},{"name":"United Arab Emirates","code":"ae"},{"name":"United Kingdom","code":"gb"},{"name":"United States","code":"us"},{"name":"United States Minor Outlying Islands","code":"um"},{"name":"Uruguay","code":"uy"},{"name":"Uzbekistan","code":"uz"},{"name":"Vanuatu","code":"vu"},{"name":"Venezuela, Bolivarian Republic of","code":"ve"},{"name":"Vietnam","code":"vn"},{"name":"Virgin Islands, British","code":"vg"},{"name":"Virgin Islands, U.S.","code":"vi"},{"name":"Wallis and Futuna","code":"wf"},{"name":"Western Sahara","code":"eh"},{"name":"Yemen","code":"ye"},{"name":"Zambia","code":"zm"},{"name":"Zimbabwe","code":"zw"}]
lan_ctr = [['ps', ['af', 'pk']], ['fa', ['af', 'ir']], ['uz', ['af', 'uz']], ['sv', ['ax', 'fi', 'se']], ['sq', ['al', 'xk', 'mk']], ['en', ['us','gb','nz','ca','au']], ['ar', ['dz', 'bh', 'td', 'km', 'dj', 'eg', 'er', 'iq', 'il', 'jo', 'kw', 'lb', 'ly', 'mr', 'ma', 'om', 'ps', 'qa', 'sa', 'so', 'ss', 'sd', 'sy', 'tn', 'ae', 'eh', '001', 'ye']], ['fr', ['fr']], ['kab', ['dz']], ['ca', ['ad', 'fr', 'it', 'es']], ['ln', ['ao', 'cf', 'cg', 'cd']], ['pt', ['ao', 'br', 'cv', 'gq', 'fr', 'gw', 'lu', 'mo', 'mz', 'pt', 'st', 'ch', 'tl']], ['es', ['ai', 'ag', 'ar', 'aw', 'bs', 'bb', 'bz', 'bm', 'bo', 'br', 'vg', 'ca', 'ic', 'bq', 'ky', 'ea', 'cl', 'co', 'cr', 'cu', 'cw', 'dm', 'do', 'ec', 'sv', 'gq', 'fk', 'gf', 'gl', 'gd', 'gp', 'gt', 'gy', 'ht', 'hn', '419', 'mq', 'mx', 'ms', 'ni', 'pa', 'py', 'pe', 'ph', 'pr', 'sx', 'es', 'bl', 'kn', 'lc', 'mf', 'pm', 'vc', 'sr', 'tt', 'tc', 'vi', 'us', 'uy', 've']], ['hy', ['am']], ['nl', ['aw', 'be', 'bq', 'cw', 'nl', 'sx', 'sr']], ['de', ['de']], ['az', ['az']], ['bn', ['bd', 'in']], ['ccp', ['bd', 'in']], ['be', ['by']], ['ru', ['by', 'kz', 'kg', 'md', 'ru', 'ua']], ['wa', ['be']], ['yo', ['bj', 'ng']], ['dz', ['bt']], ['qu', ['bo', 'ec', 'pe']], ['bs', ['ba']], ['hr', ['ba', 'hr']], ['sr', ['ba', 'xk', 'me', 'rs']], ['tn', ['bw', 'za']], ['ms', ['bn', 'my', 'sg']], ['bg', ['bg']], ['ff', ['bf', 'cm', 'gm', 'gh', 'gw', 'gn', 'lr', 'mr', 'ne', 'ng', 'sn', 'sl']], ['rn', ['bi']], ['km', ['kh']], ['agq', ['cm']], ['ksf', ['cm']], ['bas', ['cm']], ['dua', ['cm']], ['ewo', ['cm']], ['kkj', ['cm']], ['nmg', ['cm']], ['mgo', ['cm']], ['mua', ['cm']], ['nnh', ['cm']], ['jgo', ['cm']], ['yav', ['cm']], ['iu', ['ca']], ['moh', ['ca']], ['kea', ['cv']], ['sg', ['cf']], ['arn', ['cl']], ['yue', ['cn', 'hk']], ['zh', ['cn', 'hk', 'mo', 'sg', 'tw']], ['ii', ['cn']], ['bo', ['cn', 'in']], ['ug', ['cn']], ['lu', ['cd']], ['sw', ['cd', 'ke', 'tz', 'ug']], ['el', ['cy', 'gr']], ['tr', ['cy', 'tr']], ['cs', ['cz']], ['da', ['dk', 'gl']], ['fo', ['dk', 'fo']], ['so', ['dj', 'et', 'ke', 'so']], ['byn', ['er']], ['gez', ['er', 'et']], ['tig', ['er']], ['ti', ['er', 'et']], ['et', ['ee']], ['ss', ['sz', 'za']], ['am', ['et']], ['om', ['et', 'ke']], ['wal', ['et']], ['fi', ['fi']], ['smn', ['fi']], ['se', ['fi', 'no', 'se']], ['br', ['fr']], ['co', ['fr']], ['oc', ['fr']], ['gsw', ['fr', 'li', 'ch']], ['ka', ['ge']], ['os', ['ge', 'ru']], ['ksh', ['de']], ['nds', ['de', 'nl']], ['dsb', ['de']], ['hsb', ['de']], ['ak', ['gh']], ['ee', ['gh', 'tg']], ['gaa', ['gh']], ['ha', ['gh', 'ne', 'ng']], ['kl', ['gl']], ['kpe', ['gn', 'lr']], ['nqo', ['gn']], ['hu', ['hu']], ['is', ['is']], ['as', ['in']], ['brx', ['in']], ['gu', ['in']], ['hi', ['in']], ['kn', ['in']], ['ks', ['in']], ['kok', ['in']], ['ml', ['in']], ['mni', ['in']], ['mr', ['in']], ['ne', ['in', 'np']], ['or', ['in']], ['pa', ['in', 'pk']], ['sa', ['in']], ['sat', ['in']], ['ta', ['in', 'my', 'sg', 'lk']], ['te', ['in']], ['ur', ['in', 'pk']], ['id', ['id']], ['jv', ['id']], ['ckb', ['ir', 'iq']], ['mzn', ['ir']], ['lrc', ['ir', 'iq']], ['syr', ['iq', 'sy']], ['ga', ['ie']], ['gv', ['im']], ['he', ['il']], ['fur', ['it']], ['it', ['it', 'sm', 'ch', 'va']], ['sc', ['it']], ['scn', ['it']], ['ja', ['jp']], ['kk', ['kz']], ['ebu', ['ke']], ['guz', ['ke']], ['kln', ['ke']], ['kam', ['ke']], ['ki', ['ke']], ['luo', ['ke']], ['luy', ['ke']], ['mas', ['ke', 'tz']], ['mer', ['ke']], ['saq', ['ke']], ['dav', ['ke']], ['teo', ['ke', 'ug']], ['ky', ['kg']], ['lo', ['la']], ['lv', ['lv']], ['st', ['ls', 'za']], ['vai', ['lr']], ['lt', ['lt']], ['lb', ['lu']], ['mg', ['mg']], ['ny', ['mw']], ['dv', ['mv']], ['bm', ['ml']], ['khq', ['ml']], ['ses', ['ml']], ['mt', ['mt']], ['mfe', ['mu']], ['ro', ['md', 'ro']], ['mn', ['mn']], ['tzm', ['ma']], ['zgh', ['ma']], ['shi', ['ma']], ['mgh', ['mz']], ['seh', ['mz']], ['my', ['mm']], ['af', ['na', 'za']], ['naq', ['na']], ['fy', ['nl']], ['mi', ['nz']], ['twq', ['ne']], ['dje', ['ne']], ['ig', ['ng']], ['kaj', ['ng']], ['kcg', ['ng']], ['ko', ['kp', 'kr']], ['mk', ['mk']], ['nb', ['no', 'sj']], ['nn', ['no']], ['sd', ['pk']], ['gn', ['py']], ['ceb', ['ph']], ['fil', ['ph']], ['pl', ['pl']], ['ba', ['ru']], ['ce', ['ru']], ['cv', ['ru']], ['myv', ['ru']], ['sah', ['ru']], ['tt', ['ru']], ['rw', ['rw']], ['dyo', ['sn']], ['wo', ['sn']], ['sk', ['sk']], ['sl', ['si']], ['nso', ['za']], ['nr', ['za']], ['ts', ['za']], ['ve', ['za']], ['xh', ['za']], ['zu', ['za']], ['nus', ['ss']], ['ast', ['es']], ['eu', ['es']], ['gl', ['es']], ['si', ['lk']], ['rm', ['ch']], ['wae', ['ch']], ['trv', ['tw']], ['tg', ['tj']], ['asa', ['tz']], ['bez', ['tz']], ['lag', ['tz']], ['jmc', ['tz']], ['kde', ['tz']], ['rof', ['tz']], ['rwk', ['tz']], ['sbp', ['tz']], ['ksb', ['tz']], ['vun', ['tz']], ['th', ['th']], ['to', ['to']], ['ku', ['tr']], ['tk', ['tm']], ['cgg', ['ug']], ['lg', ['ug']], ['nyn', ['ug']], ['xog', ['ug']], ['uk', ['ua']], ['kw', ['gb']], ['gd', ['gb']], ['cy', ['gb']], ['chr', ['us']], ['haw', ['us']], ['lkt', ['us']], ['vi', ['vn']], ['eo', ['001']], ['io', ['001']], ['ia', ['001']], ['jbo', ['001']], ['bem', ['zm']], ['nd', ['zw']], ['sn', ['zw']]]

logger = logging.getLogger(__name__)

class custom_session(requests.Session):
    """Custom session class inheriting from requests.Session.

    This class provides per-instance rate limiting, automatic retry for
    certain error codes, and a default timeout.

    Attributes:
        DEFAULT_TIMEOUT (int): Default timeout for requests.
        RETRY_CODES (list): List of HTTP status codes to be retried.
        MAX_RETRIES (int): Maximum number of retries.
        GET_RATE_LIMIT (float): Time (in seconds) to wait between GET requests.
        POST_RATE_LIMIT (float): Time (in seconds) to wait between POST requests.
        last_request_time (float): Timestamp of the last request made.
    """

    def __init__(self,
                 timeout=60,
                 retry_codes=[429, 503],
                 max_retries=3,
                 get_rate_limit=5,
                 post_rate_limit=5):
        """Initialize a new CustomSession instance.

        Args:
            timeout (int): Default timeout for requests.
            retry_codes (list): List of HTTP status codes to be retried.
            max_retries (int): Maximum number of retries.
            get_rate_limit (float): Time (in seconds) to wait between GET requests.
            post_rate_limit (float): Time (in seconds) to wait between POST requests.
        """
        super(custom_session, self).__init__()

        self.DEFAULT_TIMEOUT = timeout
        self.RETRY_CODES = retry_codes
        self.MAX_RETRIES = max_retries
        self.GET_RATE_LIMIT = get_rate_limit
        self.POST_RATE_LIMIT = post_rate_limit
        self.last_request_time = 0

    def request(self, method, url, **kwargs):
        """Override the request method to include rate limiting, retries, and default timeout.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            url (str): URL to send the request to.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            response: Response object returned from the request.
        """
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT

        # Ensure rate limiting
        elapsed_time = time.time() - self.last_request_time
        if method == 'GET' and elapsed_time < self.GET_RATE_LIMIT:
            time.sleep(self.GET_RATE_LIMIT - elapsed_time)
        elif method == 'POST' and elapsed_time < self.POST_RATE_LIMIT:
            time.sleep(self.POST_RATE_LIMIT - elapsed_time)

        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                response = super(custom_session, self).request(method, url, **kwargs)

                self.last_request_time = time.time()

                if response.status_code in self.RETRY_CODES:
                    logger.error(f"request error: {response.status_code} - retrying...")
                    retries += 1
                    if method == 'GET':
                        time.sleep(self.GET_RATE_LIMIT)
                    elif method == 'POST':
                        time.sleep(self.POST_RATE_LIMIT)
                    continue

                return response

            except requests.RequestException as e:
                logger.error(f"request error: {e}")
                retries += 1
                if method == 'GET':
                    time.sleep(self.GET_RATE_LIMIT)
                elif method == 'POST':
                    time.sleep(self.POST_RATE_LIMIT)

        logger.error(f"failed to fetch URL {url} after {self.MAX_RETRIES} attempts")
        return None

    def get(self, url, **kwargs):
        """Override the GET method to use the custom request method.

        Args:
            url (str): URL to send the GET request to.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            response: Response object returned from the GET request.
        """
        return self.request('GET', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Override the POST method to use the custom request method.

        Args:
            url (str): URL to send the POST request to.
            data (dict, optional): Data to send in the POST request.
            json (dict, optional): JSON data to send in the POST request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            response: Response object returned from the POST request.
        """
        return self.request('POST', url, data=data, json=json, **kwargs)
