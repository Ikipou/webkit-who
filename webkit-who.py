#!/usr/bin/python

import re
import subprocess
import operator


def parse_log(since='6 months ago'):
    """Parse the commit log, yielding (date, author email) pairs.

    Parser is WebKit-aware: it knows the committer frequently isn't
    the author.

    |since| is an argument for the --since flag to git log.
    """

    commit_re = re.compile('^commit ')
    author_re = re.compile('^Author: (\S+)')
    date_re = re.compile('^Date:\s+(\S+)')
    # Regexp for a ChangeLog header: date + author name + author email.
    changelog_re = re.compile('^    \d\d\d\d-\d\d-\d\d  .+?  <(.+?)>')

    log = subprocess.Popen(['git', 'log', '--date=short', '--since=' + since],
                           stdout=subprocess.PIPE)
    n = 0
    for line in log.stdout.xreadlines():
        if commit_re.match(line):
            if n > 0:
                yield date, author
            author = None
            date = None
            n += 1
            continue
        match = author_re.match(line)
        if match:
            author = match.group(1)
            continue
        match = date_re.match(line)
        if match:
            date = match.group(1)
            continue
        match = changelog_re.match(line)
        if match:
            author = match.group(1)
            continue

# See:  http://trac.webkit.org/wiki/WebKit%20Team

domain_companies = {
    'chromium.org': 'google',
    'google.com': 'google',
    'apple.com': 'apple',
    'igalia.com': 'igalia',
    'nokia.com': 'nokia',
    'torchmobile.com.cn': 'torch mobile',
    'torchmobile.com': 'torch mobile',
    'rim.com': 'rim',
}

other = {
    'google': [
        'abarth',
        'abarth@webkit.org',
        'antonm@chromium',
        'christian.plesner.hansen@gmail.com',  # v8
        'eric@webkit.org',
        'finnur.webkit@gmail.com',
        'jens@mooseyard.com',
        'joel@jms.id.au',  # intern
        'kinuko@chromium.com',
        'rniwa@webkit.org',  # intern
        'shinichiro.hamaji@gmail.com',
        'yaar@chromium.src',
    ],

    'apple': [
        'ap@webkit.org',
        'sam@webkit.org',
    ],

    'redhat': [
        'danw@gnome.org',
        'otte@webkit.org',
    ],

    'nokia': [
        'hausmann@webkit.org',

        'kenneth@webkit.org',
        'kenneth.christiansen@openbossa.org',

        'tonikitoo@webkit.org',
        'antonio.gomes@openbossa.org',

        'vestbo@webkit.org',

        'faw217@gmail.com',  # A guess, based on commits.

        'girish@forwardbias.in',  # Appears to be consulting for Qt = Nokia(?).
    ],

    'rim': [
        'dbates@webkit.org',
        'dbates@intudata.com',
        'zimmermann@webkit.org',
    ],

    'misc (e.g. open source)': [
        'becsi.andras@stud.u-szeged.hu',
        'bfulgham@webkit.org',  # WinCairo
        'chris.jerdonek@gmail.com',  # Seems to be doing random script cleanups?
        'jmalonzo@webkit.org',  # GTK
        'joanmarie.diggs@gmail.com',  # GTK Accessibility (Sun?)
        'joepeck@webkit.org',   # Inspector.
        'joepeck02@gmail.com',   # Inspector.
        'krit@webkit.org',
        'ossy@webkit.org',
        'simon.maxime@gmail.com',  # Haiku
        'skyul@company100.net',  # BREWMP
        'zandobersek@gmail.com',  # GTK
        'zecke@webkit.org',  # GTK+Qt
        'zecke@selfish.org',  # GTK+Qt
        'zoltan@webkit.org',
        'hzoltan@inf.u-szeged.hu',
        'christian@twotoasts.de',  # GTK, Midori
    ]
}

people_companies = {
    'mike@belshe.com': 'google',
    'martin.james.robinson@gmail.com': 'appcelerator',

    'xan@webkit.org': 'igalia',
    'xan@gnome.org': 'igalia',

    'kevino@webkit.org': 'wx',
    'kevino@theollivers.com': 'wx',

    'gustavo.noronha@collabora.co.uk': 'collabora',
    'kov@webkit.org': 'collabora',
    'gns@gnome.org': 'collabora',

    'ariya.hidayat@gmail.com': 'qualcomm',
    'ariya@webkit.org': 'qualcomm',
}


def classify_email(email):
    """Given an email, return a string identifying their company."""
    company = None
    user = domain = None
    if '@' in email:
        user, domain = email.split('@')
    if domain:
        if domain in domain_companies:
            return domain_companies[domain]
        if domain.endswith('google.com'):
            return 'google'
    if email in people_companies:
        return people_companies[email]

    for company, people in other.iteritems():
        if email in people:
            return company

    unknown[email] = count
    return 'unknown'


counts = {}
for date, author in parse_log():
    counts[author] = counts.get(author, 0) + 1

print counts
companies = {}
unknown = {}
for email, count in counts.iteritems():
    company = classify_email(email)
    companies[company] = companies.get(company, 0) + count

if unknown:
    print 'unclassified:'
    for email, count in sorted(unknown.iteritems(), key=operator.itemgetter(1),
                               reverse=True):
        print '  %s (%d)' % (email, count)


for company, count in sorted(companies.iteritems(), key=operator.itemgetter(1),
                             reverse=True):
    print '%s: %d' % (company, count)

