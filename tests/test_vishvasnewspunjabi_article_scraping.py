import unittest
from factchecking_news_sites import get_tree, get_metadata_vishvasnews, get_content_vishvasnews, get_post_vishvasnews

ARTICLE_URL = "https://www.vishvasnews.com/punjabi/society/fact-check-corona-virus-cannot-cure-by-gargling-with-warm-salty-water/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_vishvasnews(tree)
body_div="div[@class='lhs-area']"
body_elements = tree.xpath(f'//{body_div}/*[self::p or self::h2]')
content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
post = get_post_vishvasnews(ARTICLE_URL, langs=["punjabi"], body_div="div[@class='lhs-area']")

expected_metadata = {
    "headline": "Fact Check: ਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਜਾਂ ਵਿਨੇਗਰ ਪਾ ਕੇ ਗਰਾਰੇ ਕਰਨ ਨਾਲ ਨਹੀਂ ਠੀਕ ਹੁੰਦਾ ਹੈ ਕੋਰੋਨਾ ਵਾਇਰਸ, ਫਰਜ਼ੀ ਪੋਸਟ ਹੋ ਰਿਹਾ ਹੈ ਵਾਇਰਲ",
    "author": "Abhishek Parashar",
    "author_link": "https://www.vishvasnews.com/punjabi/author/abhishek-parashar/",
    "date_updated": "March 26, 2020"
}

