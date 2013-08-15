__author__ = 'erico'

"""
Does analysis of the data
input data is of the form :


"""
from csv import reader
from time import strptime

class Analyzer(object):
    def process_file_stream(self, file_stream):
        if file_stream is None:
            raise BaseException('Stream not set')
        hours = {}
        csv_reader = reader(file_stream)
        for row in csv_reader:
            tym = self.time_from_string(row[-1])
            if tym is None: continue
            hr = str(tym.tm_hour)
            if hr in hours.keys():
                hours[hr]['count'] +=  1
                #hours[hr]['vals'].append(row)
            else:
                hours[hr] = {'count': 1}#, 'vals': [row]}
        file_stream.close()
        hrs_sort = sorted(hours, key=lambda x: x['count'], reverse=True)
        return hrs_sort
        
    def time_from_string(self, str_time):
        try:
            tym = strptime(str_time[:-6], '%a, %d %b %Y %H:%M:%S')
            return tym
        except:
            return None

    def process_file_path(self, file_path):
        if file_path == '':
            raise BaseException('File path not set')
        
        file_obj = open(file_path, 'r')
        hours = self.process_file_stream(file_obj)                
        file_obj.close()
        return hours


if __name__== '__main__':
    from sys import argv
    from sys import exit
    if len(argv) != 2:
        print 'file not set'
        exit()
        
    fpath = argv[1]
    data = Analyzer().process_file_path(fpath)
    fpath_ana = fpath+'_ana'
    f = open(fpath_ana,'w')
    f.write(str(data))
    f.close()
    print "analysis written to",fpath_ana
