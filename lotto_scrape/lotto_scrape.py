from bs4 import BeautifulSoup
import sqlite3
from urllib.request import Request, urlopen
import logging
from pathlib import Path 
import sys


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
        self._name='lottery_scrape'
        self.lottery=lottery
        self.pg_num=pg_num
        self.base_url=base_url
        self.log=self._setup_log(logfile,debug)
        self.db=self._setup_db(dbname,'schema.sql') 

    def call_scaper(self,self.pg_num):
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
            scrape_page(i)

    def scrape_page(self,pg_num):
        _name='scrape_page'
        '''
        '''
        try:
            url=f'{self.base_url}={str(self.pg_num)}'
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read())
#            soup = BeautifulSoup(urlopen('http://www.usamega.com/mega-millions-history.asp?p='+page_num).read())
        except Exception as e:
            self.log.error(f'{_name}: Error with ...\n{e}')
            return 

        for row in soup('table',{'bgcolor':'white'})[0].findAll('tr'):
            tds = row('td')
            if tds[1].a is not None:
                #date = tds[1].a.string.encode("utf-8")
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
                        'lddate':datetime.now().strftime("%s")
                    }
                    self.db.add_rowdata(data,self.lottery)
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


class dbmgr(object):

    def __init__(self, db,schema_file,log=None):
        if (log):
            self.log=logging.getLogger(__name__)
        else:
            self.log=logging.getLogger('/dev/null')
        self.schema_file=schema_file
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.schema_cmds=""

    def read_schema_txt(self):
        _name='read_schema_txt'
        here = Path(__file__).resolve().parent
        schema_file= here / self.schema_file
        self.log.debug(f"{_name}: reading from {schema_file}")
        try:
            self.schema_cmds=open(schema_file,'r').read();
            self.log.debug(f'Spew of schema\n{self.schema_cmds}')
        except Exception as e:
            self.log.error(f'{_name}: Problem ... {e}')
            sys.exit(0)

    def table_exists(self,tbl_name):
        _name='table_exists'
        try:
            cmd=f'SELECT count(*) FROM sqlite_master WHERE type="table" AND name="{tbl_name}"'
            self.log.debug(f'{_name}: cmd is {cmd}')
            self.cur.execute(cmd)
            ans=self.cur.fetchone()
            if ans[0]:
                return True
            else:
                return False
        except Exception as e:
            self.log.error(f'{_name}: error ... {e}')

    def tbl_commands(self,tbl_name):
        _name="tbl_commands"
        if len(self.schema_cmds) < 1:
            self.log.warn(f"{_name}: WTH man, schema_empty, maybe run read_schema_txt first?")
            return

        try:
            first=f"CREATE TABLE {tbl_name}"
            self.log.debug(f'{_name}: index is {first}')
            start = self.schema_cmds.index( first )
            end = self.schema_cmds.index( ");", start ) + 2;
            self.log.debug(f'{_name}: index subset:{start}-{end}')
            cmds=self.schema_cmds[start:end]
            return cmds
        except Exception as e:
            self.log.error(f"{_name}: {e}")
            return 

        if not self.table_exists(tbl_name):
            try:
                self.cur.execute(schema_cmds)
            except Exceptiona as e:
                self.log.error(f"{_name} ... {e}")

    def add_rowdata(self,d_dict,table)
        _name='add_rowdata'
        '''
        Add a new row to a sql table

        :type: dict (key,value)
        :param d_dict: the key key must be legitmate field
        :type: str
        :param table: the name of the table to add data
        '''
        try:
            var_string = ', '.join('?' * len(d_dict))
            keys=', '.join(d_dict.keys())
            values=tuple(d_dict.values())
        #    cmd='INSERT INTO %s (%s) VALUES (%s);' \
        #        % (table,keys,var_string)
            cmd=f'INSERT INTO {table} ({keys}) VALUES ({var_string});'
            self.log.debug(f'{_name}: cmd={cmd}')
            self.cur.execute(cmd, (values))
            # when adding lots of rows, the commit slow things down
#            self.conn.commit();
            return 1
        except Exception as e:
            self.log.error("{_name}: WTF ... {e}")
    def commit(self):
        self.conn.commit()
