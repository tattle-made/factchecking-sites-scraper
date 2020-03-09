from factchecking_news_sites import get_content_quint, get_content_quint_test
from factchecking_news_sites import setup_driver, get_driver

def test_quint():
    ARTICLE_URL='https://www.thequint.com/news/webqoof/mp-girl-passed-off-as-one-whose-clothes-were-found-in-tahir-hussain-house'

    driver = setup_driver()
    driver2 = get_driver(ARTICLE_URL, driver, wait_time=3)
    content = get_content_quint_test(driver)
    print(content)

test_quint()

