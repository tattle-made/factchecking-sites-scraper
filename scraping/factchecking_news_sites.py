from lxml.html import fromstring
from numpy.random import randint
from tqdm import tqdm
from numpy import arange
from os import environ
import uuid
from time import sleep
from pymongo import MongoClient
from datetime import date
from dateutil.parser import parse
import requests
from dotenv import load_dotenv
from selenium import webdriver
load_dotenv()

# necessary params?
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 
          'November', 'December']

gecko_driver_path = environ['GECKO_DRIVER_PATH']

def get_db():
    # setup db
    # replace with your own db
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.publicData.stories
    
    return db

# note: priorSchema uses postID as index, and DocSchema uses doc_id
def getDocSchema(doc_id=None, postID=None, domain=None, origURL=None, s3URL=None, possibleLangs=None, isGoodPrior=[0,0], 
                 mediaType=None, content=None, nowDate=None):
    # schema for an individual doc inside a news article
    if doc_id == None:
        doc_id = uuid.uuid4().hex
    doc = {
        'doc_id': doc_id,  # unique id
        'postID': postID,  # same as postID above
        'domain': domain,  # news site such as: altnews.in | factly.in, same as domain above
        'origURL': origURL,  # orig scraped url, same as postURL
        's3URL': s3URL,  # url in s3
        'possibleLangs': possibleLangs,  # possible languages in media, user input from source of data
        'isGoodPrior': isGoodPrior,  # no of [-ve votes, +ve votes]
        'mediaType': mediaType,  # ['text', 'image', 'video', 'audio']
        'content': content,  # text, if media_type = text or text in image/audio/video
        'nowDate': nowDate  # date of scraping, same as date_accessed
    }

    return doc

def getStorySchema(postID=None, postURL=None, domain=None, headline=None, date_accessed=None, date_updated=None, 
                   author=None, docs=[]):
    # schema for a news story/article
    if postID == None:
        postID = uuid.uuid4().hex
        
    post = {  # a post is a unique article
        'postID': postID,  # unique post ID
        'postURL': postURL,  # link that was scraped
        'domain': domain,  # domain such as altnews/factly
        'headline': headline,  # headline text
        'date_accessed': date_accessed,  # date scraped
        'date_updated': date_updated,  # later of date published/updated
        'author': author,
        'docs': docs
    }

    return post

def get_tree(url):
    # get the tree of each page
    # TODO: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 
              'Content-Type': 'text/html'}
    try:
        html = requests.get(url, headers=headers)
    except Exception as e:
        print(f'failed request: {e}')
    if 'boomlive' in url:
        html.encoding = 'utf-8'
    #tree = fromstring(html.content)
    tree = fromstring(html.text)
    return tree

# site-agnostic scraping functions
def scraping_site_links(getPost=None, links=None, db=None, langs=[], domain=None, csvErr=None, 
                        body_div=None, img_link=None, header_div=None):
    for l in tqdm(links, desc="links: "):
        try:
            if db.count_documents({'postURL': l}):
                if csvErr:
                    with open(csvErr, 'a') as f:
                        f.write(f'\n{l},failed,link in db')
                else:
                    print(f'skipping post: {l}, already in db')
            else:
                if domain == 'thequint.com':
                    driver = setup_driver()
                    post = getPost(l, driver=driver, langs=langs, domain=domain, body_div=body_div, 
                                   img_link=img_link, header_div=header_div)
                    driver.close()
                else:
                    post = getPost(l, langs=langs, domain=domain, body_div=body_div, img_link=img_link, header_div=header_div)
                db.insert_one(post)        
                sleep(randint(1, 5))
        except Exception as e:
                if csvErr:
                    with open(csvErr, 'a') as f:
                        f.write(f'\n{l},failed,{e}')
                else:
                    print(f'failed @{l}: {e}')

def get_live_links(getLinks=None, url=None, db=None, domain=None):
    newLink = True
    page_num = 1
    all_links = []

    while newLink:    
        links, _ = getLinks(url=url, NUM_PAGES=[page_num], domain=domain)
        if len(links) == 0:
            newLink = False
            print('No/No more links found')                
            continue
        for l in links:
            if db.count_documents({'postURL': l}):
                newLink = False
            else:
                all_links.append(l)
                
        #all_links += links
        page_num += 1
        
    return all_links, page_num

