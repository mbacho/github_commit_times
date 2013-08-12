__author__ = 'erico'

"""Functions to fetch data from github"""


from sys import exit

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