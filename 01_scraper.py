# 01_scraper.py
# WEB SCRAPER to get the list of filew to be downloaded
# From 2022 the URL to a verdict changed from www.giustizia-amministrativa.it to portali.giustizia-amministrativa.it

### IMPORT ### 
import mechanicalsoup
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re
import sys
from pathlib import Path
import requests
from os import replace as os_replace
from os.path import join as os_join

# print(sys.getrecursionlimit())

### LOCAL IMPORT ###
from verdict import Verdict 
from config.config_reader import read_config_yaml
from utility_manager.utilities import check_and_create_directory, script_info

### GLOBALS ###
yaml_config = read_config_yaml()
verdict_dir = str(yaml_config["VERDICTS_DIR"])
verdict_file_name = str(yaml_config["VERDICTS_FILE"])
paging = int(yaml_config["PAGING"])
url_search = str(yaml_config["URL_SEARCH"])
recursion_limit = int(yaml_config["RECURSION_LIMIT"])

script_path, script_name = script_info(__file__)

sys.setrecursionlimit(recursion_limit)

# INPUT
page_increment = 1 # <-- INPUT to start from a defined page (shift -> move the response of page + page_increment) starting always from 0

# OUTPUT
# URLs
total_results = 0  # total numbers of results
total_pages = 0 # total pages to be parsed
# verdicts
verdicts_download_count = 0 # global number of verdicts downloaded
verdicts_list_obj =[] # global list of verdicts
# CSV header
csv_result_header = "pagina;codice_ecli;provvedimento_titolo;provvedimento_tipo;sentenza_numero;tribunale_codice;tribunale_citta;tribunale_sezione;ricorso_numero;sentenza_url;sentenza_file"

### FUNCTIONS ###

def add_csv_header(verdict_dir:str, file_name:str, header:str) -> None:
    """
    Adds a header to a CSV file if it does not already have one.
    
    Args:
        verdict_dir (str): The verdict directory.
        file_name (str): The file CSV in which add the header.
        header (str): The header string to be added, separated by semicolons.
    Returns:
        None
    """
    file_path = os_join(verdict_dir, file_name)

    temp_file_path = file_path + '.temp'
    
    # Read the existing content of the file
    with open(file_path, 'r', newline='') as file:
        content = file.readlines()
    
    # Write the header and the original data to a new file
    with open(temp_file_path, 'w', newline='') as new_file:
        new_file.write(header + '\n')  # Write the new header
        new_file.writelines(content)   # Write the original data
    
    # Replace the old file with the new one
    os_replace(temp_file_path, file_path)

