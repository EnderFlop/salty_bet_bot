import os
import math
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

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

#Betting Mode
MODE = 4
#1. Advanced Betting, 0.01x^2
#2. Simple Betting, C%
#3. Risky Buisness, 1%:1%. linear
#4. Airdog Simulator, bet 5% on the loser in an unbalanced matchup.
UNDERDOG_BETTING_MODES = [4]

chrome_options = Options()
chrome_options.add_argument("headless") #Runs Chrome without opening windows
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) #disables DevTools listening messages
chrome_options.add_argument("--log-level=3") #mutes non-essential logging from chrome

logging.basicConfig(filename="operation.log", format="%(asctime)s %(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

email, password = EMAIL, PASSWORD
#email, password = SELF_EMAIL, SELF_PASSWORD

def start_saltybet():
  driver = webdriver.Chrome(options=chrome_options)
  
  #signin
  driver.get("https://www.saltybet.com/authenticate?signin=1") #saltybet login page
  email_field = driver.find_element(By.XPATH, "//input[@id='email']")
  email_field.send_keys(email)
  pass_field = driver.find_element(By.XPATH, "//input[@id='pword']")
  pass_field.send_keys(password)
  sign_in_button = driver.find_element(By.XPATH, "//input[@value='Sign In']")
  sign_in_button.click()
  logger.info("SIGN IN COMPLETE")

  driver.implicitly_wait(9999) #wait for page to load and find balance.
  balance = int(driver.find_element(By.XPATH, "//span[@class='dollar'] | //span[@class='dollar purpletext']").text.replace(",", ""))
  logger.info(f"STARTING BALANCE: {balance}")
  logger.info(f"BETTING MODE: {MODE}")

  loop = 0
  while True:
    driver.implicitly_wait(9999) #wait until the wager field shows up
    wager_field = driver.find_element(By.XPATH, "//input[@style='border-color: rgb(77, 176, 68); display: inline-block;']") #wait for the wager box to show up/fight to be over

    driver.implicitly_wait(9999) #wait to get new balance
    past_balance = balance
    balance = int(driver.find_element(By.XPATH, "//span[@class='dollar'] | //span[@class='dollar purpletext']").text.replace(",", ""))
    if balance > past_balance:
      logger.info(f"{loop}. WON! Made ${balance - past_balance}")
    elif balance < past_balance:
      logger.info(f"{loop}. LOST... Lost ${past_balance - balance}")

    #START OF BETTING LOOP

    loop += 1
    logger.info(f"{loop}. Fight Number {loop}")

    #get data and decide bet
    one, two = get_data()
    win_percent_difference = abs(one - two)
    #Using the equation 0.01 * x^2 to determine bet number.
    #Plug in the percent difference (0-100)
    #Get back the answer y (0-100). Possible points include (0,0), (5, 0.25), (10, 1), (25, 6.25), (100, 100)
    #bet y% of our current balance on the favored fighter.
    #this system is safe, since it is based on percentage difference. if two %80s go up against eachother, the engine will bet safe. We make our money off of 50% vs 80% type matches.


    try:
      driver.implicitly_wait(1)
      tournament = driver.find_element(By.XPATH, "//span[@id='tournament-note']") #If the tag exists, we are in a tournament
      POVERTY_LIMIT = 3000
    except NoSuchElementException:
      POVERTY_LIMIT = 500

    if balance < POVERTY_LIMIT: #Since the floor is around $200, always go all in until you get out of poverty.
      to_bet = balance
      logger.info(f"{loop}. Odds are {one}% vs {two}%. Current balance is ${balance}. BELOW POVERTY LIMIT! To Bet: ${to_bet}")
    else:

      if MODE == 1: #ADVANCED BETTING (use the 0.01x^2 formula)
        percentage_bet = 0.01 * (win_percent_difference ** 2)
      elif MODE == 2: #SIMPLE BETTING (always bet 4%)
        percentage_bet = 4
      elif MODE == 3: #RISKY BUISNESS (go big or go home, bet 1:1 percent_difference:percent_of_balance)
        percentage_bet = win_percent_difference
      elif MODE == 4: #AIRBALL SIMULATOR (go for the underdog, bet on less likely fighter if winrates are far apart)
        if win_percent_difference >= 25: #If the fighers are 25% away (75v50, 30v55)
          percentage_bet = 5 #5% bet
        else:
          percentage_bet = 0 #just bet 1 dollarydoo (0%)


      #multiply the balance by the percentage (scaled by 0.01 for math). Get the floor to remove the decimal. Add 1 to always bet at least 1.
      to_bet = math.floor(balance * (percentage_bet / 100)) + 1

      logger.info(f"{loop}. Winrates are {one}% vs {two}%. Engine gives {percentage_bet}% of balance to bet. Current balance is ${balance}. To Bet: ${to_bet}")

    #bet
    wager_field.clear()
    wager_field.send_keys(to_bet)

    if MODE not in UNDERDOG_BETTING_MODES: #overdog betting, list is all underdog betting modes
      if one > two:
        one_button = driver.find_element(By.XPATH, "//input[@name='player1']")
        one_button.click()
      else:
        two_button = driver.find_element(By.XPATH, "//input[@name='player2']")
        two_button.click()
    else:
      if one <= two:
        one_button = driver.find_element(By.XPATH, "//input[@name='player1']")
        one_button.click()
      else:
        two_button = driver.find_element(By.XPATH, "//input[@name='player2']")
        two_button.click()

    #driver waits until it find the disabled wager button, then it loops and waits for the wager to reopen.
    driver.implicitly_wait(9999)
    disabled_wager = driver.find_element(By.XPATH, "//input[@style='border-color: black; display: none;']")
    time.sleep(5) #can't use implicit wait because they already exist, just have to wait after wager closes for it to update.
    try:
      to_gain = driver.find_elements(By.XPATH, "//span[@id='lastbet']/span")[1].text #uglier than assigning to list then multiple assignment, but I kept getting StaleElementReferenceExceptions
      odds_1 = driver.find_elements(By.XPATH, "//span[@id='lastbet']/span")[2].text
      odds_2 = driver.find_elements(By.XPATH, "//span[@id='lastbet']/span")[3].text
    except IndexError:
      pass

    if MODE not in UNDERDOG_BETTING_MODES:
      if one > two: #add some flair to the chosen fighter's odds.
        odds_1 = f"*{odds_1}*"
      else:
        odds_2 = f"*{odds_2}*"
    else:
      if one <= two:
        odds_1 = f"*{odds_1}*"
      else:
        odds_2 = f"*{odds_2}*"
    logger.info(f"{loop}. Odds are {odds_1}:{odds_2}. ${to_bet} -> {to_gain} potential")

def get_data():
  data_driver = webdriver.Chrome(options=chrome_options)
  data_driver.get("https://salty.imaprettykitty.com/live/")
  data_driver.implicitly_wait(9999) #always wait until site loads
  winrates = data_driver.find_elements(By.XPATH, "//table[@style='margin-top: -16px; margin-bottom: 0px;']/tbody/tr[3]/td[2]")
  fighter_one = int(winrates[0].text.replace("%", ""))
  fighter_two = int(winrates[1].text.replace("%", ""))
  # know im navigating a tightrope geting these data points, but I dont think this site is changing anytime soon. very simple html.
  data_driver.close()
  return fighter_one, fighter_two

if __name__ == "__main__":
  start_saltybet()

#TODO
#Add linux support (needs different webdriver/way to add to PATH. Maybe a different file, maybe a way to detect os and change driver accordingly? I dont know how linux PATH works)
#Add Tournament support. It should go all in on tournaments regularly. This is as simple as detecting when a tournament is happening and raising POVERTY_LIMIT ✅
#Add logging. Detect wins and losses after they happen (based on balance changes), record balance and how it changes. Can be done in a txt ✅
#Start own database? This is ideal, but would take forever. It would remove an external liability, but that outside database has hundreds of data points on each fighter.
# We would be blind for a very long time as it gets to a fraction of the data it has. I wonder if I can email the admins for access to the DB directly?
#Make MagicMirror Module that displays total balance and change over past day
#Do something about team fights (exhibitions). Right now it uses the last solo fight odds when betting. Could check if the odds are the same and skip. Or just let it ride.
#Memory Leak on Chrome Tabs not actually closing in get_data()