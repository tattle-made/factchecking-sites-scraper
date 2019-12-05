## scraping
A collection of scripts to scrape the following factchecking sites:
- [altnews](https://www.altnews.in/): english + hindi  
- [quint](https://www.thequint.com/news/webqoof)
- [boomlive](https://www.boomlive.in/): english + hindi + bangla
- [vishvasnews](https://www.vishvasnews.com): hindi + english + punjabi + assamese
- [indiatoday](https://www.indiatoday.in/fact-check)
- [factly](https://factly.in/category/fact-check/fake-news/): english + telugu  

and social media sites:
- [reddit](https://reddit.com)
- [sharechat](https://sharechat.com/trending)

### code
[scraping](./scraping.py): helper functions for social media sites  
[sharechat_cron_scraper](./sharechat_cron_scraper.py): refined script to scrape sharechat images  
 
[factchecking_news_sites](./factchecking_news_sites.py): helper functions for factchecking sites  
[live_scraping](live_scraping.py): scraping all sites in one-go  
[live_scraping_cmd](live_scraping_cmd.py): scraping one at a time with command-line arguments  

[storyScraperAPI](storyScraperAPI.py): API to query metadata from mongo  

### how it's done
A lot of sites render most of the HTML server-side which can be scraped with the following snippet:
```python
import requests
from lxml import html

url = 'www.mysite.com'
r = requests.get(url, headers=headers)

tree = html.fromstring(r.content)
desired_div = tree.xpath('//div')
```
These divs can then be organized into jsons and dumped to a database (mongodb).

Few sites (such as quint) render most content dynamically on the client, these require a more involved approach with selenium. Selenium is also used with social media sites to scroll through and load more posts.
Find more details in [blog](http://blog.tattle.co.in/scraping-fact-checked-news/)

### installation
Install all packages: ``` pip install -r requirements.txt ```  

**Geckodriver support**:  
download [geckodriver](https://github.com/mozilla/geckodriver/releases)  
install firefox: ``` sudo apt-get install xvfb firefox ```  

Lastly fill in details in .env_template and rename as .env