# altnews specific helper functions
def get_post_links_from_page_altnews(url='https://www.altnews.in'):
    tree= get_tree(url)
    all_links = tree.xpath('//h2/a[@href]')
    # print(len(all_links))
    links = []
    for i, x in enumerate(all_links):
        #print(f'{i}: {x.get("href")}')
        links.append(x.get('href'))
    
    return links

def get_metadata_altnews(tree):
    headline = tree.xpath('//header/h1')[0].text
    datestr = tree.xpath('//article//header//div[contains(@class, herald-date)]//span[@class="updated"]')[0].text
    author = tree.xpath('//article//header//div[contains(@class, "herald-author")]//a')
    author_name = author[0].text
    author_link = author[0].get('href')
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    
    return metadata

def get_content_altnews(tree, body_elements):
    # return body content in a dict from page tree
    content = {'text': [], 'video': [], 'image': [], 'tweet': []}

    video = tree.xpath('//iframe')
    if video: 
        for v in video:
            content['video'].append(v.get('src'))

    for i, x in enumerate(body_elements):        
        text_content = x.text_content()
        if text_content:
            content['text'].append(text_content)    

        image = x.xpath('img')
        if image:
            for im in image:
                content['image'].append(im.get('src'))
        
    return content

def get_post_altnews(page_url, langs=[], domain=None, body_div=None, img_link=None, header_div=None):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(page_url)
    metadata = get_metadata_altnews(tree)
    body_elements = tree.xpath('//div[contains(@class, herald-entry-content)]/*[self::p or self::h2 or self::iframe or self::twitter-widget]')
    content = get_content_altnews(tree, body_elements)

    # fields
    postID = uuid.uuid4().hex
    domain = domain
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = parse(metadata['date_updated']).strftime("%B %d, %Y")
    author = {'name': metadata['author'], 'link': metadata['author_link']}

    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def get_historical_links_altnews(url='https://www.altnews.in', NUM_PAGES=[1], ifSleep=True, domain=None):
    # get story links based on url and page range
    #LAST_PAGE = 20
    #NUM_PAGES = arange(20, 175)
    #NUM_PAGES = [175]
    links = []
    for page in tqdm(NUM_PAGES, desc="pages: "):
        page_url = f'{url}/page/{page}'
        curLinks = get_post_links_from_page_altnews(page_url)
        links += curLinks
        if ifSleep:
            sleep(randint(10, 20))

    return links, NUM_PAGES

def scraping_altnews_historical(url='https://www.altnews.in', db=None, langs=[], domain='altnews.in', NUM_PAGES=[1]):
    links, NUM_PAGES = get_historical_links(url=url, NUM_PAGES=NUM_PAGES)
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            post = get_post_altnews(l, langs=langs, domain=domain)
            db.insert_one(post)        
            sleep(randint(10, 20))
            
    print(f'Historical scraping complete, pages: {NUM_PAGES[0]}:{NUM_PAGES[-1]}')
                    
# boomlive specific helper functions
# get metadata
def get_metadata_boomlive(tree):
    headline = tree.xpath('//h1')[0].text
    datestr = tree.xpath('//span[contains(@class,"date")]//span')[0].text
    datestr = parse(datestr).strftime("%B %d, %Y")
    author_name = tree.xpath('//a[contains(@class,"author-name")]')[0].text
    author_link = None
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    return metadata