expected_content = {
    "text": [
        "ਨਵੀਂ ਦਿੱਲੀ (ਵਿਸ਼ਵਾਸ ਟੀਮ)। ਕੋਰੋਨਾ ਵਾਇਰਸ ਦੇ ਵਧਦੇ ਪ੍ਰਕੋਪ ਵਿਚਕਾਰ ਸੋਸ਼ਲ ਮੀਡੀਆ ‘ਤੇ ਇਸਦੇ ਇਲਾਜ ਨੂੰ ਲੈ ਕੇ ਕਈ ਤਰ੍ਹਾਂ ਦੇ ਅਫਵਾਹਾਂ ਨੂੰ ਵਾਧਾ ਦਿੱਤਾ ਜਾ ਰਿਹਾ ਹੈ। ਵਾਇਰਲ ਪੋਸਟ ਵਿਚ ਦਾਅਵਾ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ ਕਿ ਕੋਰੋਨਾ ਵਾਇਰਸ ਕਿਸੇ ਵਿਅਕਤੀ ਦੇ ਗਲੇ ਵਿਚ ਚਾਰ ਦਿਨਾਂ ਤਕ ਰਹਿੰਦਾ ਹੈ ਅਤੇ ਇਸ ਦੌਰਾਨ ਜੇਕਰ ਕੋਈ ਵਿਅਕਤੀ ਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਜਾਂ ਵਿਨੇਗਰ ਪਾ ਕੇ ਉਸਦੀ ਵਰਤੋਂ ਕਰੇ ਤਾਂ ਉਹ ਇਸ ਵਾਇਰਸ ਤੋਂ ਮੁਕਤ ਹੋ ਜਾਵੇਗਾ।",
        "ਵਿਸ਼ਵਾਸ ਟੀਮ ਦੀ ਪੜਤਾਲ ਵਿਚ ਇਹ ਦਾਅਵਾ ਫਰਜ਼ੀ ਸਾਬਿਤ ਹੋਇਆ। ਡਾਕਟਰਾਂ ਮੁਤਾਬਕ ਗਰਮ ਪਾਣੀ ਦੀ ਮਦਦ ਤੋਂ ਗਲੇ ਨੂੰ ਸਾਫ ਤਾਂ ਜ਼ਰੂਰ ਕੀਤਾ ਜਾ ਸਕਦਾ ਹੈ ਪਰ ਇਹ ਸਾਫ ਤੋਰ ‘ਤੇ ਕੋਰੋਨਾ ਵਾਇਰਸ ਦਾ ਇਲਾਜ ਨਹੀਂ ਹੈ।",
        "ਕੀ ਹੋ ਰਿਹਾ ਹੈ ਵਾਇਰਲ?",
        "ਫੇਸਬੁੱਕ ਯੂਜ਼ਰ ‘Vijay Sharma’ ਨੇ ਇੰਫਰੋਗ੍ਰਾਫੀਕਸ ਨੂੰ ਸ਼ੇਅਰ ਕਰਦੇ ਹੋਏ ਲਿਖਿਆ ਹੈ, ‘ਕੋਰੋਨਾ ਵਾਇਰਸ ਫੇਫੜਿਆਂ ਵਿਚ ਪੁੱਜਣ ਤੋਂ ਪਹਿਲਾਂ ਉਹ ਗਲੇ ਵਿਚ 4 ਦਿਨਾਂ ਤਕ ਰਹਿੰਦਾ ਹੈ। ਉਸ ਵਿਚਕਾਰ ਵਿਅਕਤੀ ਦੇ ਗਲ ਵਿਚ ਦਰਦ ਅਤੇ ਖੰਗ ਦੀ ਸ਼ਿਕਾਇਤ ਰਹਿੰਦੀ ਹੈ। ਜੇਕਰ ਤੁਸੀਂ ਜ਼ਿਆਦਾ ਪਾਣੀ ਪੀਂਦੇ ਹੋ ਅਤੇ ਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਜਾਂ ਵਿਨੇਗਰ ਪਾ ਕੇ ਗਰਾਰੇ ਕਰਦੇ ਹੋ ਤਾਂ ਵਾਇਰਸ ਖਤਮ ਹੋ ਜਾਂਦਾ ਹੈ। ਇਹ ਜਾਣਕਾਰੀ ਸਾਰਿਆਂ ਤਕ ਭੇਜੋ, ਕਿਓਂਕਿ ਤੁਸੀਂ ਕਿਸੇ ਦੀ ਜਾਨ ਬਚਾ ਸਕਦੇ ਹੋ ਇਸ ਜਾਣਕਾਰੀ ਨੂੰ ਭੇਜ ਕੇ। ਜਨਹਿੱਤ ਵਿਚ ਜਾਰੀ।’",
        "ਵਾਇਰਲ ਪੋਸਟ ਦਾ ਆਰਕਾਇਵਡ ਲਿੰਕ। ",
        "ਪੜਤਾਲ",
        "ਵਾਇਰਲ ਪੋਸਟ ਵਿਚ ਦਾਅਵਾ ਕੀਤਾ ਗਿਆ ਹੈ ਕਿ ਕੋਰੋਨਾ ਵਾਇਰਸ ਗਲੇ ਵਿਚ 4 ਦਿਨਾਂ ਤਕ ਜ਼ਿੰਦਾ ਰਹਿੰਦਾ ਹੈ। ਇਸ ਬਾਰੇ ਵਿਚ ਜਦੋਂ ਅਸੀਂ ਵਿਸ਼ਵ ਸਿਹਤ ਸੰਗਠਨ (WHO) ਦੀ ਰਿਪੋਰਟ ਨੂੰ ਵੇਖਿਆ ਤਾਂ ਪਤਾ ਚਲਿਆ ਕਿ ਇਸ ਵਾਇਰਸ ਦੇ ਜ਼ਿੰਦਾ ਰਹਿਣ ਦੀ ਅਵਧੀ 1-14 ਦਿਨਾਂ ਤਕ ਹੈ। ਵੱਧ ਮਾਮਲਿਆਂ ਵਿਚ ਇਹ ਅਵਧੀ ਕਰੀਬ 5 ਦਿਨਾਂ ਦੀ ਹੈ।",
        "WHO ਦੀ ਇੱਕ ਰਿਪੋਰਟ ਮੁਤਾਬਕ ਖਾਰੇ ਪਾਣੀ ਨਾਲ ਨੱਕ ਨੂੰ ਵਾਰ-ਵਾਰ ਸਾਫ ਕਰਨ ਨਾਲ ਇਸ ਵਾਇਰਸ ਤੋਂ ਬਚਾਅ ਦਾ ਦਾਅਵਾ ਗਲਤ ਹੈ। ਹਾਲਾਂਕਿ, ਅਜਿਹਾ ਕਰਨ ਨਾਲ ਸਰਦੀ-ਜ਼ੁਖਾਮ ਨਾਲ ਰਾਹਤ ਮਿਲ ਸਕਦੀ ਹੈ ਅਤੇ ਇਸਦੇ ਵੀ ਘੱਟ ਹੀ ਦਾਅਵੇ ਹਨ। ਪਰ ਇਹ ਕੋਰੋਨਾ ਵਾਇਰਸ ਨੂੰ ਠੀਕ ਕਰ ਸਕਦਾ ਹੈ, ਕਹਿਣਾ ਗਲਤ ਹੈ।",
        "ਪ੍ਰੈਸ ਇਨਫੋਰਮੇਸ਼ਨ ਬਿਊਰੋ ਨੇ ਵੀ ਇਸ ਦਾਅਵੇ ਨੂੰ ਗਲਤ ਦੱਸਦੇ ਹੋਏ ਕਿਹਾ ਹੈ ਕਿ ਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਜਾਂ ਵਿਨੇਗਰ ਨੂੰ ਮਿਲਾ ਕੇ ਗਰਾਰੇ ਕਰਨ ਨਾਲ ਵਾਇਰਸ ਨੂੰ ਠੀਕ ਨਹੀਂ ਕੀਤਾ ਜਾ ਸਕਦਾ ਹੈ। PIB ਮੁਤਾਬਕ ਇਹ ਖਬਰ ਫਰਜ਼ੀ ਹੈ, ਜਿਹੜੀ ਸੋਸ਼ਲ ਮੀਡੀਆ ਤੇ ਵਹਟਸਅੱਪ ‘ਤੇ ਫੈਲਾਈ ਜਾ ਰਹੀ ਹੈ।",
        "ਸੈਂਟਰ ਫਾਰ ਡਿਜ਼ੀਜ ਕੰਟਰੋਲ ਅਤੇ ਪ੍ਰਿਵੈਂਸ਼ਨ ਮੁਤਾਬਕ ਫਿਲਹਾਲ ਕੋਰੋਨਾ ਵਾਇਰਸ ਦੇ ਇਲਾਜ ਲਈ ਕੋਈ ਵੈਕਸੀਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।",
        "ਵਿਸ਼ਵਾਸ ਨਿਊਜ਼ ਨੇ ਇਸਨੂੰ ਲੈ ਕੇ ਆਯੂਸ਼ ਮੰਤਰਾਲੇ ਦੇ ਫਾਰਮੋਕੋਵਿਲੀਜੈਂਸ ਅਫਸਰ ਡਾਕਟਰ ਵਿਮਲ ਐਨ ਨਾਲ ਗੱਲ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਕਿਹਾ, ‘ਇਹ ਕੋਰੋਨਾ ਵਾਇਰਸ ਦੇ ਸੰਕ੍ਰਮਣ ਦਾ ਇਲਾਜ ਨਹੀਂ ਹੈ। ਇਸ ਗੱਲ ਦੇ ਵੀ ਘੱਟ ਸਬੂਤ ਹਨ ਕਿ ਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਪਾ ਕੇ ਗਰਾਰੇ ਕਰਨ ਨਾਲ ਸਰਦੀ ਤੋਂ ਰਾਹਤ ਮਿਲਦੀ ਹੈ ਪਰ ਇਸਦਾ ਮਤਲਬ ਇਹ ਨਹੀਂ ਕਿ ਇਸ ਨਾਲ ਕੋਰੋਨਾ ਵਾਇਰਸ ਦਾ ਇਲਾਜ ਕੀਤਾ ਜਾ ਸਕਦਾ ਹੈ’",
        "ਇਸ ਪੋਸਟ ਨੂੰ ਕਈ ਸਾਰੇ ਯੂਜ਼ਰ ਸ਼ੇਅਰ ਕਰ ਰਹੇ ਹਨ ਅਤੇ ਇਨ੍ਹਾਂ ਵਿਚੋਂ ਦੀ ਹੀ ਇੱਕ ਹੈ Vijay Sharma ਨਾਂ ਦੀ ਫੇਸਬੁੱਕ ਪ੍ਰੋਫ਼ਾਈਲ।",
        "\r\n\r\n ਨਤੀਜਾ:\r\n\r\n \r\nਗਰਮ ਪਾਣੀ ਵਿਚ ਨਮਕ ਜਾਂ ਵਿਨੇਗਰ ਪਾ ਕੇ ਗਰਾਰੇ ਕਰਨ ਨਾਲ ਕੋਰੋਨਾ ਵਾਇਰਸ ਠੀਕ ਹੁੰਦਾ ਹੈ ਦਾ ਵਾਇਰਲ ਹੋ ਰਿਹਾ ਦਾਅਵਾ ਫਰਜ਼ੀ ਹੈ।\n",
        "Tags"
    ],
    "video": [],
    "image": [
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Fake_News_March_26_1.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/image-80.png",
        "https://www.who.int/images/default-source/health-topics/coronavirus/myth-busters/23.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.gif",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/abhishekprashar-150x150.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/bhagvantsingh-150x150.jpeg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/quiz_img.png"
    ],
    "tweet": [],
    "facebook": [],
    "instagram": []
}

class TestVishvasNewsHindiArticleScraping(unittest.TestCase):
    def test_metadata_value(self):
        self.assertDictEqual(metadata, expected_metadata)

    def test_content_value(self):
        self.assertDictEqual(content, expected_content)

    def test_post_structure(self):
        self.assertIn('postID', post)
        self.assertIn('postURL', post)
        self.assertIn('author', post)
        self.assertIn('docs', post)

