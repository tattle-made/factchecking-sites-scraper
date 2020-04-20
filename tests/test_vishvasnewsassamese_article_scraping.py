import unittest
from factchecking_news_sites import get_tree, get_metadata_vishvasnews, get_content_vishvasnews, get_post_vishvasnews

ARTICLE_URL = "https://www.vishvasnews.com/assamese/politics/fact-check-video-of-teacher-of-jaunpur-goes-viral-as-beating-of-bjp-mla/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_vishvasnews(tree)
body_div="div[@class='lhs-area']"
body_elements = tree.xpath(f'//{body_div}/*[self::p or self::h2]')
content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
post = get_post_vishvasnews(ARTICLE_URL, langs=["assamese"], body_div="div[@class='lhs-area']")

expected_metadata = {
    "headline": "Fact Check: জৈনপুৰত অসভ্যালী কৰা  শিক্ষকক পিটন দিছিল,  বিধায়ক বুলি ফটো দি ভাইৰেল হৈছে",
    "author": "Pallavi Mishra",
    "author_link": "https://www.vishvasnews.com/assamese/author/pallavi-mishra/",
    "date_updated": "February 11, 2020"
}

expected_content = {
    "text":[
        "নতুন দিল্লী (বিশ্বাস নিউজ) কাল্পনিক ভাজপা বিধায়ক অনিল উপাধ্যায়ৰ নামত এবাৰ আকৌ পোষ্ট তীব্ৰগতিত ভাইৰেল হৈ আছে | এই পোষ্টটোত দুখন ফটো আছে, য’ত কিছুমান মানুহে এক সন্দেহীক পিটি থকা দেখা গৈছে | এই ফটো দুখন ভাইৰেল কৰি ইউজাৰে দাবী কৰিছে যে যিজনক পিটি আছে তেওঁ দিল্লীৰ ভাজপাৰ\xa0 বিধায়ক অনিল উপাধ্যায় | ",
        "বিশ্বাস নিউজৰ পৰিক্ষাত আগতে\nকেইবাবাৰো প্ৰমানিত হৈছে\xa0 যে ভাজপাত এই\nনামৰ কোনো বিধায়ক নাই | ছোচিয়েল মিডিয়াত অহা অনিল\nউপাধ্যাযৰ নামত নকলী পোষ্ট ভাইৰেল হৈ থাকে | যদি আমি এতিয়া ভাইৰেল হৈ থকা ফটোবোৰৰ কথা কৈ থাকোঁ তেন্তে\nযিজন ব্যক্তিক পিটি থকা দেখা গৈছে ,তেওঁ জৈনপুৰৰ এক চৰকাৰী স্কুলৰ\nসহায়ক শিক্ষক শৈলেন্দ্ৰ ডুবে আছিল | জানুৱাৰী 2020 ত গাঁৱৰ কিছু লোক আৰু ছাত্রৰ অবিভাৱকে স্কুলত সোমাই শিক্ষক\nশৈলেন্দ্ৰ ডুবক পিটিছিলে | এই জনৰ ওপৰত ছাত্রীসকলৰ লগত\nঅসভ্যালি কৰাৰ আৰোপ আছিল|",
        "কি আছিল ভাইৰেল পোষ্টত",
        "ফেচবুক ইউজাৰ পংকজ দুৱৰাই এটা\nভিডিও আপলোড কৰি লিখিছেঃ ” দিল্লীৰ মায়াপুৰীলৈ\xa0 ভোট বিচাৰি গৈছিল ”দিল্লীৰ মায়াপুৰীলৈ ভোট বিচাৰি গৈছিল দিল্লীৰ বিজেপি নেতা অনিল উপাধ্যায়, কিন্তু স্থানীয় মহিলাই উপাধ্যায়ক চাহ খোৱাম বুলি ঘৰৰ ভিতৰলৈ মাতি ঘৰত সোমোৱাই লৈ গুৰুলাগুৰুলকৈ পিটিলে” ",
        "( ফেচবুক পোষ্টৰ লিংক আৰু আৰ্কাইৱ\xa0 লিংক )",
        "অনুসন্ধান",
        "অনুসন্ধানৰ আৰম্ভ কৰোঁতে আমি\nপোনতে এই ফটোবোৰ গুগুল আৰু yandex ত আপলোড কৰি\nচাৰ্চকৰা আৰম্ভ কৰোঁ| আমি সম্বদ্ধিত ঘটনাৰ লগত জড়িত আৰু খবৰ কেইবা ঠাইতো পালোঁ|",
        "নিউজচটেট ডট কমৰ ৱেবচাইটত মজুদ\nখবৰৰৰ ভিডিওত জনোৱা হৈছে যে জৈনপুৰৰ পৱাৰা থানাক্ষেত্রত এখন স্কুলত ছাত্রীসকলৰ লগত\nঅভদ্ৰ ব্যৱহাৰ কৰাৰ কাৰণে শিক্ষকক গাঁৱৰ ৰাইজে\xa0\nপিটিছিলে|",
        "\xa0চাৰ্চ কৰাত আমি abpnews ৱেবচাইটতো এটা খবৰ পালোঁ| তাত এই ঘটনাটোৰ ভিডিও আমি পালোঁ, যি এতিয়া মিছা দাবীৰ সৈতে ভাইৰেল হৈ আছে|\xa0 খবৰটো 24 জানুৱাৰীত পাব্লিচ কৰিছিল| তাত জনাইছিল যে গাঁৱৰ ৰাইজ আৰু শিশুসকলৰ অভিভাৱকে দোষী শিক্ষকক পিটাৰ পাচত তেওঁক পুলিচত গটাই দিয়ে|",
        "তাৰ পাচত আমি গুগুল চাৰ্চৰ সহায় ল’লো| আমি গুগুলত ” জৈনপুৰত শিক্ষকৰ পিটন” বুলি টাইপ কৰি বিচাৰিলোঁ| আমি নৱভাৰত টাইমচ ৰ ৱেবচাইটত এটা খবৰ পালোঁ| তাতো শিক্ষকক পিটাৰ ঘটনাতো জৈনপুৰৰ পৱাৰা থানাক্ষেত্রৰ বুলি জনালে| ঘটনাটো প্ৰাইমেৰী স্কুলৰ আছিল|.এই বাতৰি 24 জানৱাৰী 2020 ত পাব্লিচ হৈছিল| বাতৰিৰ মতে দোষী সহায়ক শিক্ষকজনৰ নাম শৈলেন্দ্ৰ ডুবে|",
        "অনুসন্ধানৰ তাৰ পিচৰ পৰ্য্যায়ত আমি জৈনপুৰৰ পুলিচ অধিকাৰিক টুইটাৰ হেণ্ডেল@jaunpurpolice ত চালোঁ| তাত যেতিয়া আমি হেণ্ডেলক  চাৰ্চ  কৰোঁ তেতিয়া আমি 24 জানুৱাৰী 2020 ৰ এক ট্ইট পোৱা গ’ল| তাত উচ্ছ পুলিচ অধীক্ষক গাঁৱৰ ৰাইজৰ  ট্ইট পোৱা গ’ল| ইয়াত পুলিচ বিষয়াৰক পৱাৰাৰ ঘটনীৰ বিষয়ে জনোৱা হৈছে| শিশুৰ পিতাকৰ অভিযোগৰ পিচত শিক্ষকজনক আটক কৰিলোৱা গ’ল| ",
        "জৈনপুৰৰ এ এচপী গ্ৰমীন অজয় ৰায়েও ঘটনাটোত\xa0 হয়ভয় দি কয় যে আৰোপী শিক্ষকক এৰেষ্ট কৰা হৈছে| ছোচিয়েল মিডিয়াত কি ভাইৰেল হৈ আছে সেই কথা আমি একো নাজানো|",
        "অনুসন্ধানৰ সময়ত আমি Myneta.info ৱেৰচাইটলৈ গ’লো| এই ৱেবচাইটত দেশৰ সমগ্ৰ বিধায়ক আৰু সংসদৰ ৰেকৰ্ড মজুদ আছে| ইয়াত আমি অনিল উপাধ্যায় নামপ বিধায়ক আৰু সংসদক বিচাৰিব ধৰিলোঁ কিন্তু সেই নামৰ কোনো বিধায়কক নাপালোঁ যিজন বৰ্তমান ভাজপাৰ লগত জড়িত|",
        "অন্তত আমি এই পোষ্টটো ছেয়াৰ কৰা\xa0 ফেচবুক একাউন্ট পংকজ দুৱৰাৰ ছোচিয়েল স্কেনিং কৰাৰ নিৰ্ণয় ল’লোঁ| আমি পালো যে ইউজাৰ গুৱাহাটীৰ বাসিন্দা আৰু পেছাত  পত্রকাৰ|",
        "\r\n\r\n নিষ্কৰ্ষঃ\r\n\r\n \r\nবিশ্বাস টিমে নিজৰ অনুসন্ধানত পালে যে অনিল উপাধ্যায় নামৰে ভাইৰেল হৈ থকা পোষ্টটো নকলী| ভাজপাত অনিল উপাধ্যায় নামৰ কোনো বিধায়ক নাই| ভাইৰেল ফটো জৈনপুৰৰ এক চৰকাৰী স্কুলৰ সহকাৰী শিক্ষক শৈলেন্দ্ৰ ডুবেক পিটি থকা ফটো|\n",
        "ট্যাগ্স"
    ],
    "video":[],
    "image":[
        "https://www.vishvasnews.com/wp-content/uploads/2020/02/Fake_News5_fefe.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/02/Untitled-6-1024x629.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/02/Untitled-8.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/02/Untitled-5-6.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/02/Myneta-3-feb-2020-1.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.gif",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png",
        "https://www.vishvasnews.com/wp-content/uploads/2018/11/pallavi.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/bhagvantsingh-150x150.jpeg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/quiz_img.png"
    ],
    "tweet":[
        "https://twitter.com/jaunpurpolice/status/1220572868032876544?ref_src=twsrc%5Etfw"
    ],
    "facebook":[],
    "instagram":[]
}

class TestVishvasNewsAssameseArticleScraping(unittest.TestCase):
    def test_metadata_value(self):
        self.assertDictEqual(metadata, expected_metadata)

    def test_content_value(self):
        self.assertDictEqual(content, expected_content)

    def test_post_structure(self):
        self.assertIn('postID', post)
        self.assertIn('postURL', post)
        self.assertIn('author', post)
        self.assertIn('docs', post)

