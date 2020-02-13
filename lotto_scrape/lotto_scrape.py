from bs4 import BeautifulSoup
import sqlite3
from urllib.request import Request, urlopen
from datetime import datetime
import logging
from pathlib import Path 
import sys
from lotto_scrape.mydb import dbmgr


class lotto_scrape(object):
    '''
    '''
    def __init__(self,dbname,lottery,pg_num=1,base_url=None,logfile=None,debug=0):
        '''
        dbname str
            name of the lottor database
        lottery str
            the table name to write to, megamillions, powerball

        '''
        self.__name__='lotto_scrape'
        _name='lottery_scrape'
        self.lottery=lottery
        self.pg_num=pg_num
        self.base_url=base_url
        self.log=self._setup_log(logfile,debug)
        self.db=self._setup_db(dbname,'schema.sql')
        self.previous_date=datetime.strptime(
            self.db.most_recent_bydate(self.lottery,'date','date'),"%Y/%m/%d")
        self.log.debug(f'{_name}: previous data is: {self.previous_date.strftime("%Y/%m/%d")}')

    def call_scraper(self):
        _name='call_scaper'
        if self.pg_num is None:
            self.log.error(f'{_name}: self.pg_num is None')
            sys.exit(0)

        if self.base_url is None:
            self.log.error(f'{_name}: base_url needs to be set')
            sys.exit(0)

        if self.pg_num > 1: # we are going to loop to pg1
            pgs=[i for i in range(int(self.pg_num),0,-1)]
        else:
            pgs=[self.pg_num]

        for i in pgs:
            self.log.debug(f"{_name}: trying to grab page: {i}")
            self.scrape_page(i)

    def scrape_page(self,pg_num):
        _name='scrape_page'
        '''
        '''
        try:
            url=f'{self.base_url}={str(pg_num)}'
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            self.log.debug(f'{_name} sending request:\n{req}')
            soup = BeautifulSoup(urlopen(req).read(),features="lxml")
        except Exception as e:
            self.log.error(f'{_name}: Error with ...\n{e}')
            return 

        for row in soup('table',{'bgcolor':'white'})[0].findAll('tr'):
            tds = row('td')
            if tds[1].a is not None:
                date = tds[1].a.string
                weekday, month_day,YYYY=date.split(',')
                month,dayofmonth=month_day.split()
                x=datetime.strptime(f'{month} {dayofmonth} {YYYY}','%B %d %Y')
                if tds[3].b is not None:
                    uglynumber = tds[3].b.string.split()
                    nums= [int(i) for i in uglynumber if (uglynumber.index(i))%2==0]
                    moneyball = tds[3].strong.string
                    data={'epoch': x.strftime("%s"),
                        'date': x.strftime("%Y/%m/%d"),
                        'weekday': x.strftime("%A"),
                        'num1': nums[0],
                        'num2':nums[1],
                        'num3':nums[2],
                        'num4':nums[3],
                        'num5':nums[4],
                        'moneyball': moneyball,
                        'lddate':datetime.now().strftime("%s")
                    }
                    if x > self.previous_date:
                        self.log.debug(f"{_name}: adding {data} to db")
                        self.db.add_rowdata(data,self.lottery)
                    else:
                        self.log.info(f"{_name}: not adding {data}, already in db?")
        self.db.commit()                    

    def _setup_db(self,dbname,schema_file):
        _name="_setup_db"
        tbls=['megamillions','powerball']
        db=dbmgr(dbname,schema_file,log=self.log)
        db.read_schema_txt()
        for t in tbls:
            if not db.table_exists(t):
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