# get_content
def get_content_boomlive(tree, body_elements, body_div='div[@class="pf-content"]', img_link='data-src'):
    # return body content in a dict from page tree
    # english: body_div = 'div[@class="pf-content"]'
    # bengali: body_div = 'section[@id="mvp-content-main"]'
    # hindi: body_div = 'div[@class="pf-content"]'
    
    content = {'text': [], 'video': [], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}

    # video embed
    video_embed = tree.xpath(f'//{body_div}//video/source')
    for v in video_embed:
        content['video'].append(v.get('src'))
    # video youtube
    video_yt = tree.xpath(f'//{body_div}//iframe[not(contains(@class, "lazy"))]')
    for v in video_yt:
        content['video'].append(v.get('src'))
    # video fb
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed-facebook")]//div[@class="fb-video"]')
    for f in fb:
        content['facebook'].append(f.get('data-href'))
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed")]//a')    
    # first one is link, second is superfluous
    try:
        content['facebook'].append(video_fb[0].get('href'))
    except:
        pass

    # images
    images = tree.xpath(f'//{body_div}//figure/img')
    images += tree.xpath(f'//{body_div}//div[contains(@class,"image-and-caption-wrapper")]//img')
    images += tree.xpath(f'//div[@class="single-featured-thumb-container"]/img')
    for i in images:
        content['image'].append(i.get(img_link))

    # tweet
    tweets = tree.xpath('//blockquote[@class="twitter-tweet"]//a')
    for t in tweets:
        if t.text and any(m in t.text for m in months):
            content['tweet'].append(t.get('href'))
    
    # instagram
    insta = tree.xpath('//figure[contains(@class, "wp-block-embed-instagram")]//blockquote')
    for i in insta:
        content['instagram'].append(i.get('data-instgrm-permalink'))
        
    for i, x in enumerate(body_elements):        
        text_content = x.text_content()
        if text_content:
            content['text'].append(text_content)    
        
    return content

def get_post_boomlive(page_url, langs=[], domain=None, body_div='div[@class="pf-content"]', img_link='data-src', header_div=None):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(page_url)
    metadata = get_metadata_boomlive(tree)
    body_elements = tree.xpath(f'//{body_div}/*[self::p or self::div[@class="pasted-from-word-wrapper"]/p]')
    content = get_content_boomlive(tree, body_elements, body_div=body_div, img_link=img_link)
    
    # fields
    postID = uuid.uuid4().hex
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = metadata['date_updated']
    author = {'name': metadata['author'], 'link': metadata['author_link']}
    
    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def get_post_links_from_page_boomlive(url=None, domain=None):
    tree= get_tree(url)
    all_links = tree.xpath('//h2/a')
    links = []
    if domain == 'boomlive.in':
        prefix = f'https://www.{domain}'
    else:
        prefix = f'https://{domain}'
    for i, x in enumerate(all_links):
        curLink = x.get('href')
        if 'boomlive' not in curLink:
            links.append(f'{prefix}{curLink}')
        else:
            links.append(x.get('href'))
    
    return links

def get_historical_links_boomlive(url=None, NUM_PAGES=[1], domain=None):
    # get story links based on url and page range
    links = []
    for page in NUM_PAGES:
        page_url = f'{url}/page/{page}'
        curLinks = get_post_links_from_page_boomlive(url=page_url, domain=domain)
        links += curLinks
        print(f'{page}: {len(links)}')
        sleep(randint(1, 5))

    return links, NUM_PAGES

def scraping_boomlive_historical(url=None, db=None, langs=[], domain=None, NUM_PAGES=[1], body_div='div[@class="pf-content"]', img_link='data-src'):
    links, NUM_PAGES = get_historical_links_boomlive(url=url, NUM_PAGES=NUM_PAGES)
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            post = get_post_boomlive(l, langs=langs, domain=domain, body_div=body_div, img_link=img_link)
            db.insert_one(post)        
            sleep(randint(5, 15))
            
    print(f'Historical scraping complete, pages: {NUM_PAGES[0]}:{NUM_PAGES[-1]}')

# factly specific helper functions
def get_metadata_factly(tree):
    headline = tree.xpath('//header//h1')[0].text
    datestr = tree.xpath('//header//time')[0].text
    author = tree.xpath('//header//a[@rel="author"]')
    author_name = author[0].text
    author_link = author[0].get('href')
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    
    return metadata

def get_content_factly(tree, body_elements, body_div=None):
    content = {'text': [], 'video': [], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}

    video = tree.xpath(f'//{body_div}//figure//iframe')
    if video: 
        for v in video:
            content['video'].append(v.get('src'))

    image = tree.xpath(f'//{body_div}//div/figure/img')
    if image:
        for im in image:
            content['image'].append(im.get('src'))

    # tweet
    tweets = tree.xpath(f'//{body_div}//blockquote[contains(@class,"twitter-tweet")]//a')
    for t in tweets:
        if t.text and any(m in t.text for m in months):
            content['tweet'].append(t.get('href'))
    
    for i, x in enumerate(body_elements):        
        text_content = x.text_content()
        if text_content:
            content['text'].append(text_content)    
                        
    return content

