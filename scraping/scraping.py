# reference: https://stackoverflow.com/questions/55431998/how-to-scrap-data-from-website-which-is-populated-using-js

# what is a web driver: https://developer.mozilla.org/en-US/docs/Web/WebDriver

# sharechat images are stored in shadow-root elements: https://blog.revillweb.com/open-vs-closed-shadow-dom-9f3d7427d1af?gi=1a449f44d35f

# xpath does not support shadow-DOM scraping: https://stackoverflow.com/questions/49763626/can-xpath-expressions-access-shadow-root-elements

# public viewing of S3 buckets

from selenium import webdriver
from time import sleep
from datetime import date
from wget import download
from os import remove, environ, listdir
from os.path import getmtime
import uuid
from tqdm import tqdm
from pymongo import MongoClient
from mimetypes import guess_type
from dotenv import load_dotenv
load_dotenv()

gecko_driver_path = environ['GECKO_DRIVER_PATH']
SCROLL_PAUSE_TIME = 1
NOT_A_BOT_SLEEP = 1

def sharechat(num_scrolls=10, lang='hindi', wait_time=3):
    # scroll into view of button then click: https://stackoverflow.com/questions/44912203/selenium-web-driver-java-element-is-not-clickable-at-point-x-y-other-elem  
    # download a file and skip dialog: https://stackoverflow.com/questions/18439851/how-can-i-download-a-file-on-a-click-event-using-selenium  
    # download file to specified folder: https://stackoverflow.com/questions/25251583/downloading-file-to-specified-location-with-selenium-and-python  
    
    # get all filepaths in local dir
    # upload to s3
    # delete all files
    # save metadata to mongo
    # make it into a daily job?
    
    serviceurl = 'https://sharechat.com/trending/' + lang

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    # firefox profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'image/jpeg')

    # using firefox gecko driver
    url = serviceurl
    driver = webdriver.Firefox(executable_path=gecko_driver_path, firefox_profile=profile, options=options)
#     driver.maximize_window() #For maximizing window
    driver.get(url)
    driver.implicitly_wait(wait_time) #gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != 'complete':
        pass

    # auto-scrolling
    last_height = driver.execute_script('return document.body.scrollHeight')
    
    for i in tqdm(range(num_scrolls)):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    download_links = driver.find_elements_by_xpath('//button[@aria-label="Click to download"]')    
    
    link = serviceurl
    download_path = '/home/ubuntu/Downloads/'
    
#     all_download_files = listdir(download_path)
#     all_download_files = [f'{download_path}/{f}' for f in all_download_files]
#         latest = max(all_download_files, key=getmtime)
#     last_time = getmtime(latest)
    
    for i, x in tqdm(enumerate(download_links)):
        try:
            driver.execute_script('arguments[0].scrollIntoView()', x)
            try:
                x.click()
            except Exception as e:
                print(f'{i} failed\n{e}')
        except Exception as e:
            print(f'{i} failed\n{e}')
        sleep(NOT_A_BOT_SLEEP)
        
    all_download_files = listdir(download_path)
    all_download_files = [f'{download_path}/{f}' for f in all_download_files]
#     filepaths = [f for f in all_download_files if getmtime(f) > last_time]
    filepaths = all_download_files
    
    # close driver
    driver.close()
        
    return filepaths, link

def get_reddit_image_links(page='/r/Hindi/top/?t=all', num_scrolls=10, wait_time=3):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    # headless driver!
    # https://stackoverflow.com/questions/16180428/can-selenium-webdriver-open-browser-windows-silently-in-background
    driver = webdriver.Firefox(executable_path=gecko_driver_path, options=options)    
    
    url = 'https://www.reddit.com' + page
    driver.get(url)
    driver.implicitly_wait(wait_time) #gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != 'complete':
        pass;    
    
    # auto-scrolling
    last_height = driver.execute_script('return document.body.scrollHeight')
    
    for i in tqdm(range(num_scrolls)):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
    all_imgs = driver.find_elements_by_tag_name('img')
    len(all_imgs)
    imgs = [x for x in all_imgs if x.get_attribute('alt') == 'Post image']
    post_imgs = []
    for x in imgs:
        post_imgs += [x.get_attribute('src')]
    
    # close driver
    driver.close()
    
    print(f'{page} scraped \n')
    print('all images: ', len(all_imgs), '\n', 'post images: ', len(post_imgs), '\n', 'ratio: ', len(post_imgs)/len(all_imgs))
    return post_imgs

def getPriorSchema(postID=None, domain=None, origURL=None, s3URL=None, possibleLangs=None, isGoodPrior=[0,0], mediaType=None, content=None, nowDate=None):
    if postID == None:
        postID = uuid.uuid4().hex
    doc = {
        'postID': postID,  # unique id
        'domain': domain,  # domain/data source
        'origURL': origURL,  # orig scraped url
        's3URL': s3URL,  # url in s3
        'possibleLangs': possibleLangs,  # possible languages in media, user input from source of data
        'isGoodPrior': isGoodPrior,  # no of [-ve votes, +ve votes]
        'mediaType': mediaType,  # ['text', 'image', 'video', 'audio']
        'content': content,  # text, if media_type = text or text in image/audio/video
        'nowDate': nowDate  # date of scraping
    }

    return doc

