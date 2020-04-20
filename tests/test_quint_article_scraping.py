import unittest

from factchecking_news_sites import get_content_quint
from factchecking_news_sites import setup_driver, get_driver

ARTICLE_URL='https://www.thequint.com/news/webqoof/mp-girl-passed-off-as-one-whose-clothes-were-found-in-tahir-hussain-house'

driver = setup_driver()
driver2 = get_driver(ARTICLE_URL, driver, wait_time=3)
content = get_content_quint(driver)

expected_response = {
    "text": [
        "CLAIM",
        "Suspended Aam Aadmi Party (AAP) councillor Tahir Hussain has been booked under Section 302 of the IPC (punishment for murder) in connection with the death of Intelligence Bureau (IB) officer Ankit Sharma.",
        "Now, an image is being circulated online to claim that a body of a young girl was found in Hussain’s basement and she has been identified as a 13-year-old Jyoti Patidar.",
        "The picture is being circulated online with a claim that reads, “ताहिर को फाँसी दो\nताहिर हुसैन के आतंक की फैक्ट्री घर से जिस लड़की के कपड़े बरामद हुवे थे और उसकी नाले में लाश मिली थी, उसकी पहचान हो चुकी है। 13 साल की ज्योति पाटीदार है। हिंदुओ के घरों पर हमले के बाद, इस लड़की को शांतिदूतो द्वारा ताहिर के घर के अंदर घसीट कर लाया गया, 40-50 शांतिदुतों ने रेप किया और #मारकर_लाश_नाले_में_फेंक_दी |”",
        "[Translation: Hang Tahir. The girl whose clothes were found in Tahir Hussain’s basement and was later found in a drain has now been identified. She is 13-year-old Jyoti Patidar. After attacking the houses of Hindus, she was dragged and taken inside Hussain’s house]",
        "Also Read : Biryani Laced With Drugs for Hindus? No, Photos Are Unrelated",
        "The post has been shared on Facebook by multiple users.",
        "TRUE OR FALSE?",
        "False.",
        "The picture of the girl which is being circulated online is actually from Madhya Pradesh’s Susner. An 18-year-old girl allegedly killed herself in her house while her mother and aunt had gone to the fields. According to the police, the evidence hints towards a possible case of suicide but the investigation is still going on.",
        "WHAT’S THE TRUTH?",
        "On conducting a reverse image search, we came across an article published by Dainik Bhaskar on 21 February which had the same image as the viral post.",
        "According to the article, the body of a girl, identified as Jyoti Patidar was found lying dead on 20 February in Madhya Pradesh’s Parsulya Kalan village. At around 4 pm, the villagers could see smoke coming out of the house, after which, police and fire department were alerted. Jyoti, a student of class 12 was alone at home when the incident took place.",
        "Also Read : Fake Posts Shared to Claim Justice Muralidhar Worked Under Cong MP",
        "The Quint spoke to Vivek Kanodiya, Station House officer (SHO) of Susner police station who confirmed to us that the incident had happened in Parsulya Kalan village and that the police is investigating office.",
        "“The family had accused a boy who lives in their neighborhood, but we have checked records and he wasn’t in the village when the incident happened. However we have filed a case under Section 306 (abetment of suicide) against him,” he added.",
        "Also Read : Fake Posts Shared to Claim Justice Muralidhar Worked Under Cong MP",
        "(Not convinced of a post or information you came across online and want it verified? Send us the details on Whatsapp at 9643651818, or e-mail it to us at webqoof@thequint.com and we'll fact-check it for you. You can also read all our fact-checked stories here.)",
        "We'll get through this! Meanwhile, here's all you need to know about the Coronavirus outbreak to keep yourself safe, informed, and updated.",
        "(Make sure you don't miss fresh news updates from us. Click here to stay updated)"
    ],
    "video": [],
    "image": [
        "https://gumlet.assettype.com/thequint%2F2020-03%2Fd7b4fc48-42d1-4ce1-9006-cb395c8bd4cd%2F1.JPG?auto=format%2Ccompress&w=640",
        "https://gumlet.assettype.com/thequint%2F2020-03%2F6818bc7a-8c86-4a68-81be-77213332450f%2F2.JPG?auto=format%2Ccompress&w=640",
        "https://gumlet.assettype.com/thequint%2F2020-03%2F69268973-f1ce-40a1-a427-07846395848b%2F4.JPG?auto=format%2Ccompress&w=640",
        "https://gumlet.assettype.com/thequint%2F2020-03%2Fec8bd2f0-866d-4de8-bcd9-6288c260f2d9%2Fdainik1.png?auto=format%2Ccompress&w=640"
    ],
    "tweet": [],
    "facebook": [],
    "instagram": []
}

class TestQuintArticleScraping(unittest.TestCase):
    def test_quint_content_value(self):
        self.assertDictEqual(content, expected_response)