def get_post_factly(page_url, langs=[], domain=None, body_div=None, img_link=None, header_div=None):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(page_url)
    metadata = get_metadata_factly(tree)
    body_elements = tree.xpath(f'//{body_div}//p')
    content = get_content_factly(tree, body_elements, body_div=body_div)
    
    # fields
    postID = uuid.uuid4().hex
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = metadata['date_updated']
    author = {'name': metadata['author'], 'link': metadata['author_link']}
    
    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def get_historical_links_factly(url=None, NUM_PAGES=[1], domain=None):
    # get story links based on url and page range
    links = []
    for page in tqdm(NUM_PAGES, desc="pages: "):
        page_url = f'{url}/page/{page}'
        sleep(1)
        tree = get_tree(page_url)
        all_links = tree.xpath('//div[contains(@class,"main-content")]//h2[@class="post-title"]/a[@href]')
        for l in all_links:
            links.append(l.get('href'))

    return links, NUM_PAGES

def dump_links_factly():
    # loop through all links
    links = []

    for page_num in tqdm(range(1, 85), desc="links: "):
    #     page_num = 2 # 1-85
        page_url = f'https://factly.in/category/fake-news/page/{page_num}/'
        sleep(1)
        tree = get_tree(page_url)
        
        all_links = tree.xpath('//div[contains(@class,"main-content")]//h2[@class="post-title"]/a[@href]')

        for l in all_links:
    #         print(l.get('href'))
            links.append(l.get('href'))

    with open('factly_links', 'w') as f:
        for l in links:
            f.write(f'{l}\n')

def scraping_factly_historical(links=None, db=None, langs=[], domain=None, body_div=None):
    print(db.count_documents({}))
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            post = get_post_factly(l, langs=langs, domain=domain, body_div=body_div)
            db.insert_one(post)        
            sleep(randint(5, 15))
            
    print(f'Historical scraping complete: {domain}')
    print(db.count_documents({}))

def run_factly():
    db = get_db()
    dump_links_factly()

    links =[]
    with open('factly_links', 'r') as f:
        for l in f.readlines():
            links.append(l.strip('\n'))
    links = list(set(links))

    langs=['english', 'telugu']
    domain='factly.in'
    body_div='div[@itemprop="articleBody"]'

    scraping_factly_historical(links=links, db=db, langs=langs, domain=domain, body_div=body_div)

# quint specific helper functions
# selenium setup
def setup_driver():
    # selenium scrape
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    # firefox profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.manager.showWhenStarting', False)

    # using firefox gecko driver
    driver = webdriver.Firefox(executable_path=gecko_driver_path, firefox_profile=profile, options=options)
    
    return driver

def get_driver(url, driver, wait_time=1):
    driver.get(url)
    driver.implicitly_wait(wait_time) #gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != 'complete':
        pass
    
    return driver

def get_metadata_quint(tree):
    false = None
    jsonData = eval(tree.xpath('//script[@type="application/ld+json"]')[0].text_content())[0]
    
    headline = jsonData['headline']
    datestr = parse(jsonData['dateModified']).strftime("%B %d, %Y")
    author = jsonData['author']
    author_name = author['name']
    author_link = author['sameAs']
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    
    return metadata

def get_content_quint(driver):    
    content = {'text': [], 'video': [], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}

    # facebook
    facebook = driver.find_elements_by_xpath('//div[@class="story-card"]//div[contains(@class,"fb-post")]//iframe[@src]')
    for f in facebook:
        content['facebook'].append(f.get_attribute('src'))

    # videos
    videos = driver.find_elements_by_xpath('//div[@class="story-card"]//iframe[@src]')
    for v in videos:
        content['video'].append(v.get_attribute('src'))
        
    # images
    images = driver.find_elements_by_xpath('//div[@class="story-card"]//div/figure/img')
    for i in images[1:]:
        content['image'].append(i.get_attribute('src'))
        
    body_elements = driver.find_elements_by_xpath('//div[@class="story-card"]//p')
    for i, x in enumerate(body_elements):        
        text = x.text
        if text:
            content['text'].append(text)    
        
    return content

