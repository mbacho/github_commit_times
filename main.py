#!/usr/bin/env python

from getopt import  getopt
from getopt import GetoptError

from sys import argv
from sys import exit

from lib import stuff

BASE_URL = "https://api.github.com/"

USER_URL = "users/{userid}"
USER_REPOS = "users/{userid}/repos"

REPO_URL = "repos/{full_name}"
ALL_REPOS = "repositories"

REPO_COMMITS = "/repos/{owner}/{repo}/commits"


def get_full_url(part_url):
    """Append base url to partial url"""
    return BASE_URL + part_url


def helpme(app_name):
    """Help for this program"""
    print "\nUsage : {0} [-h] [-u|r][user|repo] [-l]".format(app_name)
    print "-h --help   Show this help"
    print "-u --user   Get commit stats for the user"
    print "-r --repo   Get commit stats for the repo"
    print "-l --log    Log commit stats to file"
    print "If user and repo are not specified, defaults to all repositories"
    exit()

def game_over(msg, code=1):
    """Exit program, cleanup if needed. Usually done on errors to display message and exit"""
    print msg
    exit(code)


def main(user='', repo='',logfile=''):
    """Entry point"""
    if user=='' and repo=='':
        game_over('username or repo not set')


if __name__ == '__main__':
    if len(argv) < 2:
        game_over('try {0} -h for usage'.format(argv[0]))

    check_user = ''
    check_repo = ''
    log_file = ''

    long_opts = ['--help','--user=', '--repo=', '--logfile=']
    short_opts = 'hu:r:l'

    try:
        opts,args = getopt(argv[1:], short_opts, long_opts)

        for i,j in opts:
            if i in ('-h','--help'):
                helpme(argv[0])
            elif i in ('-u', '--user'):
                check_user = j
            elif i in ('-r', '--repo'):
                check_repo = j
            elif i in('-l','--logfile'):
                log_file = j
            else:
                game_over('Unknown option : {0}'.format(i))
    except GetoptError, e:
        game_over(str(e))

    except BaseException, e:
        game_over(str(e))

    if check_repo!='':
        main(repo=check_repo,logfile=log_file)
    elif check_user!='':
        main(user=check_user,logfile=log_file)
    else:
        main(logfile=log_file)

