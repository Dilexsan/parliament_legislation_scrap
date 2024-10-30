import random
import time
import bs4
import requests
import urllib3
import pandas as pd
import os
import re

import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



from requestsAct import load_bills
# from clean_up_pdf_filenames import clean_up_file_names

import ssl
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.poolmanager import PoolManager


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        # This allows connections with lower DH key size
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

def setup_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
    adapter = SSLAdapter()
    adapter.max_retries = retries
    session.mount("https://", adapter)
    return session

def parse_page(page):
    soup = bs4.BeautifulSoup(page, "html.parser")
    return soup



def get_act_name(soup):
    # get text attribute of all h4 tags
    h4_tags = soup.find_all("h4")
    act_names = [tag.text for tag in h4_tags]
    act_names = [name.strip() for name in act_names]
    print(f"number of act names: {len(act_names)}")
    return act_names



def get_class_acts_box(soup):
    # get the div with class acts-box
    acts_boxes = soup.find_all("div", class_="acts_box")
    print(f"number of acts_box: {len(acts_boxes)}")
    return acts_boxes



def get_read_dates(acts_box):
    """
    find the div with class="con_box read_date", then get each span text

    """
    read_dates = []
    read_date_box = acts_box.find_all("div", class_="con_box read_date")
    print(f"number of read_date_box: {len(read_date_box)}")
    print(type(read_date_box))
    print(read_date_box)
    spans = read_date_box[0].find_all("span")
    read_dates.append([span.text for span in spans])
    return read_dates



def clean_act_name(act_name):
    act_name = act_name.replace(" ", "-")
    act_name = act_name.replace("-:-", "_")
    act_name = act_name.replace("--", "-")
    act_name = act_name.replace("/", "_")


    return act_name



def create_download_df(act_boxes):
    bills_with_det = []
    for act_box in act_boxes:
        print("------------------------------------------------------------------")
  
        # Find the specific 'Download Act' link
        download_link_tag = act_box.find("a", class_="act_down")
        scdet_pdf_link = download_link_tag["href"] if download_link_tag and "href" in download_link_tag.attrs else None

        # Get and clean the bill name
        act_name = act_box.find("h4").text.strip()
        act_name = clean_act_name(act_name)

        # Get the endorsed date
        endorsed_date = None
        date_box = act_box.find("span", text=lambda x: "Endorsed Date" in x if x else False)
        if date_box:
            endorsed_date = date_box.text.replace("Endorsed Date:", "").strip()

        dict_ = {
            "act_name": act_name,
            "act_link": scdet_pdf_link,
            "endorsed_date": endorsed_date
        }
        bills_with_det.append(dict_)

    print(f"number of bills with SC determination: {len(bills_with_det)}")
    print(bills_with_det)
    df = pd.DataFrame(bills_with_det)
    print(df)
    return df




def get_pagenav(soup):
    pagenav_div = soup.find("div", class_="list-footer")
    pagenav_spans = pagenav_div.find_all("span", class_="pagenav")

    paginate_nums = []
    for span in pagenav_spans:
        onclick_text = span.get("onclick", "")
        match = re.search(r"paginate\('(\d+)',", onclick_text)
        if match:
            paginate_nums.append(int(match.group(1)))

    print(f"number of pages: {len(paginate_nums)}")
    # print(paginate_nums)

    return paginate_nums



# def download_from_df(df):
#     session = requests.Session()
#     # Apply the adapter to HTTPS connections
#     session.mount("https://", SSLAdapter())

#     for idx, row in df.iterrows():
#         print("----------------------------------------------------")
#         print(f"downloading {idx}")
#         print(row)
#         time.sleep(random.randint(1, 5))

#         pdf_link = row["pdf_link"][0]
#         pdf_file_name = row["act_name"]
#         pdf_file_name = re.sub(r"[^a-zA-Z0-9]+", "_", pdf_file_name)
#         pdf_file_name = pdf_file_name.lower()

#         # pdf = requests.get(pdf_link)
#         pdf = session.get(pdf_link)  # Use the modified session with SSLAdapter
#         print(f"downloading {pdf_file_name}")
#         print(f"pdf link: {pdf_link}")
#         if not os.path.exists("pdfs_2022_onwards_fresh"):
#             os.makedirs("pdfs_2022_onwards_fresh")
#         pdf_file_name = f"pdfs_2022_onwards_fresh/{pdf_file_name}_{idx}.pdf"
#         print(f"pdf file name: {pdf_file_name}")
#         print("----------------------------------------------------")
#         with open(pdf_file_name, "wb+") as f:
#             f.write(pdf.content)
#         df.loc[idx, "file_location"] = pdf_file_name
#     return df



def download_act_links(df, parliment_id):
    session = setup_session_with_retries()
    
    # Create the directory if it does not exist
    directory_path = f"{parliment_id}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for idx, row in df.iterrows():
        act_link = row["act_link"]
        if act_link:
            print("----------------------------------------------------")
            print(f"Downloading act link {idx}")
            time.sleep(random.randint(5, 10))  # Use a longer, random delay

            pdf_file_name = row["act_name"].lower()
            pdf_file_path = f"{directory_path}/{pdf_file_name}.pdf"

            try:
                response = session.get(act_link, timeout=10)
                response.raise_for_status()
                
                print(f"Downloaded {pdf_file_path}")
                with open(pdf_file_path, "wb+") as f:
                    f.write(response.content)
                df.loc[idx, "act_file_location"] = pdf_file_path

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {pdf_file_path}: {e}")
                df.loc[idx, "act_file_location"] = None  # Mark failed downloads

    return df




if __name__ == "__main__":

    all_parliment_ids = [994, 993, 992 ,991, 900, 218,217,216,215,214,213,212,208,206,205,204,200 ]

for parliment_id in all_parliment_ids:

    page = load_bills("0", parliment_id)
    soup = parse_page(page)

    # Write the soup to a file as HTML
    html_file_name = f"{parliment_id}.html"
    with open(f"D:\\d\\Intern_works\\legislation_scrap\\html_files\\{html_file_name}", "w") as f:
        f.write(str(soup))

    next_pagination_nums = get_pagenav(soup)
    pagination_full = [0] + next_pagination_nums
    print(pagination_full)

    df_list = []

    for pagination in pagination_full:
        page = load_bills(str(pagination), parliment_id)
        soup = parse_page(page)

        acts_boxes = get_class_acts_box(soup)
        act_names = get_act_name(soup)

        # Create DataFrame for bills with SC determination
        df_to_download = create_download_df(acts_boxes)
        df_list.append(df_to_download)

    df = pd.concat(df_list).reset_index(drop=True)
    csv_file_name = f"{parliment_id}.csv"
    df.to_csv(f"D:\\d\\Intern_works\\legislation_scrap\\csv_files\\{csv_file_name}", index=False)

    # df = download_from_df(df)
    df = download_act_links(df, parliment_id)

    # df.to_csv("sc_determination_bills_file_loc.csv", index=False)

