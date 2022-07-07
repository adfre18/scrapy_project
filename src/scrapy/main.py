from src.scrapy.utils import get_soup_elements, elements_and_ids, get_image_url_and_title, get_title
from tqdm import tqdm

class SimpleScrapyFramework:
    def __init__(self):
        self.num_pages = 12

    def scrape_url(self):
        data = get_soup_elements(typ_obchodu="prodej", typ_stavby="byty", pages=self.num_pages)
        print( "1/8 Data scrapnuta, získávám URLs.")
        data = elements_and_ids(data)
        while data.shape[0] != 200:
            self.num_pages += 1
            data = get_soup_elements(typ_obchodu="prodej", typ_stavby="byty", pages=self.num_pages)
            data = elements_and_ids(data)

        url_ids = data.get('url_id')
        output = []
        for url_id in tqdm(url_ids, desc="Scraping titles and images"):
            image_url, title = get_image_url_and_title(url_id)
            output.append([title, image_url])
        return output
