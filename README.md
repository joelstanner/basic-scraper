# basic-scraper

This project will scrape the [King County Restaurant Inspection](http://info.kingcounty.gov/health/ehs/foodsafety/inspections/) website and return a text file with inspection data. You can change the settings for different date ranges and different zipcodes.

Command line options:

```
usage: scraper.py [-h] [-s {hi,avg,most}] [-n NUMBER] [-r]

Return some inspection scores

optional arguments:
  -h, --help            show this help message and exit
  -s {hi,avg,most}, --sort {hi,avg,most}
                        sort the resturants score (default high)
  -n NUMBER, --number NUMBER
                        how many results to produce (default 10)
  -r, --reverse         reverse the order of the results
```

This version is a modified version forked from [Efrain Camacho](https://github.com/efrainc/basic_scraper/tree/step1).  
Some additional code from [Constantine Hatzis](https://github.com/constanthatz/basic-scraper/blob/step2/scraper.py).
