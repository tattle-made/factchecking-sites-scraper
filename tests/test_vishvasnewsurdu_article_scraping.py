import unittest
from scraping.factchecking_news_sites import (
    get_tree,
    get_metadata_vishvasnews,
    get_content_vishvasnews,
    get_post_vishvasnews,
)

ARTICLE_URL = "https://www.vishvasnews.com/urdu/viral/fact-check-not-chinese-but-kyrgyz-people-detained-in-patna-over-coronavirus-suspect/"
tree = get_tree(ARTICLE_URL)
metadata = get_metadata_vishvasnews(tree)
body_div = "div[@class='lhs-area']"
body_elements = tree.xpath(f"//{body_div}/*[self::p or self::h2]")
content = get_content_vishvasnews(tree, body_elements, body_div=body_div)
post = get_post_vishvasnews(
    ARTICLE_URL, langs=["urdu"], body_div="div[@class='lhs-area']"
)


expected_metadata = {
    "headline": "فیکٹ چیک: پٹنہ میں مسجد سے چینی مسلمانوں کے پکڑے جانے کا دعویٰ غلط، گمراہ کن دعویٰ کے ساتھ وائرل ہو رہا ویڈیو",
    "author": "Abhishek Parashar",
    "author_link": "https://www.vishvasnews.com/urdu/author/abhishek-parashar/",
    "date_updated": "March 25, 2020",
}