def get_post_quint(page_url, driver=None, langs=[], domain=None, body_div=None, img_link=None, header_div=None):
    # from a page url, get a post dict ready for upload to mongo

    tree = get_tree(page_url)
    metadata = get_metadata_quint(tree)
    driver = get_driver(page_url, driver, wait_time=3)
    content = get_content_quint(driver)
        
    # fields
    postID = uuid.uuid4().hex
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = metadata['date_updated']
    author = {'name': metadata['author'], 'link': metadata['author_link']}
    
    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def dump_links_quint():
    # loop through all links
    links = []

    for page_num in tqdm(range(1, 140), desc="links: "):
        page_url = f'https://www.thequint.com/news/webqoof/{page_num}'
        sleep(1)
        tree = get_tree(page_url)
        
        all_links = tree.xpath('//div[contains(@class,"ctg-news")]/a[@href]')
        all_links = list(set(all_links))
        
        for l in all_links:
            #print(f"https://www.thequint.com{l.get('href')}")
            links.append(f"https://www.thequint.com{l.get('href')}")

    with open('quint_links', 'w') as f:
        for l in links:
            f.write(f'{l}\n')

def get_historical_links_quint(url=None, NUM_PAGES=[1], domain=None):
    # get story links based on url and page range
    links = []
    for page in tqdm(NUM_PAGES, desc="pages: "):
        page_url = f'{url}/{page}'
        sleep(1)
        tree = get_tree(page_url)
        
        all_links = tree.xpath('//div[contains(@class,"ctg-news")]/a[@href]')
        all_links = list(set(all_links))
        
        for l in all_links:
            links.append(f"https://www.thequint.com{l.get('href')}")

    return links, NUM_PAGES

def scraping_quint_historical(links=None, db=None, langs=[], domain=None):
    print(db.count_documents({}))
    
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            try:
                driver = setup_driver()
                post = get_post_quint(l, driver=driver, langs=langs, domain=domain)
                driver.close()
                
                db.insert_one(post)        
                sleep(randint(5, 15))
            except Exception as e:
                print(f'failed @{l}: {e}')
            
    print(f'Historical scraping complete: {domain}')
    print(db.count_documents({}))

def run_quint():
    db = get_db()
    dump_links_quint()

    links =[]
    with open('quint_links', 'r') as f:
        for l in f.readlines():
            links.append(l.strip('\n'))
    links = list(set(links))

    langs=['english']
    domain='thequint.com'

    scraping_quint_historical(links=links, db=db, langs=langs, domain=domain)

# vishvasnews specific helpers
def get_metadata_vishvasnews(tree):
    headline = tree.xpath('//h1')[0].text.strip('\r\n ')
    datestr = tree.xpath('//ul[@class="updated"]//li')[1].text.split('Updated: ')[-1]
    author = tree.xpath('//ul[@class="updated"]/li/span/a')
    author_name = author[0].text
    author_link = author[0].get('href')
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    
    return metadata

def get_content_vishvasnews(tree, body_elements, body_div=None):
    # return body content in a dict from page tree
    # english: body_div = 'div[@class="pf-content"]'
    # bengali: body_div = 'section[@id="mvp-content-main"]'
    # hindi: body_div = 'div[@class="pf-content"]'
    
    content = {'text': [], 'video': [], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 
          'November', 'December']

    # video embed
    video_embed = tree.xpath(f'//{body_div}//video/source')
    for v in video_embed:
        content['video'].append(v.get('src'))
    # video youtube
    video_yt = tree.xpath(f'//{body_div}//iframe')
    for v in video_yt:
        content['video'].append(v.get('src'))
    # video fb
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed-facebook")]//div[@class="fb-video"]')
    for f in fb:
        content['facebook'].append(f.get('data-href'))
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed")]//a')    
    # first one is link, second is superfluous
    try:
        content['facebook'].append(video_fb[0].get('href'))
    except:
        pass

    # images
    images = tree.xpath(f'//{body_div}/div/img')
    for i in images:
        if i.get('src'):
            content['image'].append(i.get('src'))
    images = tree.xpath(f'//{body_div}//figure/img')
    for i in images:
        if i.get('data-src'):
            content['image'].append(i.get('data-src'))

    # tweet
    tweets = tree.xpath('//blockquote[@class="twitter-tweet"]//a')
    for t in tweets:
        if t.text and any(m in t.text for m in months):
            content['tweet'].append(t.get('href'))
    
    # instagram
    insta = tree.xpath('//figure[contains(@class, "wp-block-embed-instagram")]//blockquote')
    for i in insta:
        content['instagram'].append(i.get('data-instgrm-permalink'))
        
    for i, x in enumerate(body_elements):        
        text_content = x.text_content()
        if text_content:
            content['text'].append(text_content)    
        
    return content

