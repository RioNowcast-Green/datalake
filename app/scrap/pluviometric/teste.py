from app.config.selenium_config import SeleniumConfig

def teste():
    selenium_cfg = SeleniumConfig(headless=False)
    
    driver = selenium_cfg.create_driver()


    driver.get("https://www.google.com")
    # driver.quit()