## Code to scrape today's arxiv and email yourself unread papers
## Script requires existing author and topic lists, stored in the same folder
## These should be called 'topics.txt' and 'authors.txt'

import feedparser
import requests
from bs4 import BeautifulSoup
import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# now, compare with my lists
def read_list_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = []
        for line in f:
            clean_line = line.strip()
            # Remove backslashes before quotes, if any
            clean_line = clean_line.replace('\\"', '"').replace("\\'", "'")
            if clean_line:
                lines.append(clean_line)
    return lines

def read_paper_list_from_txt(filepath):
    """
    Reads a plain .txt file and reconstructs a list of paper dictionaries.
    """
    separator = " ~|~ "
    papers = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(separator)
                if len(parts) == 5:
                    arxiv_id, title, authors_str, abstract_url, abstract = parts
                    authors = [a.strip() for a in authors_str.split(";")]
                    paper = {
                        'arxiv_id': arxiv_id,
                        'title': title,
                        'authors': authors,
                        'abstract_url': abstract_url,
                        'abstract': abstract
                    }
                    papers.append(paper)
    else:
        print('Creating new old_papers.txt')
    return papers

def write_paper_list_to_txt(paper_list, filepath):
    """
    Writes each paper dict to a line in a plain .txt file using a custom separator.
    """
    separator = " ~|~ "  # unlikely to occur in normal text
    with open(filepath, 'w', encoding='utf-8') as f:
        for paper in paper_list:
            line = separator.join([
                paper['arxiv_id'],
                paper['title'].replace('\n', ' ').strip(),
                "; ".join(paper['authors']),
                paper['abstract_url'],
                paper['abstract'].replace('\n', ' ').strip()
            ])
            f.write(line + '\n')

def fetch_latest_astro_ph_with_abstracts():
    url = "https://arxiv.org/list/astro-ph/new"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    dl = soup.find('dl')
    if not dl:
        print("Could not find listing (<dl>) on the page.")
        return []

    dt_tags = dl.find_all('dt')
    dd_tags = dl.find_all('dd')

    if len(dt_tags) != len(dd_tags):
        print("Warning: Mismatch between number of <dt> and <dd> elements")

    papers = []

    for dt, dd in zip(dt_tags, dd_tags):
        # arXiv ID and abstract URL
        link_tag = dt.find('a', title='Abstract')
        arxiv_id = link_tag.text.strip() if link_tag else None
        abstract_url = f"https://arxiv.org{link_tag['href']}" if link_tag else None

        # Title
        title_tag = dd.find('div', class_='list-title')
        title = title_tag.text.replace('Title:', '').strip() if title_tag else None

        # Authors
        authors_tag = dd.find('div', class_='list-authors')
        authors = [a.text.strip() for a in authors_tag.find_all('a')] if authors_tag else []

        # Abstract (requires following the abstract URL)
        abstract = None
        if abstract_url:
            abs_resp = requests.get(abstract_url)
            abs_soup = BeautifulSoup(abs_resp.text, 'html.parser')
            abstract_tag = abs_soup.find('blockquote', class_='abstract')
            if abstract_tag:
                abstract_text = abstract_tag.get_text(strip=True)
                abstract = abstract_text.replace('Abstract:', '').strip()

        papers.append({
            'arxiv_id': arxiv_id,
            'title': title,
            'authors': authors,
            'abstract_url': abstract_url,
            'abstract': abstract
        })
    return papers

def send_paper_email(papers, from_addr, to_addr, smtp_server, smtp_port, password):
    # Compose email content
    message_body = ""
    for paper in papers:
        authors = ", ".join(paper['authors'])
        clean_abstract = paper['abstract'].replace('\n', ' ').replace('\r', ' ').strip()
        clean_title = paper['title'].replace('\n', ' ').replace('\r', ' ').strip()
        clean_link = paper['abstract_url']
        message_body += f"Title: {clean_title}<br>"
        message_body += f"Authors: {authors}<br>"
        message_body += f'Link: <a href="{clean_link}">Arxiv link</a><br>'
        message_body += f"Abstract: {clean_abstract}<br>"
        message_body += "-" * 80 + "<p>"

    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "arXiv Paper Summaries"

    # Attach the message body as plain text
    msg.attach(MIMEText(message_body, 'html'))

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(from_addr, password)
        server.send_message(msg)
        print("Email sent successfully!")


def send_warning_email(from_addr, to_addr, smtp_server, smtp_port, password):
    # Compose email content
    message_body = ""

    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "papergirl not working today - please attend"

    # Attach the message body as plain text
    msg.attach(MIMEText(message_body, 'html'))

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(from_addr, password)
        server.send_message(msg)
        print("Warning email sent successfully!")

def papergirl():

    author_list = read_list_from_file('./authors.txt')
    topic_list = read_list_from_file('./topics.txt')
    previously_collected = read_paper_list_from_txt('old_papers.txt')

    ## Actually fetch all papers from today's arxiv
    papers = fetch_latest_astro_ph_with_abstracts()

    ## Check today's papers for my author and topic lists
    num_papers = len(papers)
    collected = []
    send_warning = False
    if (num_papers == 0):
        send_warning = True
        exit

    i = 0
    for paper in papers:
        collect_it = False

        # check if it's already been collected
        if paper in previously_collected:
            continue

        # check if the authors are people we are looking for
        for author in paper['authors']:
            last_name = author.split()[-1]
            for item in author_list:
                if last_name in item:
                    collect_it = True

        # check if the title or abstract has any of our key words
        summary = paper['abstract'].lower()
        if any(word.lower() in summary for word in topic_list):
            collect_it = True
        # now if we need to, add it to the list
        # also add it to the historical list so we don't collect it twice
        if (collect_it == True):
            collected.append(paper)
            previously_collected.insert(0,paper)
        i += 1

    # Now write the first 100 previously collected papers to file so we can keep a record
    write_paper_list_to_txt(previously_collected,'old_papers.txt')

    ## Send this information to myself

    # now send myself an email with this info

    # retrieve the app password
    app_password = os.getenv("PAPERGIRL_PASSWORD")
    app_from = os.getenv("PAPERGIRL_FROM")
    app_to = os.getenv("PAPERGIRL_TO")

    call_stop = False
    if (app_password == None): call_stop = True
    if (app_from == None): call_stop = True
    if (app_to == None): call_stop = True

    if (call_stop):
        sys.exit('Stored app details are missing, save appropriately and try again.')

    if (send_warning == True):
        send_warning_email(
        from_addr=app_from,
        to_addr=app_to,
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        password=app_password  # Use app password, not your Gmail password
        )
    else:
        send_paper_email(
            from_addr=app_from,
            papers=collected,
            to_addr=app_to,
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            password=app_password  # Use app password, not your Gmail password
        )

if __name__ == "__main__":
    synchronise_for_movie()