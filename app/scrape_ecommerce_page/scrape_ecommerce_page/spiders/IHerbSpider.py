import scrapy
import sqlite3
import os


class IHerbCategorySpider(scrapy.Spider):
    name = "iherb"
    # Ethical delay to not trigger Lazada's security measures.
    # Rapid crawling led to pages not being loaded correctly.
    custom_settings = {"DOWNLOAD_DELAY": 1}

    def start_requests(self):
        url = "https://my.iherb.com/c/categories"
        yield scrapy.Request(url=url, callback=self.parse, meta={'category_chain': []})

    def parse(self, response):
        parent_chain = response.meta["category_chain"]
        self.log("Current chain: {}".format(str(parent_chain)))

        sub_categories = [cat.get() for cat in response.xpath(
            "//li[@class='filter-links']/div[@class='filter-name']/a/@href")]

        # if the current chain has 2 elements, a super- and sub-category, then mine the page
        # Yes, this technically requests the same page twice, but it's 3 am and I can't figure out a better solution
        # to this right now.
        if len(parent_chain) == 2 or (len(parent_chain) < 2 and len(sub_categories) == 0):
            yield scrapy.Request(
                url=response.url, callback=self.parse_items,
                dont_filter=True, meta={'category_chain': parent_chain})

        # If the current page corresponds to either level 0 or level 1 in the chain and there are sub-categories
        # then navigate to these and initiate item scraping
        if len(parent_chain) < 2 and len(sub_categories) > 0:
            for cat in sub_categories:
                cat_chain = parent_chain.copy()
                cat_chain.append(cat)
                cat_url = "https://my.iherb.com/c/{}".format(cat)
                yield scrapy.Request(url=cat_url, callback=self.parse, meta={'category_chain': cat_chain})

    def parse_items(self, response):
        items = response.xpath("//div[@class='product-inner product-inner-wide']")
        category = response.meta["category_chain"]
        db_items = []
        for item in items:
            name = item.xpath(".//span[@itemprop='name']/bdi/text()").get()
            url = item.xpath(".//span[@itemprop='name']/parent::a/@href").get()
            price = item.xpath(".//meta[@itemprop='price']/@content").get()
            currency = item.xpath(".//meta[@itemprop='priceCurrency']/@content").get()
            rating = item.xpath(".//meta[@itemprop='ratingValue']/@content").get()
            reviews = item.xpath(".//meta[@itemprop='ratingCount']/@content").get()
            availability = item.xpath(".//link[@itemprop='availability']/@href").get()
            condition = item.xpath(".//link[@itemprop='itemCondition']/@href").get()
            db_items.append((
                name.strip() if name is not None else None,
                url if url is not None else None,
                float(price.strip()) if price is not None else None,
                currency.strip() if currency is not None else None,
                float(rating.strip()) if rating is not None else None,
                int(reviews.strip()) if reviews is not None else None,
                availability.split("/")[-1].strip() if availability is not None else None,
                condition.split("/")[-1].strip() if condition is not None else None,
                ",".join(category)))

        # Store values in an SQL database
        db_name = os.path.join("..", "databases", "items.db")
        con = sqlite3.connect(db_name)
        c = con.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS {} 
                  (name text, url text, price real, currency text, rating real, reviews integer, 
                  availability text, condition text, category text);""".format(self.name))

        c.executemany("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)".format(self.name), db_items)
        self.log("Inserted items from page {} into DB table".format(response.url))
        self.log("Category: {}".format(category))

        con.commit()
        con.close()

        # After saving the items, check if there's a next page (but
        # only if the maximum number of pages has been reached)
        next_link = response.xpath("//a[@class='pagination-next']")
        if next_link:
            url = "https://my.iherb.com" + next_link.xpath(".//@href").get()
            if int(url.split("=")[-1]) <= 25:
                yield scrapy.Request(url=url, callback=self.parse_items, meta={'category_chain': category})
