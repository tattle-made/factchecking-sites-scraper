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
- [thelogicalindian.com](https://thelogicalindian.com/): english
- [youturn.in](https://youturn.in/): english
- [newschecker.in](https://newschecker.in/): english + hindi + bengali + gujarati + marathi + punjabi + malayalam + tamil

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

This scraper has gone through multiple iterations and has different implementations for different fact checking sites.
* For Boomlive, digiteye and newsmeter, you should run the script for each of the three sites independently. The script for each site can be found in the [scraper_v3 folder](https://github.com/tattle-made/tattle-research/tree/master/scraper_v3).
This scraper handles scraping the sites, downloading and uploading images to s3, and uploading the text and metadata for each article to mongo.

* For Visvhasnews run scraping/scrape_data.py
This scraper handles scraping the site and uploading text and metadata for each article to mongo. It also uses a pickle file. 

* For Newsmobile, Factly and IndiaToday run scraping/live_scraping.py
  * This step will scrape the sites and upload the content from fact checking sites as per this [data structure](http://blog.tattle.co.in/scraping-fact-checked-news/) to the mongo DB. At this stage the images/videos have not been uploaded to s3. Only the url of these items on the fact checking sites is retrieved. 
  * Run [Upload_to_s3.py](https://github.com/tattle-made/tattle-research/blob/master/scraping/upload_to_s3.py)
This retrieves the URLs for items on the fact checking sites, downloads them to an s3 bucket and updates the MongoDB with an s3 link. 
  * Run [Register_to_portal.py](https://github.com/tattle-made/tattle-research/blob/master/scraping/register_to_portal.py) (optional)
This step registers the media items to Tattle kosh. If you don't have credentials to write to the kosh, skip this step. 
  * Make sure the sites you want the scraper run for during the day are not commented out in live_scraping.py/scraper_data.py


For each of these scrapers:

* Add your s3, Mongo DB credentials to a .env file which should be in the folder that contains the scraper. 




## Request Access
If you want access to the fact-checking sites data please fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSd6KtwsHiS1JaIME0D7n6CDrqZR3swI4D9i8fR2kr1Lp2CTvA/viewform?usp=sf_link). If you have a specific requirement not covered by this form, please ping us on [Slack](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg). 


## Generating the Fact-Checking Sites Dashboard
The data collected from the scrapers is used to generate the weekly fact-checking sites dashboard: https://services.tattle.co.in/khoj/dashboard/

The instructions to generate the dashboard can be found in the [data-experiments repository](https://github.com/tattle-made/data-experiments/blob/master/themes_viz_generator.ipynb). 

## Contribute
Please see instructions [here](CONTRIBUTE.md).

## Get help with developing

Join our [Slack channel](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg) to get someone to respond to immediate doubts and queries.

## Want to get help deploying it into your organisation?

Contact us at admin@tattle.co.in or ping us on [Slack channel](https://join.slack.com/t/tattle-workspace/shared_invite/zt-da07n75v-kIw9Z5b~_gDKP~JsScP1Vg)


## Licence
When you submit code changes, your submissions are understood to be under the same licence that covers the project - GPL-3. Feel free to contact the maintainers if that's a concern.

