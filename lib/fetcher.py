__author__ = 'erico'

from sys import exit

from urllib2 import urlopen
from urllib2 import HTTPError
from json import loads

from csv import writer
from csv import QUOTE_MINIMAL

from lib import BASE_URL
from lib import RAW_COMMIT
from lib import REPO_COMMIT_LIST
from lib import COMMIT_DETAILS


class Fetcher(object):
    """
    Fetch data from github
    """

    def get_full_url(self, part_url):
        """Append base url to partial url"""
        return BASE_URL + part_url


    def get_from_net(self, url):
        """Return string from net resource
        :param url:
        """
        print 'opening', url
        ty = urlopen(url)
        print 'reading...'
        s = ty.read()
        print 'done'
        return s


    def get_commit_datetimezone(self, html_url):
        url = RAW_COMMIT.format(commit_href=html_url)
        print 'getting tz for [{0}]'.format(url)
        try:
            raw_commit = urlopen(url)
            raw_commit.readline()  #skip first line
            raw_commit.readline()  #skip second line
            date_info = raw_commit.readline()
            return date_info[6:-1]
        except HTTPError, e:
            print 'error for', url
            print str(e)
            return ''

    def get_commit_change_stats(self, commit_url='', full_name='', commit_sha=''):
        """
        Gets stats about additions and deletions
        Commit url to be used can be set via commit_url or generated using both full_name and commit_sha
        If all parameters are set, commit_url will be used, the others ignored

        :param commit_url Absolute path to commit
        :param full_name Full name of repo i.e. user/reponame
        :param commit_sha Sha of the commit

        :returns dictionary with 'additions', 'deletions' as keys
        """
        if commit_url == '' and (commit_sha == '' and full_name == ''):
            raise BaseException('commit url could not be generated. Commit url, commit sha and full name not set')
            return None
        url = commit_url
        if url == '':
            url = COMMIT_DETAILS.format(commit_sha=commit_sha, full_name=full_name)
            url = self.get_full_url(url)

        json_data = loads(self.get_from_net(url))
        stats = {'additions': 0, 'deletions': 0}
        if 'stats' in json_data:
            stats['additions'] = json_data['stats']['additions']
            stats['deletions'] = json_data['stats']['deletions']

        return stats

    def extract_commits(self, repo_obj):
        """Extract repo commits from details in the repo object"""
        url = REPO_COMMIT_LIST.format(full_name=repo_obj['full_name'])
        url = self.get_full_url(url)
        json_data = loads(self.get_from_net(url))
        commits = []
        for i in json_data:
            committer = i['committer']
            #stats = self.get_commit_change_stats(full_name=repo_obj['full_name'], commit_sha=i['sha'])
            stats = self.get_commit_change_stats(commit_url=i['url'])
            comm = {#TODO Fetch user's location in USER_URL
                    'date': self.get_commit_datetimezone(i['html_url']),
                    'user': i['commit']['committer']['name'],
                    'login': '',
                    'additions': stats['additions'],
                    'deletions': stats['deletions']
            }
            if committer is not None:
                comm['login'] = committer['login']

            commits.append(comm)
        return commits


    def write_commits(self, logfile, repo, commits):
        """
        write csv to file in the format given below
        output format : reponame, language, committer, login, time + timezone, additions, deletions
        """
        csv__writer = writer(logfile, delimiter=',', quoting=QUOTE_MINIMAL)

        for c in commits:
            try:
                csv__writer.writerow([
                    repo['full_name'],
                    repo['language'],
                    c['user'],
                    c['login'],
                    c['date'],
                    c['additions'],
                    c['deletions']
                ])
            except UnicodeEncodeError, ue:
                #TODO Handle unicode errors since csv lib doesn't like to work with unicode
                print str(ue)
                continue


    def process_repo(self, url, multiple=False):
        """Return an array of repo details. If url is for one repo, the result is an array of one element"""
        json_data = loads(self.get_from_net(url))
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
