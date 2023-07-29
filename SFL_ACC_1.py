from datetime import datetime
from glob import glob
from math import sqrt
import random
import sys
import traceback
import undetected_chromedriver as webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

#Done
def report_exception(e):
    print("\n\n\nStart:")
    print(str(e))
    print(traceback.print_exc())
    print("End.\n\n\n")

#Done
def take_browser_screenshot():
    print("Taking Screenshot.\t" + time.asctime())
    global browser
    try:
        for i in range(10):
            try:
                browser.save_screenshot(".\\ScreenShots\\" + "Profile_1_" + str(time.time()) + ".png")
                break
            except:
                if i == 9:
                    raise Exception()
                time.sleep(5)
                continue
    except Exception as e:
        print("\n\n\nCrashed while taking a screenshot.\n")
        report_exception(e)
        while True:
            print("Waiting here to keep chrome open.")
            time.sleep(1000)

#Done
def close_open_dialogs():
    global close_open_dialogs_loop
    if close_open_dialogs_loop == 100:
        close_open_dialogs_loop -= 1
        raise Exception("More than 100 open dialog loops!!!")
    opened_dialog = browser.find_elements(By.XPATH, "//div[@role='dialog']")
    if len(opened_dialog) != 0:
        close_open_dialogs_loop += 1
        for x in opened_dialog:
            try:
                x.send_keys(Keys.ESCAPE)
                time.sleep(humanize_float(1.5, 0.3))
            except Exception as e:
                print("\n\n\nCrashed while sending Keys.ESCAPE!!!")
                report_exception(e)
                print("\n\n\n")
                take_browser_screenshot()
        close_open_dialogs()
        close_open_dialogs_loop -= 1

#Done
def humanize_float(weight: float, jitter: float) -> float:
    if jitter == 0.0:
        jitter = weight * 0.3
    normalized_jitter = random.uniform(-1 * sqrt(jitter), sqrt(jitter))
    return weight + normalized_jitter * abs(normalized_jitter)

#Done
def wait_for_dialog_popup_with_delay() -> bool:
    try:
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
    except:
        #can just not use try and throw TimeoutException here
        return False
    time.sleep(humanize_float(0.6, 0.2))
    return True
    
#Done
def wait_for_farms_to_load() -> bool:
    try:
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, farm_stack1_xpath)))
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, farm_stack2_xpath)))
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, farm_stack3_xpath)))
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, farm_stack4_xpath)))
    except:
        #can just not use try and throw TimeoutException here
        return False
    time.sleep(humanize_float(0.6, 0.2))
    return True

#Done #Change the need to sync to buy button disabled and not hardcoded
def buy_seeds() -> bool:
    #return false if all seeds are bought !!!!!!!!!!!!!!!!!!!!!!!
    #lets not close dialogs to reduce network traffic
    #close_open_dialogs()
    #time.sleep(humanize_float(0.4, 0.2))
    #browser.find_element(By.XPATH, shop_xpath).click()
    
    
    browser.find_element(By.XPATH, shop_buy_menu_button_xpath).click()
    time.sleep(humanize_float(0.4, 0.2))


    if not wait_for_dialog_popup_with_delay():
        raise TimeoutException
    
    no_seeds_left = True
    for i in range(unlocked_seeds):
        if len(plant_only) != 0:
            if not seed_orders[i] in plant_only:
                continue
        #try:
        x_10 = int(0)
        browser.find_element(By.XPATH, shop_seed_buy_xpaths[i]).click()
        buy_amount = int(seed_amounts[i] / 10)
        #remove for and use while true
        for j in range(buy_amount):
            buy_10 = browser.find_elements(By.XPATH, shop_buy10_button_xpath)
            if len(buy_10) == 0:
                break
            no_seeds_left = False
            time.sleep(humanize_float(0.15, 0.05))
            if buy_10[0].is_enabled():
                buy_10[0].click()
                seed_amounts[i] -= 10
                x_10 += 1
            else: #Buy button is disabled and stock is not emptied = no money = no need to check rest. Just return.
                ##uncomment return to revert to seperate buy / sell
                ##return True
                break

        #except:
        #    pass
        time.sleep(humanize_float(0.6, 0.2))
        if not no_seeds_left:
            ##kinda redundant remove this whole part if want to buy more than 1 seed at a time. but opens the inventory alot to change the seed so it sux.
            global selected_seed_name
            global selected_seed_amount
            selected_seed_name = seed_orders[i]
            selected_seed_amount = x_10* 10
            ##kinda redundant remove this whole part if want to buy more than 1 seed at a time. but opens the inventory alot to change the seed so it sux.
            print("Bought")
            return True
    if no_seeds_left:
        return False
    time.sleep(humanize_float(1.0, 0.4))
    print("Bought")
    return True

