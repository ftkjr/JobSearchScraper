###############################
# Import Packages 
import csv
from datetime import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
####

##################################
# Define functions
def get_job_results(url: str, info_id: str) -> list:
    """Return page results from job site"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id=info_id) 
    return results

# def collect_individual_search_info(site: str, individual_searches: list, total_results_frame, unique_results_frame, search_times: list, total_search_time: float, notes:str = None):
#     """Return individual search info as one DataFrame"""
#     # Create framework for the individual search data. 
#     individual_searches_frame = pd.DataFrame(individual_searches, columns=['search_location', 'search_title'])
#     individual_searches_frame['SearchTimes'] = search_times
#     individual_searches_frame['Site'] = site
#     individual_searches_frame['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Collect the counts for the results before removing duplicates.
#     total_results = total_results_frame[['search_title', 'search_location', 'description']].groupby(['search_title', 'search_location'], as_index=False).count()

#     # Collect the counts for the results after removing duplicates.
#     unique_results = unique_results_frame[['search_title', 'search_location', 'description']].groupby(['search_title', 'search_location'], as_index=False).count()

#     # Add the Total Results count to the individual searches frame.
#     individual_searches_frame = pd.merge(
#         individual_searches_frame, 
#         pd.DataFrame({
#             'search_title': total_results['search_title'], 
#             'search_location': total_results['search_location'], 
#             'TotalResults': total_results['description']
#             }),
#         on=['search_title', 'search_location'], 
#         how='left'
#         )

#     # Add the Unique Results count to the individual searches frame.
#     individual_searches_frame = pd.merge(
#         individual_searches_frame, 
#         pd.DataFrame({
#             'search_title': unique_results['search_title'], 
#             'search_location': unique_results['search_location'], 
#             'UniqueResults': unique_results['description']
#             }),
#             on=['search_title', 'search_location'], 
#             how='left'
#             )
    
#     # Where we didn't have a results count we must not have found anything, so replace the NaN with a 0.
#     for col in ['TotalResults', 'UniqueResults']:
#         individual_searches_frame[col][individual_searches_frame[col].isnull()] = 0

#     # Add the total search time to the data frame.
#     individual_searches_frame['TotalSearchTime'] = total_search_time
#     # Add any notes we have to the frame.
#     individual_searches_frame['Notes'] = notes
#     individual_searches_frame.to_csv('Diagnostics/ScraperPerformancebySearch.csv', mode='a+', header=False)
  

def preprocess_jobs(initial_data):
    """Clean up the jobs frame"""
    for col in initial_data.columns:
       if col != 'posted': 
            initial_data[col] = initial_data[col].str.replace('\n', ' ')
    processed_data = initial_data.drop_duplicates(subset=['title', 'company', 'description'], keep='first')
    processed_data['description'] = processed_data['description'].str.replace(r"([a-z])([A-Z])", r"\1 \.\2")
    processed_data['description'] = processed_data['description'].str.replace(r' \\.', '')
    return processed_data

        
# def save_search_stats(site: str, total_returned_jobs: int, unique_jobs: int, search_time: float, total_searches: int, notes = None):
#     """Write search statistics as new row in ScraperPerformance.csv"""
#     with open('Diagnostics/ScraperPerformance.csv', 'a+', newline='') as file:
#         write = csv.writer(file, delimiter=',')
#         if notes is not None:
#             notes = notes.replace(',', ';')
#         write.writerow([site, total_returned_jobs, unique_jobs, search_time, total_searches, date.today(), notes])

#####

###############
# Job titles
prefixes = [
    'entry level ', 
    'junior ', 'associate ', 
#    ''
    ]

titles = [
    'data',
    'data analyst', 'data scientist', 
    'business analyst', 'financial analyst',
#    'macro analyst', 
#    'data engineer'
            ]
 

search_locations = [
    'New York, NY', 
    'Stamford, CT',
    'Greenwich, CT',
    'Bridgewater, NJ', 
    'Newark, NJ', 'Princeton, NJ', 'Jersey City, NJ', 
    'Trenton, NJ', 
    'Somerville, NJ', 
    'Summit, NJ', 'Morristown, NJ', 'Edison, NJ', 'Metuchen, NJ', 'Hackensack, NJ',
#    'Philadelphia, PA',
    # 'New York', 'New Jersey', 'New Hampshire', 'Pennsylvania', 'Connecticut',
    # 'NY', 'NJ', 'CT', 
    # 'NH', 'PA',
#    'NH', "New Hampshire", "Manchester, NH", "Concord, NH", "Nashua, NH", "Brattleboro, NH", "Keene, NH",
    'remote' 
    ]

n_searches = (len(titles) * len(prefixes)) * len(search_locations)

search_times = []
individual_searches = []

ttm = True
start_time = time.time()
counter = 1

# Data Frame Stuff
# Empty container for posting info
jobs = []
visited_links = set()

########################
# Search Specific info #
########################
# This is a limited search!
# Prompt the user for a numeric value, and if the days posted are greater than the value, we disregard it.
n_days_ago = pd.to_numeric(input("Within how many days should we search?\nIntegers preferred.\n"))

# How many posts per locale
location_results = 70
# How far out should we look?
radius = 50
# Data Frame Columns
columns = [
    'search_title', 'search_location',
     'location', 'title', 'company', 'posted', 'salary', 'summary', 'link', 'description'
     ]

##################################################
# Start on the page with the boxes for each post #
#################################################
# For each state listed
#   Go to the url for entry level data analyst postins in that state
#   Get the jobs postings from pages 1 through 10
for search_location in search_locations: 
    for search_title in [(p + t) for p in prefixes for t in titles]:
        ####################################
        # Monitoring Chunk
        individual_searches.append([search_location, search_title])
        if counter > 1: 
            search_time = time.time() - search_start
            # search_times.append(search_time)
           # If the search time is less than 0.01 seconds it means they've shut us out. 
            if search_time < 0.01:
                print("They're on to us! Guess it's time to stop.")
                break 
            if ttm:
                print(f'The search took {search_time} seconds.\n')
        if ttm:
            print(f'Searching Indeed for {search_title} positions in {search_location}.\nSearch number {counter} of {n_searches}') 
        counter += 1
        search_start = time.time()
    #####################################
        for nresults in range(0, location_results, 10):
            time.sleep(2)
            url = f'https://www.indeed.com/jobs?q={search_title.replace(" ", "+")}+%2420%2C000&l={search_location.replace(" ", "+")}+&radius={radius}&start={str(nresults)}'
            results = get_job_results(url, "resultsCol")
            if results is None:
                continue
            job_elems = results.find_all('div', class_='jobsearch-SerpJobCard')
            

            # For each posting on the page
            #   1. Check that it's a valid job post.
            #   2. Check if it's been posted over 30 days ago. 
            #   3. Get the job information from the post
            for job in job_elems:
                title_elem = job.find('h2', class_='title')
                if title_elem is None:  
                    continue
                
                link = job.find('a')['href']
                new_url = f'https://www.indeed.com{link}'
                if new_url in visited_links:
                    continue
                else:
                    visited_links.add(new_url) 
                ################################
                # Collect only the recent jobs # 
                ################################
                # After prompting the user for a date range,
                # use it to fiter the search.
                # Jobs posted that day use "Today" and "Just posted",
                # hence "t" and "j". 
                posted = job.find('span', class_='date').text.strip()
                
                #if posted is None:
                #    continue
                if posted[0] == "+":
                    continue
                elif (posted[0] == "T") | (posted[0] == "J"):
                    posted = 0 
                elif pd.to_numeric(posted[:1]) > n_days_ago:
                    continue
                else:
                    posted = pd.to_numeric(posted[:1])
                
                title = title_elem.text.strip()

            
                company_elem = job.find('span', class_='company')

                
                location_elem = job.find('span', class_='location')
                salary_elem = job.find('span', class_='salary')

                summary_elem = job.find('div', class_='summary')
                

                # Make sure there's a company name associated, otherwise move on
                if company_elem is None:
                    continue
                else:
                    company_elem = company_elem.text.strip()

                # If there isn't a location provided, denote that
                if location_elem is None:
                    location_elem = 'No Location Provided'
                else:
                    location_elem = location_elem.text.strip()

                
                # If there isn't a job summary provided, denote that
                if summary_elem is None:
                    summary_elem = 'No Summary Provided'
                else:
                    summary_elem = summary_elem.text.strip()

                # If there isn't a salary provided, denote that
                if salary_elem is None:
                    salary_elem = 'No Salary Provided'
                else:
                    salary_elem = salary_elem.text.strip()

                ##################################
                # Go to the Job Description Page #
                ##################################
                time.sleep(2)

                # Get the job description from the new page
                description = get_job_results(new_url, "jobDescriptionText") 
                # If we screwed up locating the description, denote that
                if description is None:
                    description_text = 'could not find description'
                else:
                    description_text = description.text.strip()


                # Create an array of info for this job posting
                info = [search_title,
                    search_location,
                    location_elem, 
                    title,
                    company_elem,
                    posted,
                    salary_elem,
                    summary_elem,
                    new_url,
                    description_text
                ]

                # Append the job info array to the array of job posting arrays
                jobs.append(info)

# This adds the time for the final search.
search_time = time.time() - search_start
print("Final search took", search_time, "seconds.")
# search_times.append(search_time)
total_search_time = time.time() - start_time

if ttm:
     print(f'Indeed search took {total_search_time} seconds to retreive {len(jobs)} total results (including some duplicates).')


# Convert array of arrays into data frame
df_0 = pd.DataFrame(jobs, columns=columns)


tdy = datetime.now().strftime("%Y-%m-%d") 
file_name = tdy + "_indeed.csv" 

df_0.to_csv(f"data/rawdata/{file_name}", index=False)
df_0.to_csv(f"/home/pi/ShareDrive/data/0rawdata/{file_name}", index=False)

# filter and modify df going forward
df_1 = preprocess_jobs(df_0)

# Save the monitoring data into their respective csv's for later analysis.
# collect_individual_search_info saves into a new csv which monitors performance of each individual search
# collect_individual_search_info('Indeed', individual_searches, monster_0, monster_1, search_times_monster, total_search_time_monster)
# save_search_stats('Monster', len(monster_0), len(monster_1), total_search_time_monster, n_searches)


df_1.to_csv(f"data/{file_name}", index=False)
df_1.to_csv(f"/home/pi/ShareDrive/data/{file_name}", index=False)

print(f'Returned {len(df_1)} unique entries from Indeed.com \nThe file is dated {tdy}')

