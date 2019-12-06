from selenium import webdriver
from time import sleep
from datetime import date, datetime
from os import remove, environ, listdir
from os.path import getmtime
import psutil
import uuid
from tqdm import tqdm
from pymongo import MongoClient
from mimetypes import guess_type
from dotenv import load_dotenv
load_dotenv()

gecko_driver_path = environ['GECKO_DRIVER_PATH']
download_path = environ['DOWNLOAD_PATH']
SCROLL_PAUSE_TIME = 1
NOT_A_BOT_SLEEP = 1

class Scraper():
    def __init__(self, url=None, method=None, **kwargs):
        if url is None:
            print('No URL provided')
            return None
        else:
            self.url = url
        
        ### all possible methods
        # selenium | requests
        if method is None:
            print('No Method provided')
        else:
            self.method = method
        
        ### all possible kwargs
        # lang='hindi'
        # wait_time=3
        # num_scrolls=10
        self.params = kwargs
        
        # other vars
        self.driver = None
        self.posts = []
        
    def load_driver(self):
        if self.method == 'selenium':
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')

            # firefox profile
            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'image/jpeg')
            
            # driver
            driver = webdriver.Firefox(executable_path=gecko_driver_path, firefox_profile=profile, options=options)
        
            self.driver = driver
        else:
            self.driver = None
    
    def get_url(self):
        # driver.maximize_window() #For maximizing window
        self.driver.get(self.url)
        self.driver.implicitly_wait(self.params.get('wait_time', 5)) #gives an implicit wait for n seconds
        while self.driver.execute_script("return document.readyState") != 'complete':
            pass

        # auto-scrolling
        if self.params.get('scroll', None):
            last_height = self.driver.execute_script('return document.body.scrollHeight')

            for i in tqdm(range(self.params.get('num_scrolls', None))):
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                sleep(self.params.get('SCROLL_PAUSE_TIME', 1))
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
    
    def click_download_links_sharechat(self):
        # click and download a list of links
        download_links = self.driver.find_elements_by_xpath('//button[@aria-label="Click to download"]')
        temp = self.driver.find_elements_by_xpath('//section[@class="post-batch"]')
        temp_div = temp[0].find_elements_by_xpath('//div[contains(@class, "Fz($fzcaption)") and contains(@class ,"C($darkTextDisabled)")]//div')
        temp_title_tag = temp[0].find_elements_by_xpath('//div/h3')
        #print(f'download links: {len(download_links)} \n tags: {len(temp_title_tag)} \n div stats: {len(temp_div)}')
        if (len(temp_div) != 2*len(download_links)) or (len(temp_title_tag) != len(download_links)):
            return        

        if self.download_path:
            files = listdir(self.download_path)
            if files:
                for f in files:
                    remove(f'{self.download_path}/{f}')
                print('cleaned download directory')
        
        download_status = []
        for i, x in tqdm(enumerate(download_links)):
            try:
                self.driver.execute_script('arguments[0].scrollIntoView()', x)
                try:
                    x.click()
                    download_status.append('passed')
                except Exception as e:
                    print(f'{i} failed\n{e}')
                    download_status.append('failed')
            except Exception as e:
                print(f'{i} failed\n{e}')
                download_status.append('failed')
            sleep(self.params.get('NOT_A_BOT_SLEEP', 1))

        if self.download_path:
            all_download_files = listdir(self.download_path)
            all_download_files = [f'{self.download_path}/{f}' for f in all_download_files]
            #assert(len(all_download_files) == len(download_links))
            all_download_files = sorted(all_download_files, key=getmtime)
            self.filepaths = all_download_files
        
        #print(download_status)
        #print(f'downloaded files: {len(all_download_files)} \n download links: {len(download_links)} \n tags: {len(temp_title_tag)} \n div stats: {len(temp_div)}')
        i = 0
        #print(all_download_files)
        for f in range(len(download_links)):
            if download_status[f] == 'passed':
                self.posts.append({
                    'filename': all_download_files[i].split('/')[-1],
                    'views': temp_div[f*2].text.split(' ')[0],
                    'timeSince': temp_div[f*2-1].text.split(' ')[:-1],
                    'titleTag': temp_title_tag[f].text
                })
                
                i += 1
            
    def close_driver(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()
            
def getSharechatSchema(postID=None, domain=None, origURL=None, s3URL=None, mediaType=None, content=None, 
                       scrapeDate=None, scrapeTime=None, timeZone=None, postDate=None, postTime=None, 
                       titleTag=None, views=None, tags=None, filename=None, duplicates=None):
    # added nowTime for analysis
    if postID == None:
        postID = uuid.uuid4().hex
    doc = {
        'postID': postID,  # unique id
        'domain': domain,  # domain/data source
        'origURL': origURL,  # orig scraped url
        's3URL': s3URL,  # url in s3
        'mediaType': mediaType,  # ['text', 'image', 'video', 'audio']
        'content': content,  # text, if media_type = text or text in image/audio/video
        'scrapeDate': scrapeDate,  # date of scraping
        'scrapeTime': scrapeTime,  # time of scraping
        'timeZone': timeZone,  # timezone
        'postDate': postDate, # date of post
        'postTime': postTime, # time of post
        'titleTag': titleTag, # tag from sharechat
        'views': views, # no of views on scrapeDate
        'tags': tags,  # misc. tags
        'filename': filename,  # filename on server
        'duplicates': duplicates # duplicates while scraping
    }

    return doc

def image_files_to_s3(imgs, bucket):
    # upload filepaths to s3 and return s3 urls
    
    s3 = aws_connection()
    
    if type(imgs) == list:
        filenames = []
        contentTypes = []

        for f in tqdm(imgs):
            filename = f.split('/')[-1]
            ContentType = guess_type(f)[0]
            S3filename = str(uuid.uuid4())

            s3.upload_file(f, bucket, S3filename, ExtraArgs={
                'ContentType': ContentType
            })
            remove(f)
            contentTypes.append(ContentType)
            filenames.append(S3filename)

        print('all files uploaded')
        return filenames, contentTypes
    elif type(imgs) == str:
        filename = imgs.split('/')[-1]
        ContentType = guess_type(imgs)[0]
        S3filename = str(uuid.uuid4())

        s3.upload_file(imgs, bucket, S3filename, ExtraArgs={
            'ContentType': ContentType
        })
        remove(imgs)

        print('file uploaded')
        return S3filename, ContentType
        
def aws_connection():
    import boto3
    ACCESS_ID = environ['ACCESS_ID']
    ACCESS_KEY = environ['ACCESS_KEY']

    s3 = boto3.client('s3', region_name='ap-south-1',
                      aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)

    return s3

def process_img_files(lang=None):    
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.publicData.sharechat

    bucket = environ['SHARECHAT_BUCKET']
    s3_prefix = f'https://{bucket}.s3.ap-south-1.amazonaws.com/'
    nowDate = date.today().strftime("%B %d, %Y")
    nowTime = datetime.now().strftime("%H:%M:%S")
    timeZone = 'UTC'
    # all_images = []
    
    print(f'##{nowDate}: {nowTime} Starting sharechat/{lang}...##')
    
    url = f'https://sharechat.com/trending/{lang}'
    method = 'selenium'
    wait_time = 5
    scraper = Scraper(url=url, method=method, lang=lang, wait_time=wait_time)
    scraper.load_driver()
    print("scraper loaded...\n")
    scraper.get_url()
    
    scraper.download_path = download_path
    scraper.click_download_links_sharechat()
    filenames = [x['filename'] for x in scraper.posts]
    filepaths = [f'{scraper.download_path}/{x}' for x in filenames]
    
    duplicates = []
    for i in scraper.posts:
        if db.count_documents({'filename': i['filename']}):
            duplicates.append(i['filename'])
    
    timeSince = [x['timeSince'] for x in scraper.posts]
    domain=f'sharechat/{lang}'

    for i, filepath in enumerate(tqdm(filepaths)):
        filename = filenames[i]
        if filename in duplicates:
            db.update_one(
                {'filename': filename},
                {'$inc': {'duplicates': 1}}
            )
        else:
            s3Filename, ContentType = image_files_to_s3(filepath, bucket=bucket)
            s3URL = f'{s3_prefix}{s3Filename}'
            doc = getSharechatSchema(domain=domain, origURL=url, s3URL=s3URL, 
                               mediaType=ContentType.split('/')[0], 
                               scrapeDate=nowDate, scrapeTime=nowTime, timeZone=timeZone, 
                               postDate=scraper.posts[i]['timeSince'], 
                               titleTag=scraper.posts[i]['titleTag'], 
                               views=scraper.posts[i]['views'],
                               filename=scraper.posts[i]['filename'], duplicates=0)
            db.insert_one(doc)

    scraper.close_driver()
    
    print('all files metadata stored in ~/data/scraping')

def kill_processes(proc_name):
    # https://stackoverflow.com/questions/47999568/selenium-how-to-stop-geckodriver-process-impacting-pc-memory-without-calling
    PROCNAME = proc_name # geckodriver or chromedriver or IEDriverServer
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            proc.kill()

if __name__ == "__main__":
#     process_img_files(lang='hindi')
    for i in range(10):
        process_img_files(lang='hindi')
        kill_processes('geckodriver')
        kill_processes('firefox')
        sleep(60)
    for i in range(10):
        process_img_files(lang='gujarati')
        kill_processes('geckodriver')
        kill_processes('firefox')
        sleep(60)