#Done
def sell_seeds():
    close_open_dialogs()
    time.sleep(humanize_float(0.7, 0.2))
    browser.find_element(By.XPATH, shop_xpath).click()

    if not wait_for_dialog_popup_with_delay():
        raise TimeoutException
    browser.find_element(By.XPATH, shop_sell_menu_button_xpath).click()

    for i in range(unlocked_seeds):
        #Skip non-sell seeds.
        
        if seed_orders[i] in dont_sell_list:
            continue
        
        #Skip selling if have none of current seed.
        if len(browser.find_elements(By.XPATH, shop_seed_sell_xpaths[i] + "/div")) == 0:
            continue
        
        time.sleep(humanize_float(0.6, 0.2))
        #try:
        browser.find_element(By.XPATH, shop_seed_sell_xpaths[i]).click()
        time.sleep(humanize_float(0.5, 0.1))
        
        if browser.find_element(By.XPATH, (shop_seed_sell_xpaths[i] + "/div")).text == "1":
            browser.find_element(By.XPATH, shop_sell_1_button_xpath).click()
            continue
        
        browser.find_element(By.XPATH, shop_sell_all_button_xpath).click()
        time.sleep(humanize_float(0.9, 0.2))
        browser.find_element(By.XPATH, shop_sell_all_confirm_button_xpath).click()
                
        #except:
        #    pass
    print("Sold")
    time.sleep(humanize_float(1.0, 0.4))

#Done
def select_seed() -> bool:
    #return false if all seeds are bought !!!!!!!!!!!!!!!!!!!!!!!

    close_open_dialogs()
    time.sleep(humanize_float(2.0, 0.5))
    browser.find_element(By.XPATH, inventory_button_xpath).click()
    
    if not wait_for_dialog_popup_with_delay():
        raise TimeoutException

    have_inventory_crops = len(browser.find_elements(By.XPATH, inventory_no_crops_text_xpath)) == 0
    have_no_seeds_left = len(browser.find_elements(By.XPATH, inventory_no_seeds_text_xpath)) != 0
    #closed_seed_selection = False

    if have_no_seeds_left:
        if have_inventory_crops:
            sell_seeds()
            #closed_seed_selection = True
            #if not buy_seeds():
            #    return False
        if not buy_seeds():
            return False
    else:
        global selected_seed_name
        global selected_seed_amount
        if len(plant_only) != 0:
            for i in range(len(browser.find_elements(By.XPATH, inventory_seeds))):
                browser.find_element(By.XPATH, inventory_seeds + "[" + str(i + 1) + "]/div[1]").click()
                time.sleep(1)
                selected_seed_name = browser.find_element(By.XPATH, inventory_seed_text_xpath).text.split(" ")[0]
                print("Seed Name: " + selected_seed_name)
                if not selected_seed_name in plant_only:
                    print("Skipped Seed.")
                    continue
                selected_seed_amount = int(browser.find_element(By.XPATH, inventory_seeds + "[" + str(i + 1) + "]/div[1]/div").text)
                close_open_dialogs()
                return True
            sell_seeds()
            if not buy_seeds():
                close_open_dialogs()
                return False
            close_open_dialogs()
            return True
        browser.find_element(By.XPATH, inventory_fist_seed_location_xpath).click()
        time.sleep(1)
        selected_seed_name = browser.find_element(By.XPATH, inventory_seed_text_xpath).text.split(" ")[0]
        selected_seed_amount = int(browser.find_element(By.XPATH, inventory_first_seed_number_box_xpath).text)
    #if closed_seed_selection:
    #    return select_seed()

    #need to do else right here cuz what if i buy seeds but actually didnt buy any need to check func #ig fixed in buy func but idk
    ##Select first seed ##kinda redundant since im now buying 1 type of seed per buy
    ##close_open_dialogs()
    ##time.sleep(humanize_float(1.0, 0.5))
    ##browser.find_element(By.XPATH, inventory_button_xpath).click()
    
    ##if not wait_for_dialog_popup_with_delay():
        ##raise TimeoutException

    ##time.sleep(humanize_float(0.4, 0.2))
    ##browser.find_element(By.XPATH, invertory_fist_seed_location_xpath).click()                        
    ##time.sleep(humanize_float(0.4, 0.2))
    ##global selected_seed_name
    ##global selected_seed_amount
    ##selected_seed_name = browser.find_element(By.XPATH, inventory_seed_text_xpath).text.split(" ")[0]
    ##selected_seed_amount = int(browser.find_element(By.XPATH, inventory_first_seed_number_box_xpath).text)
    close_open_dialogs()
    return True


