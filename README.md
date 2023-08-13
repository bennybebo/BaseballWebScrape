# BaseballWebScrape

This project is a web scraping tool designed to gather Major League Baseball (MLB) data from various websites and generate data sheets in a presentable format. 
The data sheets can be easily shared on Twitter (@BlueChipProps), providing valuable information for sports betting fans.

How it Works:
The program utilizes web scraping techniques to extract data from different websites that provide MLB statistics, such as player's hit rates, home run rates,
, pitcher matchups for today, YRFI (Yes Run First Inning) probabilities, and current sportsbook odds for a prop. The scraped data is then processed and organized into 
dataframes and excel sheets that are suitable for sharing on Twitter.

The project consists of the following components:
Web Scraping: Uses libraries like BeautifulSoup and Pandas to extract data from specific URLs. It navigates through the web pages, identifies the 
relevant data elements, and extracts the desired information. Websites backend api calls were also used to collect data.

Data Processing: Once the data is scraped, it goes through a processing phase where it is cleaned, filtered, and transformed into a format suitable for presentation. 
This includes handling missing values, formatting headers, converting units, and matching players/teams to collected data.

Data Sheet Generation: The processed data is used to generate data sheets in a presentable format. These sheets use VisualBasic macros in order to format, highlight, and
beautify the data sheets into a presentable end product that is saved directly to your desktop. Using the Dinger Tuesday Template with VBA macros already written, the python program opens the template, fills it with today's data, runs the macro and then closes the file.

### Dinger Tuesday Sheet:
![Dinger Tuesday Pic](https://github.com/bennybebo/BaseballWebScrape/assets/98127047/0857dfc9-a814-4f3b-92fb-420e69a7f52b)

### Hit Sheet:

### Cold Streak Sheet:
![Cold Streak Pic](https://github.com/bennybebo/BaseballWebScrape/assets/98127047/be0798e4-7e17-48d8-b2aa-e4d0aca1b54f)