def get_post_vishvasnews(page_url, langs=[], domain=None, body_div=None, img_link=None, header_div=None):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(page_url)
    metadata = get_metadata_vishvasnews(tree)
    body_elements = tree.xpath(f'//{body_div}/*[self::p or self::h2]')
    content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
    
    # fields
    postID = uuid.uuid4().hex
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = metadata['date_updated']
    author = {'name': metadata['author'], 'link': metadata['author_link']}
    
    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def scraping_vishvasnews_historical(links=None, db=None, langs=[], domain=None, body_div=None):
    print(db.count_documents({}))
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            try:
                post = get_post_vishvasnews(l, langs=langs, domain=domain, body_div=body_div)
                db.insert_one(post)        
                sleep(randint(5, 15))
            except Exception as e:
                print(f'failed @ {l}: {e}')
            
    print(f'Historical scraping complete: {domain}')
    print(db.count_documents({}))

def dump_links_vishvasnews(lang):
    # NOTE: need to run this with a GUI session
    # lang = ['assamese', 'english', 'hindi', 'urdu', 'punjabi']
    if lang == 'hindi':
        url = 'https://www.vishvasnews.com/'
    else:
        url = f'https://www.vishvasnews.com/{lang}'
    tree = get_tree(url)

    # selenium scrape
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
                         
    # profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.manager.showWhenStarting', False)

    # using firefox gecko driver
    driver = webdriver.Firefox(executable_path=gecko_driver_path, firefox_profile=profile, options=options)
    driver.maximize_window() #For maximizing window

    driver.get(url)
    driver.implicitly_wait(3) #gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != 'complete':
        pass

    i = 0
    more_posts_link = True
    more_posts_link = driver.find_elements_by_xpath('//div[@class="nav-links"]/a')[0]

    while True:
        driver.execute_script('arguments[0].scrollIntoView();', more_posts_link)
        
        articles = driver.find_elements_by_xpath('//div/h3/a')
        print(len(set(articles)))

        more_posts_link.click()
        print(i, ' clicked!')
        i += 1
        
        sleep(0.5)
        
        try:
            more_posts_link = driver.find_elements_by_xpath('//div[@class="nav-links"]/a')[0]
        except Exception as e:
            print(f'failed: no more posts: {e}')
            break

    links = []
    for a in set(articles):
        links.append(a.get_attribute('href'))
        links = list(set(links))
    print(len(links))

    with open(f'vishvasnews_links_{lang}', 'w') as f:
        for l in links:
            f.write(f'{l}\n')

def get_historical_links_vishvasnews(url=None, NUM_PAGES=[1], domain=None):
    # NOTE: need to run this with a GUI session
    # lang = ['assamese', 'english', 'hindi', 'urdu', 'punjabi']
    tree = get_tree(url)

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    # firefox profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.manager.showWhenStarting', False)

    # using firefox gecko driver
    driver = webdriver.Firefox(executable_path=gecko_driver_path, firefox_profile=profile, options=options)
    driver.maximize_window() #For maximizing window

    driver.get(url)
    driver.implicitly_wait(3) #gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != 'complete':
        pass

    i = 0
    more_posts_link = True
    more_posts_link = driver.find_elements_by_xpath('//div[@class="nav-links"]/a')[0]

    while True and i < 10:
        driver.execute_script('arguments[0].scrollIntoView();', more_posts_link)

        articles = driver.find_elements_by_xpath('//div/h3/a')
        print(len(set(articles)))

        try:
            more_posts_link.click()
            print(i, ' clicked!')
            i += 1
        except Exception as e:
            break

        sleep(0.5)

        try:
            more_posts_link = driver.find_elements_by_xpath('//div[@class="nav-links"]/a')[0]
        except Exception as e:
            print(f'failed: no more posts: {e}')
            break

    links = []
    for a in set(articles):
        links.append(a.get_attribute('href'))
        links = list(set(links))
    
    driver.close()
                         
    return links, NUM_PAGES
                         