farm_stack1_xpath = "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]"
farm_stack2_xpath = "//div[@id='cropzone-two']"
farm_stack3_xpath = "//div[@id='cropzone-three']"
farm_stack4_xpath = "//div[@id='cropzone-four']"
goblin1_xpath = "//img[@class='absolute z-10 hover:img-highlight cursor-pointer']"
goblin2_xpath = "//img[@class='absolute z-20 hover:img-highlight cursor-pointer']"
goblin3_xpath = "//img[@class='absolute z-20 hover:img-highlight cursor-pointer -scale-x-100']"
inventory_button_xpath = "//div[@class='w-16 h-16 sm:mx-8 mt-2 relative flex justify-center items-center shadow rounded-full cursor-pointer']"
inventory_seed_text_xpath = "//span[@class='text-center text-shadow']"
#inventory_first_seed_number_box_xpath = "//div[contains(@class,'overflow-y-auto scrollable')]/div[1]/div[1]/div[1]/div[1]/div[1]"
inventory_first_seed_number_box_xpath = "/html/body/div[@role='dialog']/div/div/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div"
inventory_seeds = "//body/div[@role='dialog']/div[@class='modal-dialog modal-dialog-centered modal-dialog-scrollable']/div[@class='modal-content']/div[@class='bg-brown-600 p-0.5 text-white shadow-lg pt-5 relative']/div[@class='bg-brown-300 p-1']/div[@class='flex flex-col']/div[2]/div[1]/div[1]/div"
inventory_no_seeds_text_xpath = "//p[normalize-space()='No Seeds in inventory']"
inventory_no_crops_text_xpath = "//p[normalize-space()='No Crops in inventory']"
inventory_fist_seed_location_xpath = "//body/div[@role='dialog']/div[@class='modal-dialog modal-dialog-centered modal-dialog-scrollable']/div[@class='modal-content']/div[@class='bg-brown-600 p-0.5 text-white shadow-lg pt-5 relative']/div[@class='bg-brown-300 p-1']/div[@class='flex flex-col']/div[2]/div[1]/div[1]/div[1]/div[1]"
shop_xpath = "//div[@id='shop']"

shop_seed_buy_xpaths = ["//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[1]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[2]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[3]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[4]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[5]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[6]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[7]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[8]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[9]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[10]/div" ]

shop_seed_sell_xpaths = ["//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[1]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[2]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[3]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[4]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[5]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[6]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[7]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[8]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[9]/div", 
                        "//div[contains(@class,'w-3/5 flex flex-wrap h-fit')]/div[10]/div" ]

farm_1_soil_list_xpath = ["//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[1]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[1]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[2]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[3]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[3]/div[2]/img[2]" ]

farm_2_soil_list_xpath = ["//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[1]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[1]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[2]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[3]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[3]/div[2]/img[2]" ]

farm_3_soil_list_xpath = ["//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[3]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[3]/img[2]" ]

farm_4_soil_list_xpath = ["//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[3]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[1]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[2]/img[2]", 
                          "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[3]/img[2]" ]

all_soils_list_xpath = ["//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[1]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[1]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[2]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[3]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[1]/div[3]/div[2]/img[2]", 
					    "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[1]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[1]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[2]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[3]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[2]/div[3]/div[2]/img[2]", 
					    "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[1]/div[3]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[3]/div[2]/div[3]/img[2]", 
					    "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[1]/div[3]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[1]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[2]/img[2]", 
                        "//div[@class='relative h-gameboard w-gameboard']/div[@class='absolute'][2]/div[4]/div[2]/div[3]/img[2]" ]

