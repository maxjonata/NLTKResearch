import concurrent.futures
import os
import re
import threading

import nltk
import requests
from bs4 import BeautifulSoup


def process_page(current_url, visited_pages, pages_to_visit, vocabulary, wiki_base_url):
    try:
        response = requests.get(current_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        body_content = soup.find('div', {'id': 'bodyContent'})
        page_content = body_content.find('div', {'id': 'mw-content-text'}) if body_content else None

        if page_content:
            page_text = page_content.get_text(separator=' ', strip=True)
            tokens = nltk.word_tokenize(page_text, language='portuguese')
            page_words = set()
            for token in tokens:
                clean_token = re.sub(r'[^a-zA-ZáàãâéèêíìîóòõôúùûçÁÀÃÂÉÈÊÍÌÎÓÒÕÔÚÙÛÇ]+', '', token).lower()
                if clean_token:
                    page_words.add(clean_token)

            vocabulary.update(page_words)

        content_links = page_content.find_all('a', href=True) if page_content else []
        body_links = body_content.find_all('a', href=True) if body_content and not page_content else []
        links = content_links if content_links else body_links

        new_urls = []
        for link in links:
            href = link.get('href')
            if href and href.startswith('/wiki/'):
                full_link_url = wiki_base_url + href
                new_urls.append(full_link_url)

        for url in new_urls:
            if url not in visited_pages and url not in pages_to_visit:
                pages_to_visit.add(url)

        visited_pages.add(current_url)

        print(f"Thread {threading.current_thread().name}: Processed {current_url}, found {len(page_words)} new words, {len(new_urls)} new links.")

    except requests.exceptions.RequestException as e:
        print(f"Thread {threading.current_thread().name}: Error accessing URL: {current_url} - {e}")
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Unexpected error processing {current_url} - {e}")

    return visited_pages, pages_to_visit

def generate_wiki_vocabulary_thread(initial_wiki_page_url, num_threads=8):
    vocabulary = set()
    visited_pages = set()
    pages_to_visit = set()
    pages_to_visit.add(initial_wiki_page_url)

    wiki_base_url = "https://codexofdarkness.com"

    print(f"Starting multi-threaded processing with {num_threads} threads...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        while pages_to_visit or futures:
            while pages_to_visit:
                url_to_process = pages_to_visit.pop()
                if url_to_process not in visited_pages:
                    future = executor.submit(process_page, url_to_process, visited_pages, pages_to_visit, vocabulary, wiki_base_url)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                visited_pages, pages_to_visit = future.result()
                futures.remove(future)

    print(f"Multi-threaded processing finished.")
    return list(vocabulary), list(visited_pages), list(pages_to_visit)

def write_vocabulary_to_file(vocabulary, file_name):
    with open(file_name, 'w') as f:
        for word in sorted(vocabulary):
            f.write(word + '\n')

initial_wiki_page_url = "https://codexofdarkness.com/wiki/Main_Page"
desired_num_threads = os.cpu_count() * 2

print(f"Extracting vocabulary from the Codex of Darkness wiki with {desired_num_threads} threads...")
codex_vocabulary, visited_pages, pages_to_visit = generate_wiki_vocabulary_thread(initial_wiki_page_url, num_threads=desired_num_threads)
write_vocabulary_to_file(codex_vocabulary, 'vocabulary_codex_darkness.txt')

print(f"Vocabulary extracted from the Codex of Darkness wiki (total unique words: {len(codex_vocabulary)}):")
print(f"First 200 words of the vocabulary (example):\n{', '.join(sorted(codex_vocabulary)[:200])}")
print(f"Visited pages: {len(visited_pages)}")
print(f"Pages to visit: {len(pages_to_visit)}")