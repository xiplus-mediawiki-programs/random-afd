# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import re
import sys
import time
import uuid
from datetime import datetime

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
from pywikibot.data.api import Request
from pywikibot.pagegenerators import RandomPageGenerator

os.environ['TZ'] = 'UTC'


class RandomAfd:
    def __init__(self, args):
        self.args = args

        self.site = pywikibot.Site()
        self.site.login()

        self.logger = logging.getLogger('random_afd')
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def _get_afd_text(self, title):
        return '''
== [[:{}]] ==
{{{{刪除}}}}理據：XXX
: 提交的維基人及時間：~~~~
'''.format(title)

    def _get_fame_text(self, title):
        return '''
=== [[:{0}]] ===
{{{{Findsources|{0}}}}}
:{{{{意見}}}}：XXXX。--~~~~
'''.format(title)

    def _mark_afd(self, title):
        if not self.args.vfd:
            return
        page = pywikibot.Page(self.site, title)
        text = page.text
        text = re.sub(r'{{vfd\|.*}}\n?', '', text)
        text = '{{vfd|Test|a|date=' + self.args.date + '}}\n' + text
        page.text = text
        summary = 'random-afd：提交存廢討論'
        page.save(summary=summary, minor=False)

    def main(self):
        self.logger.info('start')

        if not re.search(r'^\d{4}/\d{2}/\d{2}$', self.args.date):
            self.logger.error('invalid date format')
            return

        text = '{{subst:AfdHead}}\n'

        argdict = vars(args)
        total_pages = 0
        for i in range(1, 6):
            total_pages += argdict[f'n{i}']

        pages = RandomPageGenerator(total=total_pages, site=self.site, namespaces=[0])
        for _ in range(self.args.n1):
            page = next(pages)
            text += self._get_afd_text(page.title())
            self._mark_afd(page.title())

        if self.args.n2 > 0:
            text += '''
==30天后仍掛有{{tl|notability}}模板的條目==
<span style="font-size:smaller;">(已掛[[template:notability|關注度模板]]30天)</span>
'''
        for _ in range(self.args.n2):
            page = next(pages)
            text += self._get_fame_text(page.title())
            self._mark_afd(page.title())
        if self.args.n2 > 0:
            text += '''
<!-- Twinkle: User:{{subst:REVISIONUSER}} 的 fame 提刪插入點，請勿變更或移除此行，除非不再於此頁提刪 -->
----
:{{删除}}理據：沒有足夠的可靠資料來源能夠讓這個條目符合[[Wikipedia:關注度]]中的標準
提报以上<u>关注度不足</u>条目的維基人及時間：<br id="no-new-title" />~~~~
'''

        for _ in range(self.args.n3):
            page = next(pages)
            text += self._get_afd_text(page.title())
            self._mark_afd(page.title())

        if self.args.n4 > 0:
            text += '''
==批量提刪==
'''
        for _ in range(self.args.n4):
            page = next(pages)
            text += self._get_fame_text(page.title())
            self._mark_afd(page.title())
        if self.args.n4 > 0:
            text += '''
<!-- Twinkle: User:{{subst:REVISIONUSER}} 的 batch 提刪插入點，請勿變更或移除此行，除非不再於此頁提刪 -->
----
:{{删除}}理據：Test
提报以上頁面的維基人及時間：<br id="no-new-title" />~~~~
'''

        for _ in range(self.args.n5):
            page = next(pages)
            text += self._get_afd_text(page.title())
            self._mark_afd(page.title())

        afd_page = pywikibot.Page(self.site, 'Wikipedia:頁面存廢討論/記錄/{}'.format(args.date))
        afd_page.text = text
        summary = 'random-afd：產生存廢討論列表'
        afd_page.save(summary=summary, minor=False)

        self.logger.info('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('date')
    parser.add_argument('--n1', type=int, default=3)
    parser.add_argument('--n2', type=int, default=5)
    parser.add_argument('--n3', type=int, default=3)
    parser.add_argument('--n4', type=int, default=3)
    parser.add_argument('--n5', type=int, default=3)
    parser.add_argument('--vfd', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    random_afd = RandomAfd(args)
    random_afd.logger.setLevel(args.loglevel)
    random_afd.logger.debug('args: %s', args)
    random_afd.main()
