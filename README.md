## lottery_scrape ##

Pull winning numbers for the Megamillions and Powerball and
save in a Sqlite3 database.

### Purpose/Scope ###

Build a local database of winning numbers for snits and giggles.

Currently only pulls data for Mega and Powerball, but other lotteries
could be added.


## Install ##

Clone source package  
`git clone http://github.com/flyrok/lottery_scrape`

Install with pip after download  
`pip install .`

Install in editable mode  
`pip install -e .`

Or install directly from github  
`pip install git+https://github.com/flyrok/lottery_scrape#egg=lottery_scrape`


## Python Dependencies ##

python>=3.6 (script uses f-strings)  
argparse  
pathlib  
sqlite3  
bs4  
urllib  
logging  


## Usage/Examples ##

To see help:  
`lottery_scrape --help`    

To see version:  
`lottery_scrape --version`    

To build initial database of all past numbers, with debugging:  
`lottery_scrape -d lotto.sqlite3 -p 0 -vvv`  

To add most recent numbers to database:  
`lottery_scrape -d lotto.sqlite3 -p 1`

To report all numbers from the database for drawings after 2020-01-01 to the terminal:  
`lottery_scrape -d lotto.sqlite3 -r -s 2020-01-01` 

To report numbers from the database for drawings between 2010-01-01 and 2011-01-01:  
`lottery_scrape -d lotto.sqlite3 -r -s 2010-01-01 -e 2011-01-01`  

Handy aliases  
`alias lotto_get='lotto_scrape -d $HOME/Dropbox/lotto.db -p 1'`  
`alias lotto_show='lotto_scrape -d $HOME/Dropbox/lotto.db -r -s $(date --date="-5 days" "+%Y-%m-%d")'`



