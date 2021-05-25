## Why Does This Exist?

One of Tattle's goals is to make stories fact-checking content circulated on chat apps and social media more accessible to mobile first users. To make the content accessible, Tattle wants the content to be discoverable through image search and video search. To implement search, Tattle needs the multi-media content inside the stories from fact-checking sites, linked with the sites that it is coming from.  

## Introduction
This repository contains collection of scripts to scrape the factchecking sections of the following sites:

- [altnews](https://www.altnews.in/): english + hindi  (IFCN expired)
- [quint](https://www.thequint.com/news/webqoof)
- [boomlive](https://www.boomlive.in/): english + hindi + bangla
- [vishvasnews](https://www.vishvasnews.com): hindi + english + punjabi + assamese
- [indiatoday](https://www.indiatoday.in/fact-check)
- [factly](https://factly.in/category/fact-check/fake-news/): english + telugu  
- [factchecker.in](https://www.factchecker.in/): english  (IFCN expired)
- [newsmobile.in](https://newsmobile.in/articles/category/nm-fact-checker):english
- [newsmeter.in](https://newsmeter.in/fact-check/)
- [digiteye.in](https://digiteye.in/)

At present Tattle only scrapes [IFCN](https://ifcncodeofprinciples.poynter.org/signatories) certified fact-checking sites. See [factchecting_sites_status.md] (https://github.com/tattle-made/tattle-research/blob/master/factchecking_sites_status.md) for the updated status on each of the websites. 

## Running Locally:

### Prerequisites:

* Python Libraries: Install all packages: `pip install -r requirements.txt`

* **Geckodriver support**:\
download [geckodriver](https://github.com/mozilla/geckodriver/releases)\
install firefox: `sudo apt-get install xvfb firefox`

* Data Storage: 
  * A MongoDB database where all the content scraped can be pushed.
  * An AWS S3 bucket on which images, videos and other multimedia items can be pushed. 

The code can be amended so that content is written to a local folder (instead of an S3 bucket). For conciseness, those steps have been excluded from this documentation. If you need help doing that, please reach out to us (See section on 'Get Help with Developing')

### Steps to Run:

* Add your s3, Mongo DB credentials to a .env file which should be in the [scraping folder](https://github.com/tattle-made/tattle-research/tree/master/scraping).
* Make sure the sites you want the scraper run for during the day are not commented out in live_scraping.py
* Run [live_scraping.py] (https://github.com/tattle-made/tattle-research/blob/master/scraping/live_scraping.py)
This step will scrape the sites and upload the content from fact checking sites as per this [data structure](http://blog.tattle.co.in/scraping-fact-checked-news/) to the mongo DB. At this stage the images/videos have not been uploaded to s3. Only the url of these items on the fact checking sites is retrieved. 

* Run [Upload_to_s3.py](https://github.com/tattle-made/tattle-research/blob/master/scraping/upload_to_s3.py)
This retrieves the URLs for items on the fact checking sites, downloads them to an s3 bucket and updates the MongoDB with an s3 link. 

* Run [Register_to_portal.py](https://github.com/tattle-made/tattle-research/blob/master/scraping/register_to_portal.py) (optional)
This step registers the media items to Tattle kosh. If you don't have credentials to write to the kosh, skip this step. 

# Code Structure

The fact-checking scraper comprises of two essential files:

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

## Request Access
If you want access to the fact-checking sites data please fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSd6KtwsHiS1JaIME0D7n6CDrqZR3swI4D9i8fR2kr1Lp2CTvA/viewform?usp=sf_link). If you have a specific requirement not covered by this form, please ping us on [Slack](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg). 

## Contribute
Please see instructions [here](CONTRIBUTE.md).

## Get help with developing

Join our [Slack channel](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg) to get someone to respond to immediate doubts and queries.

## Want to get help deploying it into your organisation?

Contact us at admin@tattle.co.in or ping us on [Slack channel](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg)


## Licence
When you submit code changes, your submissions are understood to be under the same licence that covers the project - GPL-3. Feel free to contact the maintainers if that's a concern.

