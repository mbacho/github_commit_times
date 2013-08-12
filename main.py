#!/usr/bin/env python

from getopt import getopt
from getopt import GetoptError

from sys import argv
from sys import exit
from sys import stdout

from lib.fetcher import  process_repo
from lib.fetcher import  write_commits
from lib.fetcher import  extract_commits
from lib.fetcher import  get_full_url

from lib.fetcher import  USER_REPO_LIST
from lib.fetcher import  REPO_URL
from lib.fetcher import  ALL_REPO_LIST


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

