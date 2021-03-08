# Job hunting made easy(ish)

This repository is a combination of Python scripts, notebooks, as well as a Scrapy web spider.

## Scraping/Crawling

### Beautiful Soup
#### Insert Obligatory Lewis Carroll Reference Here

We have a few scripts all of which use Beautiful Soup to parse the xml on a few job boards. 
ScrapeRecentJobs checks the posted date before going to the job description page so we can contain our search.

It is suggested to run the full scraper first, then use the ScrapeRecentJobs to check what has been posted since the last scrape.

The scripts write the collected data to csv's when finished and are currently set up to write both raw and cleaned data.

### Scrapy 

Currently only the Monster spider is opperational. 
It goes to the JSON page for each job post and collects the data from there. 
The spider is called from the command line and needs a designated output file to write the info it returns.

## Sorting

After collecting the job posts, we use the SortJobs notebook to help us sift through what's collected.
Using a Pandas we slice the set, including or excluding jobs based on words in the job title as well as job description.

Additionally, we have included code that when we look through job descripitoins, we are prompted for whether this is a job that 
either we would apply to, we are underqualified, we are not interested, and other (y, u, n, o).
Based on our response, the descriptions are sorted into their respective categories and when we are done sorting, 
we write the data to csv's for use later in a machine learning classifier.

### NOTE: The following repository contains coarse code and due to its content should not be used by anyone
