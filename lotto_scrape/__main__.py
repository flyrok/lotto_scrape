#!/usr/bin/env python3

import argparse
from pathlib import Path
from datetime import datetime
import sys
from lotto_scrape import lotto_scrape

here = Path(__file__).resolve().parent
exec(open(here / "version.py").read())

lottos={'megamillions':['http://www.usamega.com/mega-millions-history.asp?p=',92],
        'powerball':['https://www.usamega.com/powerball-history.asp?p=',112]}

def main():
    '''
    Scrape some lotto numbers from MegaMillions and PowerBall 
    '''
    parser = argparse.ArgumentParser(prog=progname,
            formatter_class=CustomFormatter,
            description= '''
            ''',
            epilog=f""""
            usage examples:

            # scrape all pages 
            lotto_scrape -d lotto.sqlite3 -p 0 -v

            # scrape most recent page 
            lotto_scrape -d lotto.sqlite3  -v

            # report from database, all dates
            lotto_scrape -d lotto.sqlite3  -r 

            # report from database for 2020-01-01 to 2020-02-01
            lotto_scrape -d lotto.sqlite3  -r -s 2020-01-01 -e 2020-02-01

            lottos set to ....
            {lottos}
            """
            )

    parser.add_argument("-r","--report", action='store_true',default=False,
        required=False, help="Dump db contents instead of pulling new data")

    parser.add_argument("-s","--start", type=str,default='1900-01-01',
        required=False, help="in report mode, this is the start date (e.g. yyyy-mm-dd)")

    parser.add_argument("-e","--end", type=str,default='2599-01-01',
        required=False, help="in report mode, this is the end date.")

    parser.add_argument("-d","--database", type=str,default=None,
        required=True, help="Sqlite database")

    parser.add_argument("-p","--pg_num", type=int,default=1,
        required=False, help="""If this is the first time, 
            set -p to 0 to get all past (see hardwired pg_num in code)
            """)

    parser.add_argument("-l","--logfile", type=str,default=datetime.now().strftime("%Y%j") + ".lottoscrape.log",
        required=False, help="log file name")

    parser.add_argument("-v", "--verbose", action="count",default=0,
        help="increase debug spewage spewage (e.g. -v, -vv, -vvv)")

    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    args=parser.parse_args()
    debug=args.verbose
    pg=args.pg_num
    db=args.database
    start=args.start
    end=args.end
    report=args.report
    logfile=args.logfile

    # Intitialize lotto_scrape class


    if report: # just report, don't grab new data
        #need to initialize obj, only import parameter is db
        obj=lotto_scrape(db,'megamillions',pg_num=pg,base_url='junk.com',logfile=logfile,debug=debug)
        for i in lottos.keys():
            #obj.report(tbl_name,date_start,date_end)
            obj.report(i,start,end)

    else: # grab new data for mega and powerball
        for i in lottos.keys():
            lottery=i
            urlbase=lottos[i][0]
            if pg == 0:
                pg_num=lottos[i][1]
            else:
                pg_num=1
            print(f'doing {lottery} {urlbase}{pg_num}')
            obj=lotto_scrape(db,i,pg_num=pg_num,base_url=lottos[i][0],logfile=logfile,debug=debug)
            obj.call_scraper()

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    '''
    re-class ArgDefaults formatter to also print things pretty. Helps printing out the config file example
    '''
    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if type(action.default) == type(sys.stdin):
                        print( action.default.name)
                        help += ' (default: ' + str(action.default.name) + ')'
                    else:
                        help += ' (default: %(default)s)'
        return help

if __name__ == '__main__':
    main()