expected_content = {
    "text": [
        "نئی دہلی (وشواس نیوز)۔ سوشل میڈیا پر ایک ویڈیو تیزی سے وائرل ہو رہا ہے، جس میں غیر ملک کے متعدد شہریوں کو باہر نکالتے ہوئے دیکھا جا سکتا ہے۔ دعویٰ کیا جا رہا ہے کہ یہ تمام چینی شہری ہیں، جنہیں پٹنہ پولیس نے ایک مسجد سے پکڑا ہے۔",
        "وشواس نیوز کی پڑتال میں یہ دعویٰ گمراہ کن ثابت ہوا۔ وائرل ہو رہا ویڈیو پٹنہ کا ہے اور اس میں نظر آرہے غیر ملکی افراد کرغستان کے شہری ہیں، نہ کی چین کے مسلمان۔",
        "کیا ہے وائرل پوسٹ میں؟",
        "فیس بک پیج ’ڈاکٹر سدھانشو تریویدی فین کلب‘ نے مذکورہ ویڈیو کو شیئر کرتے ہوئےدعویٰ کیا ہے کہ’’ پٹنہ کے کرجی علاقہ میں اٹلی اور ایران سے آئے تقریبا 50 غیر ملکی شہریوں کو پکڑا گیا‘‘۔",
        " اس پروفائل سے وائرل ویڈیو کو تقریبا 13 ہزار سے زائد لوگ شیئر کر چکے ہیں، تاہم 6400 سے زیادہ لوگوں نے لائک کیا ہے۔ ",
        "پڑتال",
        "ہم نے اپنی پڑتال کا آغاز کیا اور پایا کہ اس معاملہ سے منسلک ایک ویڈیو بھی وائرل کیا جا رہا ہے  جسے فیس بک پر صارفین شیئر کر رہے ہیں۔",
        "فیس بک صارف ’بہار آج تک لائو‘ نے اس ویڈیو کو شیئر کرتے ہوئے دعویٰ کیا ہے کہ، ’’پٹنہ کے کرجی مسجد میں چینی مسلمان گزشتہ ایک ماہ سے پوشیدہ رہ رہے تھے، جنہیں پولیس پکڑ کر لے گئی‘‘۔",
        "وہیں، فیس بک پیج لائیو بہار نے اس ویڈیو کو شیئر کرتے ہوئے دعویٰ کیا کہ پٹنہ پولیس نے جرمنی اور اٹلی سے آئی 12 غیر ملکی مسلمانوں کو پکڑا ہے۔",
        "ویڈیو میں ایک شخص کو یہ کہتے ہوئے سنا جا سکتا ہے، ’’اے تو لوگ بہار میں کیسے چلے آئے رے….‘‘۔ وہیں دوسرے عادمی کو مقامی زبان میں یہ کہتے ہوئے سنا جا سکتا ہے، ’’اب برداشت نہیں ہوگا…ای سب غیر ملکی عادمی کو اٹھا کر لے آئے ہو‘‘۔ ویڈیو میں بہار پولیس کے ایک جوان بھی دیکھا جا سکتا ہے۔",
        "ویڈیو سے ملی معلومات کے بنیاد پر نیوز سرچ کرنے پر نیوز ایجنسی پی ٹی آئی کا ٹویٹ ملا، جس کے مطابق پٹنہ پولیس نے کرغستان کے 10 شہریوں اور 2 ہندوستانیوں کو حراست میں لے کر انہیں جانچ کے لئے ایمس بھیجا ہے۔",
        "آوٹ لک انڈیا میں پی ٹی آئی کے حوالے سے شائع رپورٹ کے مطابق، ’بہارکے پٹنہ میں پولیس نے کرغستان کے 10 شہریوں اور دو ہندوستانیوں کو کورونا وائرس سے انفیکٹڈ ہونے کے شبہ میں پکڑا گیا ہے، جن کے سیپمل کو جانچ کے لئے ایمس بھیجا گیا ہے‘‘۔",
        "خبر کے مطابق، مقامی لوگوں کی شکایت پر پولیس نے پٹنہ کے کرجی علاقہ میں واقع ایک مسجد سے 12 لوگوں کو پکڑا، جس میں سے 10 غیر ملکی ہیں، جبکہ دو شخص گائڈ ہیں، جو اتر پردیش کے رہنے والے ہیں۔ رپورٹ کے مطابق، ان میں سے چھ لوگوں کی جانچ رپورٹ نگیٹیو آئی ہیں۔",
        "وشواس نیوز نے اسے لے کر دیگھا تھانہ انچارج منوج کمار سے بات کی۔ انہوں نے بتایا، ’’ہم نے مقامی لوگوں کی شکایت پر مسجد سے 12 لوگوں کو حراست میں لیا، جس میں 10 غیر ملک کے، جب کہ دو اترپردیش کے رہنے والے ہیں‘‘۔ انہوں نے بتایا، ’’وائرل ہو رہا ویڈیو پٹنہ کا ہی ہے اور اس میں نظر آرہے غیر ملکی افراد کرغستان کے رہنے والے ہیں، نہ کی چین کے‘‘۔",
        "پی ٹی آئی کی رپورٹ کے مطابق ، تمام غیر ملکی اسلام کے مبلغین ہیں۔ انہوں نے بتایا کہ تمام لوگوں کو حراست میں لے کر ان کی جانچ کے لئے انہیں پٹنہ کے ایمس بھیجا گیا۔",
        "وشواس نیوز نے اس معاملہ کو لے کر پٹنہ کے سٹی ایس پی (سنٹرل) سے بات کی۔ یہ پوچھے جانے پر کیا حراست میں لئے گئے شخص چینی شہری ہیں، سٹی ایس پی امرکیش ڈی نے کہا، ’کل 12 لوگوں کو پکڑا گیا تھا، جس میں 10 غیر ملکی ہیں اور تمام افراد کرغستان کے شہری ہیں‘‘۔ غیر ملکی شہریوں کے ملک میں غیر قانونی طریقہ سے رہنے کے بارے میں پوچھے جانے پر انہوں نے کہا، ’’سبھی شہریوں کے قانونی دستاویز ہیں اور اس میں سے کوئی بھی غیر قانونی طریقہ سے پٹنہ میں نہیں رہ رہا تھا۔ فی الحال ان لوگوں کو کوارنٹائن میں رکھا گیا ہے‘‘۔",
        "اب باری تھی اس ویڈیو کو فرضی دعویٰ کے ساتھ وائرل کرنے والے فیس بک پیج ’ڈاکٹر سدھانشو تریویدی فین کلب‘ کی سوشل اسکیننگ کرنے کی۔ ہم نے پایا کہ اس پیج کو132,948 فالوو کرتے ہیں۔",
        "\r\n\r\n نتیجہ:\r\n\r\n \r\nبہار کی دارالحکومت پٹنہ کے ایک مسجد میں چینی مسلمانوں کے پکڑے جانے کے دعویٰ کے ساتھ وائرل ہو رہا ویڈیو گمراہ کن ہے۔ پکڑے گئے تمام شہری کرغستان کے ہیں، جنہیں حراست میں لے کر کوارنٹائن میں رکھا گیا ہے۔\n",
        "ٹیگز",
    ],
    "video": [
        "https://www.facebook.com/plugins/video.phphref=https%3A%2F%2Fwww.facebook.com%2Fbiharaajtaknews%2Fvideos%2F214502123240698%2F&show_text=0&width=261",
        "https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Flivebihar.live%2Fvideos%2F2628143930755278%2F&show_text=0&width=261",
    ],
    "image": [
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/Fake_News_March25_9.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/image-95.png",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/image-93.png",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/image-94.png",
        "https://www.vishvasnews.com/wp-content/uploads/2020/03/صارفین-2-1024x337.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.gif",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png",
        "https://www.vishvasnews.com/wp-content/uploads/2019/07/abhishekprashar-150x150.jpg",
        "https://www.vishvasnews.com/wp-content/uploads/2019/08/2017-11-25-14-24-26-050-150x150.jpg",
        "https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/quiz_img.png",
    ],
    "tweet": [
        "https://twitter.com/PTI_News/status/1242037544046317568?ref_src=twsrc%5Etfw"
    ],
    "facebook": [],
    "instagram": [],
}


class TestVishvasNewsUrduArticleScraping(unittest.TestCase):
    def test_metadata_value(self):
        self.assertDictEqual(metadata, expected_metadata)

    def test_content_value(self):
        self.assertDictEqual(content, expected_content)

    def test_post_structure(self):
        self.assertIn("postID", post)
        self.assertIn("postURL", post)
        self.assertIn("author", post)
        self.assertIn("docs", post)