def get_administrative_judgment(input_search:str, page:int, year_search:int, browser:mechanicalsoup.stateful_browser.StatefulBrowser, paging:int, sentence_file_name:str, total_pages:int, verdicts_download_count:int, page_increment:int) -> None: 
    """ 
    Compile and submit the IAJ form: input_search is the querystring, page = 0 is the first page of results 
    Retrieve administrative judgments based on specified criteria.

    Args:
        input_search (str): The search query or keywords.
        page (int): The current page number.
        year_search (int): The year of the judgment.
        browser (mechanicalsoup.stateful_browser.StatefulBrowser): The browser object for web scraping.
        paging (int): The number of pages to navigate.
        sentence_file_name (str): The name of the file to save the judgments.
        total_pages (int): The total number of pages of search results.
        verdicts_download_count (int): The count of verdicts to download per page.
        page_increment (int): The increment value for page navigation.

    Returns:
        None: The function does not return anything. It saves the retrieved judgments to a file.
    """

    form_id = "_GaSearch_INSTANCE_2NDgCF3zWBwk_provvedimentiForm"

    try:
        browser.select_form('form[id="'+form_id+'"]') # get the form data by id
        # print(browser.get_current_form().print_summary()) # get the content objects of the form (debug)
        
        browser["_GaSearch_INSTANCE_2NDgCF3zWBwk_searchtextProvvedimenti"] = input_search # textbox
        browser["_GaSearch_INSTANCE_2NDgCF3zWBwk_pageResultsProvvedimenti"] = paging # selectbox
        browser["_GaSearch_INSTANCE_2NDgCF3zWBwk_TipoProvvedimentoItem"] = "Sentenza" # selectbox
        browser["_GaSearch_INSTANCE_2NDgCF3zWBwk_DataYearItem"] = str(year_search) # selectbox

        # _GaSearch_INSTANCE_2NDgCF3zWBwk_DataYearItem

        if (page == 0):  # if it's the first time, save the number of results
            response = browser.submit_selected()
            html_content = bs(response.text, 'html.parser')
            res_num = int(html_content.strong.string) # results number
            # Pages goes to 0 to n (visualized in the web page as 1 to n+1)
            # total_pages = int(res_num/paging) + int(res_num%paging) # number of the pages to be parsed (not working)
            temp_last_page_1 = html_content.find_all('li', {'class':'pagination-li'}) # [-1] contains the last page
            # print("temp_last_page 1:", temp_last_page_1[-1]) # debug
            for tag in temp_last_page_1[-1].find_all('a'):
                try:
                    if re.match('changePage',tag['onclick']):           # if onclick attribute exist, it will match for changePage, if success will print
                        # print("Last page object:", x['onclick'])      # debug
                        onclick = tag['onclick']                        # string value inside onclik
                        onclick_value = re.findall("[0-9]+",onclick)    # get the numbers inside the Javascript function (is a list)
                        last_page = int(onclick_value[0])
                        # print("Last page value:", str(l_page))        # debug
                        total_pages = last_page
                except:
                    print("Error on changePage RegEx")
                    print()
            print("Results found via URL:", res_num)
            print("Paging:", paging)
            print("Page shift:", page_increment)
            print("Total pages to be parsed:", total_pages)
            print()

        # if element "_GaSearch_INSTANCE_2NDgCF3zWBwk_step" is not available, LinkNotFoundError happens
        if (page != 0):
            browser["_GaSearch_INSTANCE_2NDgCF3zWBwk_step"] = page 
            response = browser.submit_selected()
            # print(type(response)) # <class 'requests.models.Response'> (debug)

        print(">> Parsing response pages")
        print(f"Page {page} / {total_pages}")

        response_parser(input_search, response, page, year_search, browser, paging, sentence_file_name, total_pages, verdicts_download_count, page_increment) # parse the results (response) for the text_to_search
    
        return
    
    except mechanicalsoup.LinkNotFoundError as e:
        print(f"LinkNotFoundError trying to connect to '{url_search}' (to form elements too)")


