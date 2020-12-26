# pretty common
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
# system
import logging
from pathlib import Path 
import sys
from datetime import datetime
import sqlite3

# mine
from lotto_scrape.mydb import dbmgr

__license__="MIT"


class lotto_scrape(object):
    '''
    '''
    def __init__(self,dbname,lottery,pg_num=1,base_url=None,logfile=None,debug=0):
        '''
        dbname: str
            name of the lotto sqlite3 database
        lottery: str
            the table name to write to, e.g. megamillions, powerball
        pg_num: int
            page number to to start the scraping
        base_url: str
            url to be scraped
        logfile: str
            name of the output logfile
        debug: int
            debug level
        '''

        self.__name__='lotto_scrape'
        _name='lottery_scrape'

        self.lottery=lottery
        self.pg_num=pg_num
        self.base_url=base_url

        # setup logging
        self.log=self._setup_log(logfile,debug)
        # initialize the database
        self.db=self._setup_db(dbname,'schema.sql')

    def call_scraper(self):
        _name=f"{self.__name__}-call_scraper"
        '''
        Call scraper method
        '''

        if self.pg_num is None:
            self.log.error(f'{_name}: self.pg_num is None')
            sys.exit(0)

        if self.base_url is None:
            self.log.error(f'{_name}: base_url needs to be set')
            sys.exit(0)

        if self.pg_num > 1: # we are going to loop to pg1 (oldest to youngest)
            pgs=[i for i in range(int(self.pg_num),0,-1)]
        else:
            pgs=[self.pg_num]

        self.log.debug(f"{_name}: self.pg_num is {self.pg_num} and pgs are {pgs}")

        for i in pgs:
            # get youngest data from database
            # self.db_most_recent(tbl_name, date_colm, return column)
            self.previous_date=datetime.strptime(
                self.db.most_recent_bydate(self.lottery,'date','date'),"%Y-%m-%d")

            self.log.debug(f'{_name}: previous date is: {self.previous_date.strftime("%Y-%m-%d")}')
            self.log.debug(f"{_name}: trying to grab page: {i}")
            self.scrape_page(i)

    def scrape_page(self,pg_num):
        _name=f"{self.__name__}-scrape_page"
        '''
        pg_num: int
            page number to pull/scrape
        '''
        try:
            url=f'{self.base_url}{str(pg_num)}'

            # setting user agent to avoid spider issues
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

            self.log.debug(f'{_name} sending requestto:\n\t{req.full_url}')

            newsoup = BeautifulSoup(urlopen(req).read(),features="lxml")
            self.parse_soup(newsoup)
        except Exception as e:
            self.log.error(f'{_name}: Error with ...\n\t{e}')
            return 0

    def parse_soup(self,soup):
        import sys
        _name=f"{self.__name__}-parse_soup"
        '''
        soup: soup
            
        Try to pull relevant data from web page and
        add to the sqlite3 dates
        '''
        rows=soup('table',{'class':'results'})[0].findAll('tr')
        for n,row in enumerate(rows):
            tds = row('td')
            print(tds)

            if tds[0].a is not None: 
                date = tds[0].a.string
                weekday, month, month_day,year=date.split(',')
                x=datetime.strptime(f'{month.strip()} {month_day.strip()} {year.strip()}','%B %d %Y')
                self.log.debug(f'{_name}: scrapped date {x} from {month} {month_day} {year}')
                
                numbers=tds[0].find_all('li')
                jackpot=tds[1].a.string.split()[0]

                if len(numbers) == 7:
                    data={'epoch': x.strftime("%s"),
                        'date': x.strftime("%Y-%m-%d"),
                        'weekday': x.strftime("%A"),
                        'num1': numbers[0].string,
                        'num2':numbers[1].string,
                        'num3':numbers[2].string,
                        'num4':numbers[3].string,
                        'num5':numbers[4].string,
                        'moneyball': numbers[5].string,
                        'jackpot': jackpot,
                        'lddate':datetime.now().strftime("%s")
                    }
                    # check that current date is more recent than
                    # previous db entries
                    if x > self.previous_date:
                        self.log.debug(f"{_name}: adding {data} to db")
                        self.db.add_rowdata(data,self.lottery)
                        self.db.commit()                    
                    else:
                        self.log.info(f"{_name}: not adding {data}, likely already in db...")

    def report(self,tbl,start,end):
        _name=f"{self.__name__}-report"
        '''
        Spew database table to screen with colored
        output. 
       
        '''
        ans=[]
        try:
            res=self.db.dbreport(tbl,start,end)
            print(f"{bcolors.HEADER}{tbl}---------------")
            for i  in res:
                out=f"{bcolors.OKGREEN}{i[1]}" # date field
                for j in [3,4,5,6,7]:
                    out+=f" {bcolors.OKBLUE}{i[j]:02d}" # number fields
                out+=f" {bcolors.RED}{i[8]:02d}" # moneyball
                out+=f" {bcolors.OKBLUE}{i[9]:4s}" # jackpot
                out+=f" {bcolors.OKGREEN}{i[2][0:3]:3s}" # date field
                print(out)
            return 1
        except Exception as e:
            self.log.error(f"{_name}: Error bc ... {e}")
            return 0

    def _setup_db(self,dbname,schema_file):
        _name=f"{self.__name__}-_setup_db"
        tbls=['megamillions','powerball'] # hardwired
        db=dbmgr(dbname,schema_file,log=self.log)
        db.read_schema_txt()
        for t in tbls:
            if not db.table_exists(t):
                self.log.debug(f"{_name}: need to make {t}")
                cmds=db.tbl_commands(t)
                try:
                    db.cur.execute(cmds)
                except Exception as e:
                    self.log.error(f"{_name}: error .. {e}")
            else:
                self.log.debug(f'{_name}: {t} tables exists in {dbname}')
        return db

    
    def _setup_log(self,logfile,debug):

        ''' Helper function to set up logging
        at the right debug level
        '''
        # INFO,DEBUG,WARN
        if debug == 0:
            loglevel="WARN"
        elif debug == 1:
            loglevel="INFO"
        else:
            loglevel="DEBUG"

        if isinstance(logfile,(logging.RootLogger)):
            log=logfile
            log.setLevel(loglevel)
        else:
            logging.basicConfig(filename=logfile, level=loglevel,
            datefmt="%Y-%j %H:%M:%S", format="%(asctime)s-%(levelname)s %(message)s")
            log=logging.getLogger(__name__)

            if debug > 1 and not log.manager.loggerDict: # this has logs also dumped to screen if debug turned on
                ch = logging.StreamHandler()
                log.addHandler(ch)
        log.debug(f"{self.__name__} loglevel set to {log.level} {log.level}")
        return log

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    UNDERLINE = '\033[4m'
