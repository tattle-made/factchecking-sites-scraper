import unittest
from factchecking_news_sites import get_tree, get_metadata_altnews, get_content_altnews, get_post_altnews

ARTICLE_URL = "https://www.altnews.in/old-images-from-rawalpindi-pakistan-shared-as-crowd-during-lockdown-in-kolkata-west-bengal/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_altnews(tree)
body_elements = tree.xpath('//div[contains(@class, herald-entry-content)]/*[self::p or self::h2 or self::iframe or self::twitter-widget]')
content = get_content_altnews(tree, body_elements)
post = get_post_altnews(ARTICLE_URL, langs=["english"], domain='altnews.in')

expected_metadata = {
    "headline": "Coronavirus: Old images from Kolkata and Pakistan falsely shared as curfew violation in West Bengal",
    "author": "Priyanka Jha",
    "author_link": "https://www.altnews.in/author/priyanka-jha/",
    "date_updated": "31st March 2020"
}

expected_content = {
    "text": [
        "A set of images is going viral on social media with the claim that it depicts the violation of coronavirus lockdown in West Bengal’s Kolkata. A Facebook user posted these images with the caption, “দেখুন আজ কলকাতার মেটিয়াবুরুজ এ LOCK DOWN চিত্র (See the picture of lockdown in Kolkata’s Metiabruz today.)” The post has been shared more than 1500 times so far.",
        "A few more individuals have posted the images with the same narrative. Meghalaya’s Governor Tathagata Roy also retweeted the images posted on Twitter. The tweet says, “Government relief should be given to only those people who abide by the rules of lockdown. Those. who don’t, shouldn’t get benefits, relief and (medical) treatment from the government.”",
        "Facebook user Ram Tapas Chandra Roy posted a set of images with the same claim. It has garnered close to 1,300 shares.",
        "In the course of this article, we will trace the images back to their earliest possible source and find their context.",
        "Image 1",
        "This image is not from India let alone Kolkata, West Bengal. It’s available on the image-sharing platform Flickr. According to the website, it’s a 2007 image from Pakistan’s Rawalpindi and it depicts the Bara Market located in the city.",
        "The image was shot on April 15, 2007, which means that it’s more than 12 years old.",
        "Image 2\xa0",
        "A reverse search of this image revealed that while the image is from Kolkata, it was clicked last year. We found this image was published along with a July 2019 Times of India report. “Vehicles moving towards the station from the north will be diverted along BB Ganguly street and asked go under Sealdah flyover to reach their destination,” reads the text inscribed below the image.",
        "Image 3",
        "The image too depicts Raja Bazar market in Pakistan’s Rawalpindi. We independently verified the location where this image was shot. It was uploaded on Reddit on October 15, 2014.",
        "However, the EXIF data of this image shows that it was clicked on July 7, 2013. Hence, the image is almost seven years old.",
        "Image 4",
        "This image has a watermark, “Jaihoon.com”. A Google reverse image search led us to the same website.\xa0According to the website, the image was shot on August 11, 2017. The filename of the image reads, “bengal-rajabazar4”.",
        "The EXIF data of the image also corroborates the date when it was clicked. Thus, the image is more than two years old. ",
        "In conclusion, old and unrelated images from Kolkata and Pakistan’s Rawalpindi were shared with the false claim that people are flouting lockdown rules in Kolkata, West Bengal.",
        "Donate Now",
        "Enter your email address to subscribe to Alt News and receive notifications of new posts by email."
    ],
    "video": [],
    "image": [
        "https://i0.wp.com/www.altnews.in/wp-content/uploads/2020/03/kolkata.jpg?resize=512%2C692",
        "https://i1.wp.com/www.altnews.in/wp-content/uploads/2020/03/tathagata.jpg?resize=698%2C559",
        "https://i2.wp.com/www.altnews.in/wp-content/uploads/2020/03/2020-03-31-11_41_52-1-Facebook.jpg?resize=441%2C575",
        "https://i1.wp.com/www.altnews.in/wp-content/uploads/2020/03/rawalpindi.jpg?resize=1320%2C750",
        "https://i0.wp.com/www.altnews.in/wp-content/uploads/2020/03/kolkata-traffic.jpg?resize=843%2C791",
        "https://i1.wp.com/www.altnews.in/wp-content/uploads/2020/03/rawalpindi-raja-bazar.jpg?resize=1320%2C712",
        "https://i1.wp.com/www.altnews.in/wp-content/uploads/2020/03/2020-03-31-11_26_02-Photos.png?resize=506%2C707",
        "https://i1.wp.com/www.altnews.in/wp-content/uploads/2020/03/bengal-rajabazar4.jpg?resize=1280%2C800",
        "https://i2.wp.com/www.altnews.in/wp-content/uploads/2020/03/2020-03-31-11_39_52-Photos.png?resize=503%2C763"
    ],
    "tweet": []
}


class TestAltnewsArticleScraping(unittest.TestCase):
    def test_metadata_value(self):
        self.assertDictEqual(metadata, expected_metadata)

    def test_content_value(self):
        self.assertDictEqual(content, expected_content)

    def test_post_structure(self):
        self.assertIn('postID', post)
        self.assertIn('postURL', post)
        self.assertIn('author', post)
        self.assertIn('docs', post)