def run_vishvasnews():
    langs = ['assamese', 'english', 'hindi', 'urdu', 'punjabi']
    db = get_db()
    for lang in langs:
        dump_links_vishvasnews(lang=lang)

        links = []
        filename = f'vishvasnews_links_{lang}'
        with open(filename, 'r') as f:
            for l in f:
                links.append(l.strip('\n'))
        
        if lang == 'hindi':
            domain = 'vishvasnews.com'
        else:
            domain = f'vishvasnews.com/{lang}'
        body_div = 'div[@class="lhs-area"]'
        scraping_vishvasnews_historical(links=links, db=None, langs=[], domain=None, body_div=body_div)

# indiatoday specific helpers
def get_metadata_indiatoday(tree, body_div=None):
    headline = tree.xpath(f'//{body_div}//h1')[0].text
    datestr = tree.xpath(f'//{body_div}//dt[@class="pubdata"]')[0].text
    author = tree.xpath(f'//{body_div}//dt[@itemprop="name"]')[0]
    if author.xpath('a'):    
        author = author.xpath('a')[0]
    author_name = author.text
    if author.get('href'):
        author_link = f"https://www.indiatoday.in{author.get('href')}"
    else:
        author_link = None
        
    metadata = {'headline': headline, 'author': author_name, 'author_link': author_link, 'date_updated': datestr}
    
    return metadata

def get_content_indiatoday(tree, body_elements, body_div=None):
    # return body content in a dict from page tree
    # english: body_div = 'div[@class="pf-content"]'
    # bengali: body_div = 'section[@id="mvp-content-main"]'
    # hindi: body_div = 'div[@class="pf-content"]'
    
    content = {'text': [], 'video': [], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}

    # video embed
    #     video_embed = tree.xpath(f'//{body_div}//input')
    #     for v in video_embed:
    #         content['video'].append(v.get('value'))
    # video youtube
    video_yt = tree.xpath(f'//{body_div}//iframe')
    for v in video_yt:
        content['video'].append(v.get('src'))
    # video fb
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed-facebook")]//div[@class="fb-video"]')
    for f in fb:
        content['facebook'].append(f.get('data-href'))
    video_fb = tree.xpath('//figure[contains(@class, "wp-block-embed")]//a')    
    # first one is link, second is superfluous
    try:
        content['facebook'].append(video_fb[0].get('href'))
    except:
        pass

    # images
    main_image = tree.xpath(f'//div[@class="stryimg"]//img')[0]
    main_image_link = main_image.get('data-src')
    if not main_image_link:
        main_image_link = main_image.get('src')
    content['image'].append(main_image_link)

    images = tree.xpath(f'//{body_div}//img')
    for i in images:
        if i.get('data-src'):
            content['image'].append(i.get('data-src'))

    # tweet
    tweets = tree.xpath('//blockquote[@class="twitter-tweet"]//a')
    for t in tweets:
        if t.text and any(m in t.text for m in months):
            content['tweet'].append(t.get('href'))
    
    # instagram
    insta = tree.xpath(f'//{body_div}//blockquote[@class="instagram-media"]')
    for i in insta:
        content['instagram'].append(i.get('data-instgrm-permalink'))
        
    for i, x in enumerate(body_elements):        
        text_content = x.text_content()
        if text_content:
            content['text'].append(text_content)    
        
    return content

def dump_links_indiatoday():
    # loop through all links
    links = []

    for page_num in tqdm(range(0, 50), desc="links: "):
        page_url = f'https://www.indiatoday.in/fact-check?page={page_num}&view_type=list'
        sleep(1)
        tree = get_tree(page_url)
        
        all_links = tree.xpath('//h2/a[@href]')

        for l in all_links:
            #print(f"https://www.indiatoday.in{l.get('href')}")
            links.append(f"https://www.indiatoday.in{l.get('href')}")

    links = list(set(links))
    with open('india_today_links', 'w') as f:
        for l in links:
            f.write(f'{l}\n')

