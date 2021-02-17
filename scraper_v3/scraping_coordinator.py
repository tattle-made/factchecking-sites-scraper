from scraper_boomlive import crawler, article_downloader, article_parser, media_downloader, data_uploader 
import json



def main():
    print('boomlive scraper initiated')
    #links = crawler("https://www.boomlive.in/fact-check",2)
    
    with open("url_list.json","r") as file:
        links = json.load(file)

    #import ipdb; ipdb.set_trace()

    print(links)

    for link in links:
        html_response = article_downloader(link)
        post = article_parser(html_response,link)
        media_items = media_downloader(post)
    #     data_uploader(post,media_items)
    
if __name__ == "__main__":
    main()