seed_orders = ["Sunflower", "Potato", "Pumpkin", "Carrot", "Cabbage", "Beetroot", "Cauliflower", "Parsnip", "Radish", "Wheat"]
seed_amounts = [400, 200, 100, 100, 90, 80, 80, 40, 40, 40]
seed_grow_time = [1 * 60, 5 * 60, 30 * 60, 60 * 60, 2 * 60 * 60, 4 * 60 * 60, 8 * 60 * 60, 12 * 60 * 60, 24 * 60 * 60, 24 * 60 * 60]
modified_seed_amounts = [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000]
shop_buy_menu_button_xpath = "//div[contains(@class,'flex justify-between absolute top-1.5 left-0.5 right-0 items-center')]/div/div[1]"
shop_sell_menu_button_xpath = "//div[contains(@class,'flex justify-between absolute top-1.5 left-0.5 right-0 items-center')]/div/div[2]"
shop_buy1_button_xpath = "//button[normalize-space()='Buy 1']"
shop_buy10_button_xpath = "//button[normalize-space()='Buy 10']"
shop_sell_1_button_xpath = "//button[normalize-space()='Sell 1']"
shop_sell_all_button_xpath = "//button[normalize-space()='Sell All']" ## check if buttons are disabled or not
shop_sell_all_confirm_button_xpath = "//button[normalize-space()='Yes']"
close_open_dialogs_loop = int(0)

