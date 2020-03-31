import unittest
from factchecking_news_sites import get_tree, get_metadata_vishvasnews, get_content_vishvasnews, get_post_vishvasnews

ARTICLE_URL = "https://www.vishvasnews.com/viral/fact-check-fireball-did-not-fall-from-the-sky-in-the-village-of-nalanda/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_vishvasnews(tree)
body_div="div[@class='lhs-area']"
body_elements = tree.xpath(f'//{body_div}/*[self::p or self::h2]')
content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
post = get_post_vishvasnews(ARTICLE_URL, langs=["hindi"], body_div="div[@class='lhs-area']")

expected_metadata = {
    "headline": "Fact Check : नालंदा के गांव में आसमान से नहीं गिरा आग का गोला",
    "author": "Ashish Maharishi",
    "author_link": "https://www.vishvasnews.com/author/ashish-maharishi/",
    "date_updated": "March 28, 2020"
}

expected_content = {
    "text": [
        "नई दिल्‍ली (विश्‍वास न्‍यूज)। सोशल मीडिया में एक खबर आग की तरह फैल रही है। इसमें दावा किया जा रहा है कि बिहार के नालंदा के एक गांव में आसमान से आग का गोला गिरने से आग लग गई। ",
        "विश्‍वास न्‍यूज ने जब वायरल खबर की पड़ताल निकली तो यह फर्जी निकली। नालंदा के हिलसा थाना इलाके लोहंडा बाजार में आग तो लगी थी, लेकिन यह सामान्‍य आग थी। आसमान से गोला गिरने की बात सिर्फ अफवाह साबित हुई।  ",
        "क्‍या हो रहा है वायरल ",
        "फेसबुक पेज Jiyo TV Bihar ने 27 मार्च को दोपहर में 2:35 मिनट पर एक खबर को पोस्‍ट किया। खबर में एक प्रतीकात्‍मक तस्‍वीर लगाते हुए हेडिंग में लिखा गया कि महामारी के बीच आसमान से गिरा आग का गोला। ",
        "पड़ताल ",
        "विश्‍वास न्‍यूज ने सबसे पहले वायरल खबर को पूरा पढ़ा। हेडिंग और इंट्रो में कहा गया कि नालंदा के हिलसा थाना इलाके के लोहंडा बाजार में आसमान से आग का गोला गिरने के कारण आग लग गई। खबर के अंत में बताया गया कि झोपड़ी में आग लगने के कोई साक्ष्‍य नहीं मिले। लेकिन खबर की हेडिंग और इंट्रो को इस प्रकार से लिखा गया कि जिससे खबर और फेसबुक पोस्‍ट फेक की श्रेणी में आती है। खबर को आप यहां पढ़ सकते हैं। ",
        "इसके बाद हमने गूगल में ‘नालंदा में आग का गोला गिरा’ कीवर्ड टाइप करके सर्च किया। हमें ऐसी कोई खबर नहीं मिली, जो इस बात की पुष्टि करती हो कि वाकई आग का गोला गिरा था। ",
        "पड़ताल के अगले चरण में सच्‍चाई जानने के लिए हमने दैनिक जागरण नालंदा के संवाददाता रजनीकांत से संपर्क किया। उन्‍होंने बताया कि आग का गोला लगने की बात अफवाह थी। इसके बाद उन्‍होंने हिलसा थाना के एसएचओ सुरेश प्रसाद से की। उन्‍होंने बताया कि घटना स्‍थल पर वे खुद गए थे। जिस झोपड़ी में आग लगी थी, उसके बगल में एक चाय की दुकान है। हो सकता है कि उसी दुकान की वजह से आग लगी हो। लेकिन आग का गोला वाली बात झूठी है। ",
        "इसके बाद हमने हिलसा अनुमंडल के एसडीपीओ मोहम्‍मद इम्तियाज से बात की। विश्‍वास न्‍यूज से बातचीत में उन्‍होंने बताया, ”आसमान से आग का गोला गिरने की बात झूठी है। गांव में आग लगी थी, लेकिन यह कहना कि आसमान से कोई गोला गिरा और आग लग गई, फर्जी बात है।”",
        "अब हमें यह जानना था कि खबर में इस्‍तेमाल की गई कवर इमेज कहां की है। इसके लिए हमने इस तस्‍वीर को गूगल रिवर्स इमेज की मदद से खोजना शुरू किया। हमें यह तस्‍वीर metro.co.uk नाम की वेबसाइट पर मिली। इसे 27 जनवरी 2016 को पब्लिश की गई थी। इसमें बताया गया कि पुर्तगाल के मैडिएरा आइलैंड के आसमान में यह नजारा देखने को मिला। पूरी खबर आप यहां पढ़ सकते हैं। ",
        "अंत में हमने भ्रामक खबर फैलाने वाली वेबसाइट और Jio TV Bihar और jiobihar.com की जांच की। हमें पता चला कि इसमें बिहार की खबरों को प्रमुखता से पब्लिश किया जाता है। इसके फेसबुक पेज को 21 हजार से ज्‍यादा लोग फॉलो करते हैं। ",
        "\r\n\r\n निष्कर्ष:\r\n\r\n \r\nविश्‍वास न्‍यूज की पड़ताल में ‘नालंदा के लोहंडा बाजार में आसामन से आग का गोला’ गिरने की खबर गलत साबित हुई। गांव में आग लगी थी। लेकिन आसमान से गोला गिरने की बात पूरी तरह निराधार है। \n",
        "टैग्स"
    ],
    "video": [],
    "image": [
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Fake_News03_28march2020.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Capture-2-1024x755.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/hand-of-god-28-march.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Capture-aag-ka-gola.jpg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.gif",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png",
        "https://www.vishvasnews.com/wp-content/uploads/2018/11/ashish.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/abhishekprashar-150x150.jpg",
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