def response_parser(input_search:str, response:requests.models.Response, page:int, year_search:int, browser:mechanicalsoup.stateful_browser.StatefulBrowser, paging:int, sentence_file_name:str, total_pages:int, verdicts_download_count:int, page_increment:int) -> None:
    """
    Parse the response from the web server for administrative judgments.

    Args:
        input_search (str): The search query or keywords.
        response (requests.models.Response): The response object from the web server.
        page (int): The current page number.
        year_search (int): The year of the judgment.
        browser (mechanicalsoup.stateful_browser.StatefulBrowser): The browser object for web scraping.
        paging (int): The number of pages to navigate.
        sentence_file_name (str): The name of the file to save the judgments.
        total_pages (int): The total number of pages of search results.
        verdicts_download_count (int): The count of verdicts to download per page.
        page_increment (int): The increment value for page navigation.

    Returns:
        None: The function does not return anything. It processes the response and saves the retrieved judgments to a file.
    """
    
    count = 0 # local count for paging

    sentence_list_obj = [] # reset the list of found sentence
    
    html_content = bs(response.text, 'html.parser')

    articles_num = len(html_content.findAll("article")) - 1 # -1 because the last article is not a verdicts

    print("Articles (number of sentences) in this page:", str(articles_num))

    print()

    # for each <article> (a verdict) extract the data (location, link, ECLI, etc...)
    for article in html_content.findAll("article"):
        count+=1 # increment local count of download (for the paging)
        verdicts_download_count+=1 # increment global count (for the whole download)

        # if (count > paging): # it it's over the paging save it to csv (does not work fot he last page with less articles)
        if (count > articles_num):
            print("Results parsed for this page:", count-1)
            print("-> Total sentences parsed until this page:", verdicts_download_count-1)

            # write sentences to CSV
            print("Writing CSV file sentences...")
            for a_sentence in sentence_list_obj:
                sentence_csv = a_sentence.toCSV() # stream a verdicts from obj to csv string

                file_name = sentence_file_name.replace("Y", str(year_search))
                csv_file_path = Path(verdict_dir) / file_name

                with open(csv_file_path, mode="a") as fp:
                    fp.write(f"{page};{sentence_csv}\n")

            print()

            # submit a new page
            if (page == 0): # if it's in page 0, move of a shift to start to a new paging, else move of 1
                page=page+page_increment
            else:
                page=page+1

            print()
            print("New page -->", str(page))

            if (page > total_pages): # if the new page it's over the total pages stop it
                print("Web scraper finished")
                print("Year:", year_search)
                print()
                return
            else:
                get_administrative_judgment(input_search, page, year_search, browser, paging, sentence_file_name, total_pages, verdicts_download_count, page_increment)

        verdict = Verdict() # create a new verdict object and extract the data from <article>

        print(f"Result [{str(count)}] / page [{str(page)}]")
        # print(type(article.get("class"))) # the class is a list so [0] is the first attribute searched
        if (article.get("class")[0] == "ricerca--item"):
            for link in article.findAll("a"):
                if (link.get("data-sede") != None):
                    # print(link["data-sede"]) # code of the tribunal
                    verdict.tribunal_code = link["data-sede"]
                    # print(link["href"])
                    # verdict.sentence_url = url + link["href"] # OLD URL, from 2022 it's changed and it's complete in the href
                    verdict.sentence_url = link["href"]
                    string_href = link["href"].split("&")
                    string_file_name = string_href[3].split("=")
                    string_file = link["data-sede"] + "_" + string_file_name[1]
                    # print(string_file)
                    verdict.sentence_filename = string_file
        div_count = 0
        for div in article.findAll("div", {"class": "col-sm-12"}):
            div_count+=1
            if (div_count==1): # title from the second div
                a_count = 0
                for ahref in div.findAll("a"):
                    a_count+=1
                    if (a_count==2):
                        # print(ahref.string)
                        verdict.sentence_title = ahref.string
            if (div_count==2): # type, city, section, number
                # print(div)
                bcount = 0
                for b in div.findAll("b"):
                    bcount+=1
                    # print(b.string)
                    if (bcount==1):
                        verdict.sentence_type = b.string
                    if (bcount==2):
                        verdict.tribunal_city = b.string
                    if (bcount==3):
                        verdict.tribunal_section = b.string
                    if (bcount==4):
                        verdict.sentence_number = b.string
            # div_count==3 not needed
            if (div_count==4): # recourse number
                # print(div)
                for b in div.findAll("b"):
                    # print(b.string)
                    verdict.recourse_number = b.string
            if (div_count==5): # ecli
                # print(div)
                for b in div.findAll("b"):
                    # print(b.string)
                    verdict.sentence_ecli = b.string
            else:
                verdict.sentence_ecli = None

        print(verdict.toString())
        if (page==0): # it is the first running (page_increment = 1), the page 0 is needed in the list
            if (page_increment==1):
                sentence_list_obj.append(verdict) # add a verdict to the list
        else:
            sentence_list_obj.append(verdict) # add a verdict to the list

### MAIN ###
def main():
    print()
    print(f"*** PROGRAM START ({script_name}) ***")
    print()

    start_time = datetime.now().replace(microsecond=0)

    print("Start process:", start_time)
    print()

    print(">> Query input")
    if len(sys.argv) > 2:
        input_search = sys.argv[1]
        year_search = int(sys.argv[2])
        print("Query:", input_search)
        print("Year:", year_search)
    else:
        print("WARNING! Query and/or Year input missing, quitting the program.")
        print(f"Use example: {script_name} 'appalt*' 2023")
        print()
        quit()
    print()

    # create the output directories
    print(">> Creating output directories")
    print(f"Creating '{verdict_dir}' directory")
    check_and_create_directory(verdict_dir)
    print(f"Creating '{verdict_dir}/{year_search}' directory")
    check_and_create_directory(str(year_search), verdict_dir)
    print()

    print(">> Starting the mechanicalsoup")
    browser = mechanicalsoup.StatefulBrowser() # web scraper object
    # print(type(browser)) # <class 'mechanicalsoup.stateful_browser.StatefulBrowser'>
    browser.open(url_search)
    browser.follow_link("dcsnprr") # moves to <url>/dcsnprr
    print("URL:",browser.get_url())
    print("Year:",year_search)
    print("Query:",input_search)
    print()

    # Crawl the IAJ website
    get_administrative_judgment(input_search, 0, year_search, browser, paging, verdict_file_name, total_pages, verdicts_download_count, page_increment)
    print()
    
    # Add the header
    print(">> Adding CSV header to results")
    file_name = verdict_file_name.replace("Y", str(year_search))
    add_csv_header(verdict_dir, file_name, csv_result_header)
    print()

    end_time = datetime.now().replace(microsecond=0)
    delta_time = end_time - start_time

    print("End process:", end_time)
    print("Time to finish:", delta_time)
    print()

    print()
    print("*** PROGRAM END ***")
    print()

if __name__ == "__main__":
    main()