def get_historical_links_indiatoday(url=None, NUM_PAGES=[1], domain=None):
    # get story links based on url and page range
    links = []
    for page in tqdm(NUM_PAGES, desc="pages: "):
        page_url = f'{url}?page={page}&view_type=list'
        sleep(1)
        tree = get_tree(page_url)
        
        all_links = tree.xpath('//h2/a[@href]')

        for l in all_links:
            links.append(f"https://www.indiatoday.in{l.get('href')}")
        links = list(set(links))
                         
    return links, NUM_PAGES
                         
def get_post_indiatoday(page_url, langs=[], domain=None, body_div=None, header_div=None, img_link=None):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(page_url)

    if not tree.xpath(f'//{body_div}'):
        headline = tree.xpath('//h1')[0].text
        datestr = tree.xpath('//p[@class="upload-date"]/span')[0].text
        metadata = {'headline': headline, 'author': None, 'author_link': None, 'date_updated': datestr}

        text = tree.xpath('//div[@class="video-slider-description"]//p')[1].text
        video = tree.xpath('//iframe[@src]')[0].get('src')
        content = {'text': [text], 'video': [video], 'image': [], 'tweet': [], 'facebook': [], 'instagram': []}
    else:
        metadata = get_metadata_indiatoday(tree, body_div=header_div)
        body_elements = tree.xpath(f'//{body_div}/p')
        content = get_content_indiatoday(tree, body_elements, body_div=body_div)
    
    # fields
    postID = uuid.uuid4().hex
    # uniform date format
    nowDate = date.today().strftime("%B %d, %Y")
    date_updated = metadata['date_updated']
    author = {'name': metadata['author'], 'link': metadata['author_link']}
    
    docs = []
    for k,v in content.items():
        if not v:  # empty list
            continue
        if k == 'text':
            content = '\n'.join(v)
            origURL = page_url
            doc = getDocSchema(postID=postID, domain=domain, origURL=origURL, possibleLangs=langs, mediaType=k, 
                               content=content, nowDate=nowDate)
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = getDocSchema(postID=postID, domain=domain, origURL=url, possibleLangs=langs, mediaType=k, 
                                   content=content, nowDate=nowDate)
                docs.append(doc)
                
    post = getStorySchema(postID=postID, postURL=page_url, domain=domain, headline=metadata['headline'], 
                          date_accessed=nowDate, date_updated=date_updated, author=author, docs=docs)
    
    return post

def scraping_indiatoday_historical(links=None, db=None, langs=[], domain=None, body_div=None, header_div=None):
    print(db.count_documents({}))
    for l in tqdm(links, desc="links: "):
        if db.count_documents({'postURL': l}):
            print(f'skipping post: {l}, already in db')
        else:
            post = get_post_indiatoday(l, langs=langs, domain=domain, body_div=body_div, header_div=header_div)
            db.insert_one(post)        
            sleep(randint(5, 15))
            
    print(f'Historical scraping complete: {domain}')
    print(db.count_documents({}))

def run_indiatoday():
    # TODO: make sure indiatoday collects images as well
    dump_links_indiatoday()
    db = get_db()
    header_div = 'div[contains(@class,"node-story")]'
    body_div = 'div[contains(@itemprop,"articleBody")]'
    body_elements = tree.xpath(f'//{body_div}/p')
    
    links = []
    filename = 'india_today_links'
    with open(filename, 'r') as f:
        for l in f:
            links.append(l.strip('\n'))

    scraping_indiatoday_historical(links=links, db=None, langs=[], domain=None, body_div=body_div, header_div=header_div)

if __name__ == '__main__':
    """
    To scrape all articles from each site and upload them to a database run:
    scraping_[site]_historical(...)
    or 
    run_[site](...)

    Please view other helper functions/change parameters 
    if you do not want to crawl the entire website
    """

    #url = 'https://www.boomlive.in/category/fake-news'
    #db = get_db()
    
    #scraping_boomlive_historical(url=url, db=db, langs=['english'], domain='boomlive.in', NUM_PAGES=arange(10, 40))
    #scraping_boomlive_historical(url=url, db=db, langs=['english'], domain='boomlive.in', NUM_PAGES=arange(40, 70))
    #scraping_boomlive_historical(url=url, db=db, langs=['english'], domain='boomlive.in', NUM_PAGES=arange(70, 101))

    pass
