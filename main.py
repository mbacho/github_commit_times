#!/usr/bin/env python

from getopt import getopt
from getopt import GetoptError

from sys import argv
from sys import exit
from sys import stdout

from urllib2 import urlopen
from urllib2 import  HTTPError
from json import loads

from csv import writer
from csv import QUOTE_MINIMAL


BASE_URL = "https://api.github.com/"

USER_URL = "users/{user}"
USER_REPO_LIST = "users/{user}/repos"

REPO_URL = "repos/{full_name}"
ALL_REPO_LIST = "repositories"

REPO_COMMIT_LIST = "repos/{full_name}/commits"#"/repos/{owner}/{repo}/commits"
RAW_COMMIT = "{commit_href}.patch"

def get_full_url(part_url):
    """Append base url to partial url"""
    return BASE_URL + part_url


def helpme(app_name):
    """Help for this program"""
    print "\nUsage : {0} [-h] [-u|r][user|repo] [-l][logfile] [-c]".format(app_name)
    print "-h --help   Show this help"
    print "-u --user   Get commit stats for the user"
    print "-r --repo   Get commit stats for the repo."
    print "-c --csv    Log data in file as csv. If not specified, defaults to json"
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
    """Return string from net resource
    :param url:
    """
    print 'opening', url
    ty = urlopen(url)
    print 'reading...'
    s = ty.read()
    print 'done'
    return s


def get_commit_datetimezone(html_url):
    url = RAW_COMMIT.format(commit_href=html_url)
    print 'getting tz for [{0}]'.format(url)
    try:
        raw_commit = urlopen(url)
        raw_commit.readline()  #skip first line
        raw_commit.readline()  #skip second line
        date_info = raw_commit.readline()
        return date_info[6:-1]
    except HTTPError, e:
        print 'error for',url
        print str(e)
        return ''


def extract_commits(repo_obj):
    """Extract repo commits from details in the repo object"""
    url = REPO_COMMIT_LIST.format(full_name=repo_obj['full_name'])
    url = get_full_url(url)
    json_data = loads(get_from_net(url))
    commits = []
    for i in json_data:
        committer = i['committer']
        comm = {#TODO Fetch user's location in USER_URL
                'date' :  get_commit_datetimezone(i['html_url']),
                'user': i['commit']['committer']['name'],
                'login': ''
                #TODO get commit's html_url then append '.patch' then get third line with timezone info
                #TODO load date string into datetime with format e.g. mm-yy-tt
        }
        if committer is not None:
            comm['login'] = committer['login']

        commits.append(comm)
    return commits


def write_commits(logfile, repo, commits):
    csv__writer = writer(logfile, delimiter=',', quoting=QUOTE_MINIMAL)
    #output format : reponame, language, committer, login, time, timezone
    #csv__writer.writerow(['reponame', 'language', 'committer', 'login', 'time'])

    for c in commits:
        try:
            csv__writer.writerow([
                repo['full_name'],
                repo['language'],
                c['user'],
                c['login'],
                c['date'],
            ])
        except UnicodeEncodeError, ue:
            #TODO Handle unicode errors since csv lib doesn't like to work with unicode
            print str(ue)
            continue


def process_repo(url, multiple=False):
    """Return an array of repo details. If url is for one repo, the result is an array of one element"""
    json_data = loads(get_from_net(url))
    if not multiple: json_data = [json_data]
    repo_dets = []
    for i in json_data:
        dets = {
            'full_name': i['full_name'],
            'name': i['name'],
            'fork': i['fork'],
            'url': i['url'],
            'language': '',
            'created': ''
        }
        if 'language' in i: dets['language'] = i['language']
        if 'created_at' in i: dets['created'] = i['created_at']
        repo_dets.append(dets)
    return repo_dets


def main(user='', repo='', logfile='', frmt='json'):
    """Entry point
    :param user:
    :param repo:
    :param logfile:
    :param frmt:
    """
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

    print 'gotten', len(repo_dets), 'repos'

    for i in repo_dets:
        commits = extract_commits(i)
        write_commits(logfile, i, commits) #TODO write file in JSON

    if logfile != stdout:
        logfile.close()


if __name__ == '__main__':
    check_user = ''
    check_repo = ''
    log_file = ''
    to_csv = False
    long_opts = ['--help', '--user=', '--repo=', '--logfile=', '--csv']
    short_opts = 'hu:r:l:c'

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
            elif i in ('-c', '--csv'):
                to_csv = True
            else:
                game_over('Unknown option : {0}'.format(i))
    except GetoptError, e:
        game_over(str(e))

    except BaseException, e:
        game_over(str(e))

    frmt = 'json'
    if to_csv:
        frmt = 'csv'

    if check_repo != '' or check_user != '':
        main(repo=check_repo, user=check_user, logfile=log_file, frmt=frmt)
    else:
        main(logfile=log_file, frmt=frmt)

