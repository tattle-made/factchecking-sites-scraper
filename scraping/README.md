## Documentation for Oldest Fact Checking Sites Scraper

This is documentation for the live_scraping.py script used to scrape data for newsmobile, Quint webqoof, 
This code needs to be refactored into the style of (scraper_v3)[https://github.com/tattle-made/tattle-research/tree/master/scraper_v3]. If you have the time to work on it, please reach out using one of [these channels](https://github.com/tattle-made/factchecking-sites-scraper/blob/master/CONTRIBUTE.md). 

# Code Structure

This fact-checking scraper comprises of two essential files:

* [live_scraping](https://github.com/tattle-made/tattle-research/blob/master/live_scraping.py): The config file where you can describe which all sites you want scraped. This is the file that is scraped. 

* [factchecking_news_sites](https://github.com/tattle-made/tattle-research/blob/master/factchecking_news_sites.py): the file which contains helper functions for each of the fact checking sites. The code is structured so that there are separate helper functions for each fact-checking site. This allows for errors for a specific fact checking site to be isolated, without affecting scraping for other sites. 

A third file [live_scraping_cmd](https://github.com/tattle-made/tattle-research/blob/master/live_scraping_cmd.py) allows scraping one file at a time with command-line arguments and can be used for ad-hoc testing. 

### Scraping a fact-checking site
A lot of fact-checking sites render most of the HTML server-side which can be scraped with the following snippet:
```python
import requests
from lxml import html

url = 'www.mysite.com'
r = requests.get(url, headers=headers)

tree = html.fromstring(r.content)
desired_div = tree.xpath('//div')
```
These divs can then be organized into jsons and dumped to a database (mongodb).

Few sites (such as Quint Webqoof) render most content dynamically on the client, these require a more involved approach with selenium. Selenium is also used with social media sites to scroll through and load more posts.
Find more details in [blog](http://blog.tattle.co.in/scraping-fact-checked-news/)

## Licence
When you submit code changes, your submissions are understood to be under the same licence that covers the project - GPL-3. Feel free to contact the maintainers if that's a concern.
