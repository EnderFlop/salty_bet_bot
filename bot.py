import os
import math
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

#access https://salty.imaprettykitty.com/live/ and find the win rates for each fighter
#use math to figure out how much to bet
#use selenium to access Salty Bet, get balance, and place a bet on the higher win rate
#profit

load_dotenv()
#Bot Credentials
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
#Personal Credentials (for farming # of bets)
SELF_EMAIL = os.environ.get("SELF_EMAIL")
SELF_PASSWORD = os.environ.get("SELF_PASSWORD")
POVERTY_LIMIT = 2000 #amount of money that, if below, always all in.

email, password = EMAIL, PASSWORD
#email, password = SELF_EMAIL, SELF_PASSWORD

def start_saltybet():
  driver = webdriver.Chrome()
  
  #signin
  driver.get("https://www.saltybet.com/authenticate?signin=1") #saltybet login page
  email_field = driver.find_element(By.XPATH, "//input[@id='email']")
  email_field.send_keys(email)
  pass_field = driver.find_element(By.XPATH, "//input[@id='pword']")
  pass_field.send_keys(password)
  sign_in_button = driver.find_element(By.XPATH, "//input[@value='Sign In']")
  sign_in_button.click()

  loop = 1
  while True:
    driver.implicitly_wait(9999) #wait until the wager field shows up
    wager_field = driver.find_element(By.XPATH, "//input[@style='border-color: rgb(77, 176, 68); display: inline-block;']") #wait for the wager box to show up
    print(f"Running loop number {loop}")

    #get data and decide bet
    one, two = get_data()
    win_percent_difference = abs(one - two)
    #Using the equation 0.01 * x^2 to determine bet number.
    #Plug in the percent difference (0-100)
    #Get back the answer y (0-100). Possible points include (0,0), (5, 0.25), (10, 1), (25, 6.25), (100, 100)
    #bet y% of our current balance on the favored fighter.
    #this system is safe, since it is based on percentage difference. if two %80s go up against eachother, the engine will bet safe. We make our money off of 50% vs 80% type matches.
    balance = int(driver.find_element(By.XPATH, "//span[@class='dollar']").text)
    if balance < POVERTY_LIMIT: #Since the floor is around $200, always go all in until you get out of poverty.
      to_bet = balance
    else:
      percentage_bet = 0.01 * (win_percent_difference ** 2)
      #multiply the balance by the percentage (scaled by 0.01 for math). Get the floor to remove the decimal. Add 1 to always bet at least 1.
      to_bet = math.floor(balance * (percentage_bet / 100)) + 1
    print(f"Odds Are {one}% vs {two}%. Engine gives {percentage_bet}% of balance to bet. Current balance is {balance}. To Bet: {to_bet}")

    #bet
    wager_field.send_keys(to_bet)
    if one > two:
      one_button = driver.find_element(By.XPATH, "//input[@name='player1']")
      one_button.click()
    else:
      two_button = driver.find_element(By.XPATH, "//input[@name='player2']")
      two_button.click()
    #driver waits until it find the disabled wager button, then it loops and waits for the wager to reopen.
    driver.implicitly_wait(9999)
    disabled_wager = driver.find_element(By.XPATH, "//input[@style='border-color: black; display: none;']")
    loop += 1

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

#TODO
#Add linux support (needs different webdriver/way to add to PATH. Maybe a different file, maybe a way to detect os and change driver accordingly? I dont know how linux PATH works)
#Add Tournament support. It should go all in on tournaments regularly. This is as simple as detecting when a tournament is happening and raising POVERTY_LIMIT
#Add logging. Detect wins and losses after they happen (based on balance changes), record balance and how it changes. Can be done in a txt
#Start own database? This is ideal, but would take forever. It would remove an external liability, but that outside database has hundreds of data points on each fighter.
# We would be blind for a very long time as it gets to a fraction of the data it has. I wonder if I can email the admins for access to the DB directly?
