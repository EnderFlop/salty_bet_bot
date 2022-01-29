import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

#request https://salty.imaprettykitty.com/live/ and find the win rates for each fighter.
#use selenium to access Salty Bet and place a bet on the higher win rate
#use math to figure out optimal bets and figure out how to get balance.
#profit

load_dotenv()
USERNAME = os.environ.get("USERNAME")
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

def start_saltybet():
  driver = webdriver.Chrome()
  
  #signin
  driver.get("https://www.saltybet.com/authenticate?signin=1") #saltybet login page
  email_field = driver.find_element(By.XPATH, "//input[@id='email']")
  email_field.send_keys(EMAIL)
  pass_field = driver.find_element(By.XPATH, "//input[@id='pword']")
  pass_field.send_keys(PASSWORD)
  sign_in_button = driver.find_element(By.XPATH, "//input[@value='Sign In']")
  sign_in_button.click()

  for i in range(3):
    print(f"Running loop number {i}")
    driver.implicitly_wait(9999) #wait until the wager field shows up
    wager_field = driver.find_element(By.XPATH, "//input[@style='border-color: rgb(77, 176, 68); display: inline-block;']") #wait for the wager box to show up
    wager_field.send_keys("1")
    one, two = get_data()
    if one > two:
      one_button = driver.find_element(By.XPATH, "//input[@name='player1']")
      one_button.click()
    else:
      two_button = driver.find_element(By.XPATH, "//input[@name='player2']")
      two_button.click()
    #driver waits until it find the disabled wager button, then it loops and waits for the wager to reopen.
    driver.implicitly_wait(9999)
    disabled_wager = driver.find_element(By.XPATH, "//input[@style='border-color: black; display: none;']")

def get_data():
  data_driver = webdriver.Chrome()
  data_driver.get("https://salty.imaprettykitty.com/live/")
  data_driver.implicitly_wait(9999) #always wait until site loads
  winrates = data_driver.find_elements(By.XPATH, "//table[@style='margin-top: -16px; margin-bottom: 0px;']/tbody/tr[3]/td[2]")
  fighter_one = int(winrates[0].text[0:2])
  fighter_two = int(winrates[1].text[0:2])
  print(fighter_one, fighter_two)
  # know im navigating a tightrope geting these data points, but I dont think this site is changing anytime soon. very simple html.
  data_driver.close()
  return fighter_one, fighter_two

if __name__ == "__main__":
  start_saltybet()