browser = ""
#try:
try:
    if __name__ == '__main__':
        browser_options = webdriver.ChromeOptions()
        browser_options.user_data_dir = "c:\\temp\\profile1"
        browser_options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        browser_options.add_argument("--start-maximized")
        browser = webdriver.Chrome(options = browser_options, suppress_welcome=True, driver_executable_path="C:\\Users\\barisWin\\AppData\\Roaming\\undetected_chromedriver\\8a43ee1681a286a0_chromedriver_1.exe")
        time.sleep(15)
        browser.get('https://sunflower-land.com/play/')
        #browser.get("http://192.168.1.135:3000")
        time.sleep(60) #Wait for user to log in here on normal site!!!!!!!!!!!!!!!!

        #seed_grow_time = [x / 120 for x in seed_grow_time]
        selected_seed_amount = int(0)
        selected_seed_name = str("")
        is_soil_full = [0] * 22
        dont_sell_list = ["Carrot", "Cauliflower", "Beetroot", "Radish"]
        plant_only = ["Sunflower", "Potato", "Pumpkin", "Carrot"]
        list_shuffler = list(range(22))

        while True:
            #try:
            unlocked_seeds = int(3)
            unlocked_soil_count = int(5)
            wait_for_farms_to_load()
            close_open_dialogs()
            time.sleep(humanize_float(1.0, 0.3))
            #try:
            #randomize soils
            if not random.randint(0,2):
                list_shuffler[0:5] = random.sample(list_shuffler[0:5], 5)
                list_shuffler[5:10] = random.sample(list_shuffler[5:10], 5)
                list_shuffler[10:16] = random.sample(list_shuffler[10:16], 6)
                list_shuffler[16:] = random.sample(list_shuffler[16:], 6)
                all_soils_list_xpath = [all_soils_list_xpath[i] for i in list_shuffler]
                is_soil_full = [is_soil_full[i] for i in list_shuffler]

            if len(browser.find_elements(By.XPATH, goblin1_xpath)) == 0:
                unlocked_seeds += 2
                unlocked_soil_count += 5
                if len(browser.find_elements(By.XPATH, goblin2_xpath)) == 0:
                    unlocked_seeds += 2
                    unlocked_soil_count += 6
                    if len(browser.find_elements(By.XPATH, goblin3_xpath)) == 0:
                        unlocked_seeds += 2
                        unlocked_soil_count += 6
            #except:
            #    time.sleep(1)
            #    close_open_dialogs()
            #    time.sleep(1)
            #    continue
            print("\n\t\t\t" + time.asctime(time.gmtime()) + "\n")
            if selected_seed_amount == 0:
                if not select_seed():
                    while True:
                        print("No Seeds Left!!! Need to sync.")
                        time.sleep(10)
            else:
                try:
                    selected_seed_amount = int(browser.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[3]/div[2]/div[1]/div[1]/div[2]").text)
                except:
                    pass

            print("Planting: " + selected_seed_name + "Seed Count: " + str(selected_seed_amount))
            #Plant
            time.sleep(humanize_float(0.25, 0.02))
            for i in range(unlocked_soil_count):
                if selected_seed_amount == 0:
                    break
                if is_soil_full[i] == 1:
                    print("SOIL FULL")
                    continue
                current_soil = browser.find_elements(By.XPATH, all_soils_list_xpath[i])
                if len(current_soil) != 0:
                    current_soil[0].click()
                    time.sleep(humanize_float(0.25, 0.02))
                    if len(browser.find_elements(By.XPATH, all_soils_list_xpath[i][:-7] + "/img")) == 2:
                        time.sleep(humanize_float(1, 0.2))
                        j = int(0)
                        while len(browser.find_elements(By.XPATH, all_soils_list_xpath[i][:-7] + "/img")) == 2:
                            current_soil[0].click()
                            time.sleep(humanize_float(1, 0.2))
                            print("LOOP 1")
                            j += 1
                            print("Xpath: " + all_soils_list_xpath[i] + "Loop i: " + str(i) + "Loop 1 Counter: " + str(j))
                    is_soil_full[i] = 1
                    selected_seed_amount -= 1

            if int(sum(is_soil_full)) * 2 < unlocked_soil_count:
                continue
            time_sleep = abs(humanize_float(0.2 * (seed_grow_time[seed_orders.index(selected_seed_name)] ** 0.78), 0))
            print("Waiting " + str(2.5 + seed_grow_time[seed_orders.index(selected_seed_name)] + time_sleep) + " seconds.")
            time.sleep(humanize_float(2.5, 0.5))
            time.sleep(seed_grow_time[seed_orders.index(selected_seed_name)])
            time.sleep(time_sleep)

            #randomize soils
            if not random.randint(0,2):
                list_shuffler[0:5] = random.sample(list_shuffler[0:5], 5)
                list_shuffler[5:10] = random.sample(list_shuffler[5:10], 5)
                list_shuffler[10:16] = random.sample(list_shuffler[10:16], 6)
                list_shuffler[16:] = random.sample(list_shuffler[16:], 6)
                all_soils_list_xpath = [all_soils_list_xpath[i] for i in list_shuffler]
                is_soil_full = [is_soil_full[i] for i in list_shuffler]

            #Collect crops and handle anti bot chests.
            for i in range(unlocked_soil_count):
                print("Here ")
                if is_soil_full[i] == 1:
                    #################
                    print("Was full")
                    time.sleep(humanize_float(0.25, 0.015))
                    if len(browser.find_elements(By.XPATH, all_soils_list_xpath[i][:-7] + "/img")) == 2:
                        browser.find_element(By.XPATH, all_soils_list_xpath[i]).click() 
                        time.sleep(humanize_float(0.2, 0.05))
                        ##ANTI BOT!
                        print("1 " + str(i))
                        if len(browser.find_elements(By.XPATH, all_soils_list_xpath[i][:-7] + "/img[@id]")) != 0:
                            browser.find_element(By.XPATH, all_soils_list_xpath[i]).click()
                            wait_for_dialog_popup_with_delay() #wait like 0.3 secs for a dialog and if it comes that means its a chest plant
                                                                # do it for like 3-5 secs if not its a misclick reloop this whole collect part
                            time.sleep(humanize_float(1, 0.2))

                            opened_dialog_chest = list[WebElement]
                            for j in range(10):
                                opened_dialog_chest = browser.find_elements(By.XPATH, "//div[@role='dialog']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/img[2]")
                                if len(opened_dialog_chest) != 0:
                                    break
                                print("LOOP 2")
                                time.sleep(1)
                            time.sleep(6)
                            if len(opened_dialog_chest) != 0:
                                time.sleep(humanize_float(0.3, 0.1))
                                opened_dialog_chest[0].click()
                                time.sleep(humanize_float(0.3, 0.1))
                                try:
                                    WebDriverWait(browser, 5).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[normalize-space()='Close']")))
                                except:
                                    pass
                                opened_dialog_close_button = browser.find_elements(By.XPATH, "//button[normalize-space()='Close']")
                                if len(opened_dialog_close_button) != 0:
                                    opened_dialog_close_button[0].click()
                                    time.sleep(humanize_float(0.4, 0.1))
                                    print("Closed Chest " + str(i))

                        #Collect crops and handle anti bot chests.
                        print("2 " + str(i))
                        print("SOIL EMPTIED")
                        is_soil_full[i] = 0
                        continue
            print("Have " + str(selected_seed_amount) + " seeds left")
except Exception as e:
    print("\n\n\nGone " + time.asctime())
    report_exception(e)
    take_browser_screenshot()
    print("Something crashed. Took screenshot. Exiting...")
    sys.exit()