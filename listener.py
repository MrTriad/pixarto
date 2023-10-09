from selenium import webdriver
from selenium.webdriver.common.by import By
from style import style
import time
import os
from telethon.sync import TelegramClient
import asyncio
from dotenv import load_dotenv
from selenium.webdriver.firefox.options import Options

options = Options()


pixart_home_url = "http://127.0.0.1/pixart/"
pixart_home_happy_hour_button_css_selector = "div.banner-top div.banner-top-strip div.slider-button.btn.blue-btn.big-btn"

pixart_hhpage_deals_css_selector = "div.col-6.col-sm-3.gallery_item.promo_hour_btn"

pixart_deal_name_css_selector = ".gallery_item_name"
pixart_deal_price_css_selector = ".gallery_discount"
pixart_deal_image_css_selector = ".img-fluid.ls-is-cached.lazyloaded"
pixart_deal_sold_out_css_selector = ".sold_out_label"

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


async def check_page(driver):   # Estrai juicy info
    deals = driver.find_elements(By.CSS_SELECTOR, pixart_hhpage_deals_css_selector)

    parsed_deals= []

    for deal in deals:
        try:
            name = deal.find_element(By.CSS_SELECTOR, pixart_deal_name_css_selector).text.strip()
            price = deal.find_element(By.CSS_SELECTOR, pixart_deal_price_css_selector).text.strip()
            
            sold_out = deal.find_elements(By.CSS_SELECTOR, pixart_deal_sold_out_css_selector)
            if(len(sold_out) == 0): sold_out = False
            else: sold_out = True

            deal_url = ''
            if not sold_out:
                deal_url = deal.find_element(By.TAG_NAME, "a").get_attribute("href")

            if(name and not price.endswith('%')):
                parsed_deals.append({
                    "name": name,
                    "price": price,
                    "sold_out": sold_out,
                    "deal_url": deal_url
                })
        except Exception as e:
            print(style.error("Exception caught while parsing the scraped item: ") + e)
    
    print(parsed_deals)
    print(len(parsed_deals))

    

    # Initialize the message
    text = "The happy hour has started. Here are the juicy dealz:\n\n"

    # Iterate through the deals and format them
    parsed_deals.sort(key=lambda x: x['sold_out'], reverse=True)

    for deal in parsed_deals:
        title = f"[{deal['name']}]({deal['deal_url']})"
        price = f"{deal['price']}"
        
        if deal['sold_out']:
            title = f"~~{deal['name']}~~ SOLD OUT"
            price = f"~~{price}~~"
        
        text += f"- {title}\n   {price}\n"

    # Print or use the formatted message
    print(text)
    await bot.send_message('elpixartoprinto', message=text)

async def main():
    # Creazione driver
    options.add_argument("--headless=new")
    driver = webdriver.Firefox(options=options)

    if await scrape(driver):    #Questa parte è lo schifo tenporaneo da sostituire con un cronjob
        for i in range(120):
            time.sleep(30)
            await check_page(driver)
    else:
        print(style.info("No funny hour yet ;w;"))
        time.sleep(30)
        if not await scrape(driver):
            print(style.info("No funny hour yet ;w;"))
    #driver.close()


async def scrape(driver):   #Check home 
    
    driver.get(pixart_home_url)
    driver.refresh()

    try:
        button = driver.find_elements(By.CSS_SELECTOR, pixart_home_happy_hour_button_css_selector)
        if(len(button) == 0):
            return False    # No funny yet
        else:
            button.pop().click()
            print(style.success("Wow, happy hour has started!"))

            await check_page(driver)

            return True
    except Exception as e:
        print(style.error("Exception caught while parsing the site: ") + str(e))
        return False






if __name__ == "__main__":
	asyncio.get_event_loop().run_until_complete(main())