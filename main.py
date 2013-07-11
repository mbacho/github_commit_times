#!/usr/bin/env python

from getopt import getopt
from getopt import GetoptError

from sys import argv
from sys import exit
from sys import stdout

from lib import stuff

from urllib2 import urlopen
from json import loads

from csv import writer
from csv import QUOTE_MINIMAL

BASE_URL = "https://api.github.com/"

USER_URL = "users/{user}"
USER_REPO_LIST = "users/{user}/repos"

REPO_URL = "repos/{full_name}"
ALL_REPO_LIST = "repositories"

REPO_COMMIT_LIST = "repos/{full_name}/commits"#"/repos/{owner}/{repo}/commits"


def get_full_url(part_url):
    """Append base url to partial url"""
    return BASE_URL + part_url


def helpme(app_name):
    """Help for this program"""
    print "\nUsage : {0} [-h] [-u|r][user|repo] [-l]".format(app_name)
    print "-h --help   Show this help"
    print "-u --user   Get commit stats for the user"
    print "-r --repo   Get commit stats for the repo."
    print "Repo name is of the form 'user/repo' when the user isn't specified via -u"
    print "Repo name is of the form 'repo' when the user is specified via -u"
    print "-l --log    Log commit stats to file"
    print "If user and repo are not specified, defaults to all repositories"
    print "If both user and repo are specified, the repo would be assumed to be "
    exit()


def game_over(msg, code=1):
    """Exit program, cleanup if needed. Usually done on errors to display message and exit"""
    print msg
    exit(code)


def get_from_net(url):
    """Return string from net resource"""
    print 'opening', url
    ty = urlopen(url)
    print 'reading...'
    s = ty.read()
    print 'done'
    return s


def extract_commits(repo_obj):
    url = REPO_COMMIT_LIST.format(full_name=repo_obj['full_name'])
    url = get_full_url(url)
    json_data = loads(get_from_net(url))
    commits = []
    for i in json_data:
        committer = i['committer']
        comm = {#TODO Fetch user's location in USER_URL
                'date': i['commit']['committer']['date'],
                'user': i['commit']['committer']['name'],
                'login': ''
        }
        if committer is not None:
            comm['login'] = committer['login']

        commits.append(comm)
    return commits


def process_repo(url, multiple=False):
    json_data = loads(get_from_net(url))
    if not multiple: json_data = [json_data]
    repo_dets = []
    for i in json_data:
        dets = {
            'full_name': i['full_name'],
            'name': i['name'],
            'fork': i['fork'],
            'url': i['url'],
            'language':'',
            'created':''
        }
        if 'language' in i: dets['language'] = i['language']
        if 'created_at' in i: dets['created'] = i['created_at']
        repo_dets.append(dets)
    return repo_dets


def main(user='', repo='', logfile=''):
    """Entry point"""
    repo_url = ''
    single_repo = False #flag : if fetching one repo (True) or many (False)
    if user != '' and repo != '':
        fullname = "{0}/{1}".format(user, repo)
        repo_url = REPO_URL.format(full_name=fullname)
        single_repo = True
    elif user != '':
        repo_url = USER_REPO_LIST.format(user=user)
        single_repo = False
    elif repo != '':
        repo_url = REPO_URL.format(full_name=repo)
        single_repo = True
    else:
        ans = raw_input('fetch all repos [y/n]? ')
        if ans in ('y', 'Y'):
            repo_url = ALL_REPO_LIST
            single_repo = False
        else:
            game_over('no repo/user selected')

    repo_url = get_full_url(repo_url)
    repo_dets = None
    if single_repo:
        repo_dets = process_repo(repo_url)
    else:
        repo_dets = process_repo(repo_url, multiple=True)

    if logfile == '': #TODO use reponame if logfile is not present
        logfile = stdout
    else:
        logfile = open(logfile, 'w')

    if type(logfile) is not file:
        game_over('nowhere to log')

    print 'gotten',len(repo_dets),'repos'
    csv__writer = writer(logfile, delimiter=',', quoting=QUOTE_MINIMAL)
    #output format : reponame, language, committer, login, time
    csv__writer.writerow(['reponame','language', 'committer', 'login', 'time'])

    for i in repo_dets:
        commits = extract_commits(i)
        #TODO when reading this file, skip first row
        for c in commits:
            try:
                csv__writer.writerow([
                    i['full_name'],
                    i['language'],
                    c['user'],
                    c['login'],
                    c['date']
                ])
            except UnicodeEncodeError, ue:
                #TODO Handle unicode errors since csv lib doesn't like work with unicode
                print str(ue)
                continue

    if logfile != stdout: logfile.close()


if __name__ == '__main__':

    check_user = ''
    check_repo = ''
    log_file = ''

    long_opts = ['--help', '--user=', '--repo=', '--logfile=']
    short_opts = 'hu:r:l:'

    try:
        opts, args = getopt(argv[1:], short_opts, long_opts)

        for i, j in opts:
            if i in ('-h', '--help'):
                helpme(argv[0])
            elif i in ('-u', '--user'):
                check_user = j
            elif i in ('-r', '--repo'):
                check_repo = j
            elif i in ('-l', '--logfile'):
                log_file = j
            else:
                game_over('Unknown option : {0}'.format(i))
    except GetoptError, e:
        game_over(str(e))

    except BaseException, e:
        game_over(str(e))

    if check_repo != '' or check_user != '':
        main(repo=check_repo, user=check_user, logfile=log_file)
    else:
        main(logfile=log_file)

