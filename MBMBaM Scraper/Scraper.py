from bs4 import BeautifulSoup
import requests
import re
import urllib.request

# Set the folder to download to
folder = "D:/Podcasts and Browser Downloads/Auto-Downloaded MBMBAM/"

# Set the url for the podcasts homepage and retrieve the html object
url_no_page = "https://maximumfun.org/podcasts/my-brother-my-brother-and-me/?_paged="
homepage_url = "https://maximumfun.org/podcasts/my-brother-my-brother-and-me/?_paged=1"
homepage_content = requests.get(homepage_url).text

# Convert homepage html object to text
homepage_soup = BeautifulSoup(homepage_content, "lxml")
homepage_html_text = homepage_soup.prettify()


def find_urls(string):
    """
    Finds all urls corresponding to mbmbam episode pages from the string
    :param string: str 
    :return: lst[str]
    """
    url_list = re.findall('https://maximumfun.org/episodes/my-brother-my-brother-and-me/[^"]*', string)
    url_list = list(dict.fromkeys(url_list))
    return url_list


def next_page(url):
    """
    Takes a string of a url with a page number at the end and returns the same string with the number incremented by 1
    :param url: str
    :return: str
    """
    number = re.findall('[0-9]+', url)
    number = int(number[0])
    number += 1
    url = url_no_page + str(number)
    return url


def find_pages(input_string):
    """
    Finds all data-page=## objects in an html text and extracts the numbers
    :param input_string: str
    :return: lst[int]
    """
    page_numbers = []
    page_strings = re.findall('data-page=."[0-9]+."', input_string)
    for item in page_strings:
        number = int(re.findall('[0-9]+', item)[0])
        page_numbers.append(number)
    return page_numbers

def find_media(input_string):
    """
    Finds the media url in the input string and extracts it
    :param input_string: str
    :return: lst[str]
    """
    media_url_1 = re.findall('https://cdn.simplecast.com/audio/.*\.mp3', input_string)
    media_url_1 = list(dict.fromkeys(media_url_1))

    if media_url_1:
        return media_url_1[0]
    else:
        media_url_2 = re.findall('http://traffic.libsyn.com/mbmbam/.*\.mp3', input_string)
        media_url_2 = list(dict.fromkeys(media_url_2))
        return media_url_2[0]

def episode_number_finder(input_string):
    """
    Takes a string input corresponding the url of an episode media and extracts the episode number, if it exists
    :param input_string: str
    :return: int
    """
    format_1 = re.findall('(?i)mbmbam[0-9]+', input_string)
    format_2 = re.findall('(?i)MeEpisode[0-9]+', input_string)
    format_3 = re.findall('(?i)andMe[0-9]+', input_string)
    if format_1:
        return int(re.findall('[0-9]+', format_1[0])[0])
    elif format_2:
        return int(re.findall('[0-9]+', format_2[0])[0])
    elif format_3:
        return int(re.findall('[0-9]+', format_3[0])[0])
    else:
        return None

def download_episodes(first, last):
    """
    downloads mbmbam episodes to a folder from the first selected to the last selected
    :param first: int 
    :param last: int
    :return: None
    """
    # Stores the maximum page number
    max_page = max(find_pages(homepage_html_text))

    # Iterates for i between 1 and max_pages - 1
    page_urls = [homepage_url]
    working_url = homepage_url
    for i in range(1, max_page):
        working_url = next_page(working_url)
        page_urls.append(working_url)

    media_url_list = []
    for page_url in page_urls:
        page_url_text = str(BeautifulSoup(requests.get(page_url).text, "lxml"))
        for subpage_url in find_urls(page_url_text):
            subpage_html_text = str(BeautifulSoup(requests.get(subpage_url).text, "lxml"))
            media = find_media(subpage_html_text)
            episode_number = episode_number_finder(media)
            if episode_number is None:
                continue
            else:
                if first <= episode_number <= last:
                    if media not in media_url_list:
                        urllib.request.urlretrieve(media, folder + "mbmbam{}.mp3".format(str(episode_number)))
                        media_url_list.append(media)
                elif episode_number < first:
                    return None


def __main__():
    first = int(input("What is the earliest episode to download?"))
    last = int(input("What is the latest episode to download?"))
    download_episodes(first, last)
    print("\nEpisodes successfully downloaded!")


__main__()
