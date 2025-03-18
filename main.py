import pyodbc
from bs4 import BeautifulSoup
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import re

server = "localhost\SQLEXPRESS"
database = os.getenv("db_name")
username = os.getenv("db_username")
passwordDB = os.getenv("jobDB_password")
conn_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={passwordDB}"
email = os.getenv("email")
password = os.getenv("linkedin_password")
conn = pyodbc.connect(conn_string)
cursor = conn.cursor()

driver = webdriver.Firefox()
driver.get("https://www.linkedin.com/")
action = ActionChains(driver)

def selenium_input(keyword, location):
    login = driver.find_element(By.XPATH, "//a[contains(., 'Sign in')]")
    login.click()
    time.sleep(2)
    user = driver.find_element(By.XPATH, "//input[contains(@id, 'username')]")
    user.send_keys(email)
    log_pass = driver.find_element(By.XPATH, "//input[contains(@id, 'password')]")
    log_pass.send_keys(password)
    signin = driver.find_element(By.XPATH, "//button[contains(., 'Sign in')][contains(@class, 'btn__primary')]")
    signin.click()
    time.sleep(2)
    jobs_tab = driver.find_element(By.XPATH, "//span[contains(@title, 'Jobs')]")
    jobs_tab.click()
    time.sleep(2)
    all_jobs = driver.find_element(By.XPATH, "//h2[contains(., 'Job picks for you')]/following::a[contains(@class, 'jobs-home')][1]")
    all_jobs.click()
    time.sleep(2)
    search = driver.find_element(By.XPATH, "//div[contains(@class, 'relative')]/input[contains(@id, 'jobs-search-box-keyword-id')]")
    search.send_keys(keyword)
    time.sleep(1)
    job_location = driver.find_element(By.XPATH, "//div[contains(@class, 'relative')]/input[contains(@id, 'jobs-search-box-location-id')]")
    job_location.send_keys(location)
    time.sleep(1)
    search.send_keys(Keys.ENTER)
    time.sleep(2)
def linkedin_jobs():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_list = []

    for job in soup.find_all("div", class_=re.compile("entity-lockup__content ember-view")):
        job_title_tag = job.find("div", class_=re.compile("lockup__title ember-view"))
        company_tag = job.find("div", class_=re.compile("lockup__subtitle ember-view"))
        location_tag = job.find("div", class_=re.compile("lockup__caption ember-view"))
        link_tag = job.find("a", class_=re.compile("job-card-container__link"))

        if job_title_tag and company_tag and location_tag and link_tag:
            job_title = job_title_tag.text.strip()
            company = company_tag.text.strip()
            location = location_tag.text.strip()
            link_url = f"https://www.linkedin.com{link_tag['href']}"

            job_list.append((job_title, company, location, link_url))

    return job_list


def insert_into_DB(jobs):
    try:

        for job in jobs:
            cursor.execute("""
                insert into LinkedInJobs(job_title, company, location, link_url)
                values (?, ?, ?, ?)
            """, job)
            conn.commit()
            print("Jobs inserted successfully")
    except Exception as e:
        print(f"An error has occured:{e}")

    finally:
        cursor.close()
        conn.close()

selenium_input("QA Automation", "Cluj-Napoca")
jobs = linkedin_jobs()
if jobs:
    insert_into_DB(jobs)







