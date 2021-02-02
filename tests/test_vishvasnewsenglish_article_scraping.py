import unittest
from scraping.factchecking_news_sites import (
    get_tree,
    get_metadata_vishvasnews,
    get_content_vishvasnews,
    get_post_vishvasnews,
)

ARTICLE_URL = "https://www.vishvasnews.com/english/health/fact-check-no-bitter-guard-juice-cannot-cure-novel-coronavirus-health-experts-refute-the-viral-claim/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_vishvasnews(tree)
body_div = "div[@class='lhs-area']"
body_elements = tree.xpath(f"//{body_div}/*[self::p or self::h2]")
content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
post = get_post_vishvasnews(
    ARTICLE_URL, langs=["english"], body_div="div[@class='lhs-area']"
)

expected_metadata = {
    "headline": "Fact Check: No, bitter gourd juice cannot cure novel coronavirus, health experts refute the viral claim",
    "author": "Urvashi Kapoor",
    "author_link": "https://www.vishvasnews.com/english/author/urvashi-kapoor/",
    "date_updated": "March 25, 2020",
}

expected_content = {
    "text": [
        "A viral post on social media claims that the juice of bitter gourd can effectively treat novel coronavirus in 2 hours. The post also mentions the name of the Health Department of Bihar purporting the information to be released by them. Vishvas News investigated and found that the viral claim is false. Medical experts have refuted the claim by saying that there is no evidence supporting the viral claim.",
        "Claim",
        "The post shared on Facebook by a user named Md Shahid reads: The treatment of coronavirus has been found. Scientists have found that consuming the juice of bitter gourd will kill coronavirus in 2 hours. The name of Bihar Health Department Patna has also been mentioned. The archived version of the post can be checked here.",
        "Investigation",
        "Vishvas News started its investigation by contacting Dr. Naveen Chandra Prasad, the Director in Chief of the Disease Control and Public Health section of Bihar’s Department. He said: “This is a false claim. We have not issued any such statement. These are absolutely fake rumours. There is no evidence supporting this claim.“",
        "This means the viral claim has been falsely attributed to the Health Department of the Bihar Government.",
        "We further investigated by finding reports on whether Bitter Gourd can cure coronavirus. According to a report published in Science Direct, bitter gourd has certain health benefits. But, nowhere has it been mentioned that bitter gourd can cure coronavirus in 2 hours.",
        "Vishvas News also spoke to Dr. Vimal N., Pharmacovigilance Officer, Ministry of AYUSH. He also refuted the claim by saying: “This is fake. Bitter gourd is no cure for coronavirus.”",
        "Press Information Bureau has also issued a statement of Twitter and stated that the juice of bitter gourd cannot cure coronavirus. It is a fake claim.  ",
        "As per Centers for Disease Control and Prevention, there is currently no vaccine to prevent 2019-nCoV infection. However, preventive actions can be taken to help prevent the spread of respiratory viruses.    ",
        "Vishvas News has debunked similar viral posts that had spread misinformation about coronavirus. These posts can be checked in Health Fact Check page.   ",
        "\r\n\r\n Conclusion:\r\n\r\n \r\nThe post claiming bitter gourd can cure novel coronavirus in 2 hours is fake. Bihar Health Department has not issued any such statement.\n",
        "Tags",
    ],
    "video": [],
    "image": [
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Fake_News_March25_4.jpg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.gif",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/urvashikapoor-150x150.jpg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/quiz_img.png",
    ],
    "tweet": [
        "https://twitter.com/PIBFactCheck/status/1240226544095621121?ref_src=twsrc%5Etfw"
    ],
    "facebook": [],
    "instagram": [],
}


class TestVishvasNewsEnglishArticleScraping(unittest.TestCase):
    def test_metadata_value(self):
        self.assertDictEqual(metadata, expected_metadata)

    def test_content_value(self):
        self.assertDictEqual(content, expected_content)

    def test_post_structure(self):
        self.assertIn("postID", post)
        self.assertIn("postURL", post)
        self.assertIn("author", post)
        self.assertIn("docs", post)