def process_img_files():
    langs = ['Hindi', 'marathi', 'gujarati', 'punjabi', 'telugu', 'malayalam', 'tamil', 'bengali', 'odia', 'kannada', 'assamese', 'bhojpuri', 'haryanvi', 'rajasthani']
    
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.publicData
    priors = db.priors

    s3_prefix = 'https://tattle-priors.s3.ap-south-1.amazonaws.com/'
    bucket = 'tattle-priors'
    nowDate = date.today().strftime("%B %d, %Y")
    refreshes = 10
    # all_images = []
    
    for r in range(refreshes): 
        for lang in langs:
            image_files, link = sharechat(num_scrolls=1, lang=lang)
            # all_images += image_files
            filenames, contentTypes = image_files_to_s3(image_files, bucket=bucket)

            domain=f'sharechat/{lang}'
            possibleLangs = [lang]

            for i, f in enumerate(tqdm(filenames)):
                f = f.split('/')[-1]  # removes local download path from filename
                s3URL = f'{s3_prefix}{f}'
                # TODO: get mediatype from downloaded file
                doc = getPriorSchema(domain=domain, origURL=link, s3URL=s3URL, mediaType=contentTypes[i].split('/')[0], nowDate=nowDate, possibleLangs=possibleLangs)
                priors.insert_one(doc)

    print('all files metadata stored in ~/data/scraping')
        
def process_img_urls():
    # https://www.reddit.com/r/languagelearning/
    # r/tamil now allows only text posts
    subreddits = ['hindi', 'tamil', 'urdu', 'punjabi', 'LearnFarsi', 'Kannada', 'BengaliLanguage', 'telugu', 'malayalam', 'gujarati', 'marathi', 'mumbai', 'delhi', 'bangalore', 'india']
    # subreddits = ['hindi']
    # domains = {'r/hindi': ['hindi', 'english'], }
    # publicData => priors
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.publicData
    priors = db.priors

    s3_prefix = 'https://tattle-priors.s3.ap-south-1.amazonaws.com/'

    for subreddit in subreddits:
        page = f'/r/{subreddit}/top/?t=all'

        post_imgs = get_reddit_image_links(page, num_scrolls=20)
        bucket = 'tattle-priors'

        filenames = image_links_to_s3(post_imgs, bucket=bucket)

        domain = f'r/{subreddit}'
        # possibleLangs = domains['langs']

        for i, f in enumerate(tqdm(filenames)):
            s3URL = f'{s3_prefix}{f}'
            doc = getPriorSchema(domain=domain, origURL=post_imgs[i], s3URL=s3URL, mediaType='image')
            priors.insert_one(doc)
    
    print('all files metadata stored in ~/data/scraping')

def aws_connection():
    import boto3
    ACCESS_ID = environ['ACCESS_ID']
    ACCESS_KEY = environ['ACCESS_KEY']

    s3 = boto3.client('s3', region_name='ap-south-1',
                      aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)

    return s3

def image_files_to_s3(imgs, bucket):
    # upload filepaths to s3 and return s3 urls
    
    s3 = aws_connection()
    
    filenames = []
    contentTypes = []
    
    for f in tqdm(imgs):
        filename = f.split('/')[-1]
        ContentType = guess_type(f)[0]
        s3.upload_file(f, bucket, filename, ExtraArgs={
            'ContentType': ContentType
        })
        remove(f)
        contentTypes.append(ContentType)
        filenames.append(f)
        
    print('all files uploaded')
    return filenames, contentTypes
        
def image_links_to_s3(imgs, bucket):
    # https://stackoverflow.com/questions/28458590/upload-files-to-s3-bucket-directly-from-a-url
    # upload_file permissions: https://forums.aws.amazon.com/thread.jspa?threadID=263884

    s3 = aws_connection()
    filenames = []

    if type(imgs) == list:
        for i in tqdm(imgs):
            f = download(i)
            filename = f.split('/')[-1]
            ContentType = guess_type(f)[0]
            s3.upload_file(f, bucket, filename, ExtraArgs={
                'ContentType': ContentType
            })
            remove(f)
            filenames.append(f)
    else:
        f = download(imgs)
        filename = f.split('/')[-1]
        s3.upload_file(f, bucket, filename)
        remove(f)
        filenames.append(f)

    print('all files uploaded')
    return filenames

def reddit_api_scrape():
    base_url = 'https://www.reddit.com/'
    data = {'grant_type': 'password', 'username': REDDIT-USERNAME, 'password': REDDIT-PASSWORD}
    auth = requests.auth.HTTPBasicAuth(APP-ID, APP-SECRET)
    r = requests.post(base_url + 'api/v1/access_token',
                    data=data,
                    headers={'user-agent': 'APP-NAME by REDDIT-USERNAME'},
            auth=auth)
    d = r.json()

def get_duplicate_files_from_mongo(db):
    # https://api.mongodb.com/python/current/examples/aggregation.html
    from bson.son import SON
    
    pipeline = [
        {"$group": {"_id": "$s3URL", "count": {"$sum": 1}, "ids": { "$push": "$_id"}, "dates": {"$push": "$nowDate"}}},
        {"$sort": SON([("count", -1), ("_id", -1)])},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    all_duplicates = list(db.aggregate(pipeline))
    duplicates = [y for x in [x['ids'][1:] for x in all_duplicates] for y in x]
    
    return duplicates
    
def remove_duplicates_from_mongo():
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.PublicData.priors
    duplicates = get_duplicate_files_from_mongo(db)
    db.remove({"_id": {"$in": duplicates}})    
    print(f'removed {len(duplicates)} duplicates!')
    
if __name__ == "__main__":
#     process_img_urls()
#     process_img_files()
#     remove_duplicates_from_mongo()
    pass