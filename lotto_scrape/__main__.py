#!/usr/bin/env python3

import argparse
from pathlib import Path
from datetime import datetime
import sys
from lotto_scrape import lotto_scrape

here = Path(__file__).resolve().parent
exec(open(here / "version.py").read())

def main():
    '''
    Scrape some lotto numbers from MegaMillions and PowerBall 
    '''

    parser = argparse.ArgumentParser(prog=progname,
            formatter_class=CustomFormatter,
            description= '''
            ''',
            epilog=""""
            e.g.
            
            """
            )

    parser.add_argument("-d","--database", type=str,default=None,
        required=True, help="Sqlite database")

    parser.add_argument("-p","--pg_num", type=int,default=1,
        required=False, help="If this is the first time, go to the website, and pick the last page. ")

    parser.add_argument("-l","--logfile", type=str,default=datetime.now().strftime("%Y%j") + ".lottoscrape.log",
        required=False, help="log file name")

    parser.add_argument("-v", "--verbose", action="count",default=0,
        help="increase debug spewage spewage (e.g. -v, -vv, -vvv)")

    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    args=parser.parse_args()
    debug=args.verbose
    pg_num=args.pg_num
    db=args.database
    logfile=args.logfile

    # Run it all
    urlbase='http://www.usamega.com/mega-millions-history.asp?p='
    lottery='megamillions'

    obj=lotto_scrape(db,lottery,pg_num=pg_num,base_url=urlbase,logfile=logfile,debug=debug)


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

