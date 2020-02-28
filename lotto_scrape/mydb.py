import sqlite3
from datetime import datetime
import logging
from pathlib import Path 
import sys

class dbmgr(object):

    def __init__(self, db,schema_file,log=None):
        self.__name__='dbmgr'
        if (log):
            self.log=logging.getLogger(__name__)
        else:
            self.log=logging.getLogger('/dev/null')
        self.schema_file=schema_file
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.schema_cmds=""

    def read_schema_txt(self):
        _name=f"{self.__name__}-read_schema_txt"
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
        _name=f"{self.__name__}-table_exists"
        try:
            cmd=f'SELECT count(*) FROM sqlite_master WHERE type="table" AND name="{tbl_name}"'
            self.log.debug(f'{_name}: cmd is:\n\t{cmd}')
            self.cur.execute(cmd)
            ans=self.cur.fetchone()
            if ans[0]:
                self.log.debug(f"{_name}: {tbl_name} exists ...")
                return True
            else:
                self.log.debug(f"{_name}: {tbl_name} doesn't exists ...")
                return False
        except Exception as e:
            self.log.error(f'{_name}: error ... {e}')

    def tbl_commands(self,tbl_name):
        _name=f"{self.__name__}-tbl_commands"
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

    def dbreport(self,table,date_start,date_end):
        _name=f"{self.__name__}-dbreport"
        '''
        :type: string
            :param table:
        '''
        command=f"SELECT * FROM {table} WHERE date >= date('{date_start}') and date <= date('{date_end}') order by date(date);"

        self.log.debug(f'{_name}: cmd is:\n\t{command}')
        self.cur.execute(command)

        # result is a list (rows) of tuples (row values)
        # e.g. result=>list, result[0]=>tuple
        result=self.cur.fetchall()
        # strip white spaces
#        result=tuple(tuple("".join(i.split()) for i in a) for a in result)
        self.log.debug(f"{_name}: resutl:{type(result)},{len(result)}")
        return result


    def add_rowdata(self,d_dict,table):
        _name=f"{self.__name__}-add_rowdata"
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
        
            cmd=f'INSERT INTO {table} ({keys}) VALUES ({var_string});'
            self.log.debug(f'{_name}: cmd={cmd}')
            self.cur.execute(cmd, (values))
            # don't forget to call commit
            return 1
        except Exception as e:
            self.log.error(f"{_name}: WTF ... {e}")

    def most_recent_bydate(self,tbl_name,col_name,return_field):
        _name=f"{self.__name__}-most_recent_bydate"
        '''
        sort table by a date field and return the
        most recent date value or row
        tbl_name str
            the table that has the date field
        col_name str
            the column name wich has the date obj (yyyy-mm-dd)
        return_field str
            set it to col_name to return only the date value
            or set it to '*' to return the whole row
        '''
        cmd=f"SELECT {return_field} FROM {tbl_name} ORDER BY date({col_name}) DESC Limit 1"
        self.log.debug(f"{_name}: cmd is:\n\t{cmd}")
        self.cur.execute(cmd)
        result=self.cur.fetchone()
        if not result:
            result="1900-01-01"
        if isinstance(result,(list,tuple)) and return_field != "*":
            result=result[0]

        return result

    def commit(self):
        self.conn.commit()

