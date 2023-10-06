#!/usr/bin/env python3
USERNAME = 'idc-administrator'
PASSWORD = 'large data is the best.'

import asyncio
import os
from pyppeteer import launch
import csv

DRUPAL_LOGIN_URL = 'https://stage.digital.library.jhu.edu/user/login'
BASE_URL = 'https://stage.digital.library.jhu.edu'

def load_input_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        return list(csv.DictReader(file))

def mark_as_completed(url):
    with open("completed.txt", "a") as f:
        f.write(url + "\n")

def is_completed(url):
    try:
        with open("completed.txt", "r") as f:
            completed_urls = f.readlines()
            return url + "\n" in completed_urls
    except FileNotFoundError:
        return False

async def main():
    browser = await launch(headless=True, args=['--no-sandbox'])
    print("Browser launched...")

    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 800})
    await page.goto(DRUPAL_LOGIN_URL)
    print(f"Opened tab for {DRUPAL_LOGIN_URL}...")

    await page.type('input[name=name]', USERNAME)
    await page.type('input[name=pass]', PASSWORD)
    await page.click('input[value="Log in"]')
    await page.waitForSelector('#toolbar-link-workbench-content')

    input_data = load_input_csv('input.csv')
    total_urls = len(input_data)

    if not os.path.isfile('output.csv'):
        with open('output.csv', 'w', newline='') as f:
            fieldnames = list(input_data[0].keys()) + ['file']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    MAX_RETRIES = 3

    for row_data in input_data:
        url = row_data['url'].replace("https://digital.library.jhu.edu", "https://stage.digital.library.jhu.edu")
        total_urls -= 1
        if is_completed(url):
            print(f"{url} has already been processed. Skipping...")
            continue
        
        for attempt in range(MAX_RETRIES):
            try:
                media_url = f"{url}/media"
                await page.goto(media_url)

                rows_length = len(await page.querySelectorAll("table.views-table tbody tr"))
                found_intermediate_file = False

                # First loop to check for any Intermediate Files
                for i in range(rows_length):
                    row = await page.querySelector(f"table.views-table tbody tr:nth-child({i+1})")
                    if not row:
                        continue
                    media_use = await row.querySelector("td.views-field.views-field-field-media-use")
                    if not media_use:
                        continue
                    media_use_text = await page.evaluate('(element) => element.textContent', media_use)
                    if "Intermediate File" in media_use_text:
                        found_intermediate_file = True
                        break  # Once we know there's at least one Intermediate File, break out

                # Second loop based on whether we found an Intermediate File or not
                file_urls = []
                for i in range(rows_length):
                    row = await page.querySelector(f"table.views-table tbody tr:nth-child({i+1})")
                    if not row:
                        continue
                    media_use = await row.querySelector("td.views-field.views-field-field-media-use")
                    if not media_use:
                        continue
                    media_use_text = await page.evaluate('(element) => element.textContent', media_use)

                    if found_intermediate_file and "Intermediate File" in media_use_text:
                        print("Found intermediate file. Getting its URL...")
                        edit_link = await row.querySelector("li.edit.dropbutton-action a")
                        if edit_link:
                            edit_link_href = await page.evaluate('(element) => element.href', edit_link)
                            # Set timeout to 1000000 ms (1000 seconds) to allow for jp2 problems.
                            print(f"Opening {edit_link_href}...")
                            await page.goto(edit_link_href, timeout=1000000)
                            await page.waitForSelector('#edit-submit')
                            remove_btn = await page.querySelector('input[type="submit"][value="Remove"]')
                            file_url_elements = await remove_btn.Jx("//span[contains(@class, 'file')]//a[@href]")
                            if file_url_elements:
                                file_url_element = file_url_elements[0]
                                file_url = await page.evaluate('(element) => element.href', file_url_element)
                                file_urls.append(file_url)
                                await page.goto(media_url)

                    elif not found_intermediate_file and "Original File" in media_use_text:
                        print("Found original file (and no intermediate file).")
                        edit_link = await row.querySelector("li.edit.dropbutton-action a")
                        if edit_link:
                            edit_link_href = await page.evaluate('(element) => element.href', edit_link)
                            # Set timeout to 1000000 ms (1000 seconds) to allow for jp2 problems.
                            print(f"Opening {edit_link_href}...")
                            await page.goto(edit_link_href, timeout=1000000)
                            await page.waitForSelector('#edit-submit')
                            remove_btn = await page.querySelector('input[type="submit"][value="Remove"]')
                            file_url_elements = await remove_btn.Jx("//span[contains(@class, 'file')]//a[@href]")
                            if file_url_elements:
                                file_url_element = file_url_elements[0]
                                file_url = await page.evaluate('(element) => element.href', file_url_element)
                                file_urls.append(file_url)
                                await page.goto(media_url)

                mark_as_completed(url)
                break
            except Exception as e:
                print(f"Error processing {url}. Error message: {e}.")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(10)
                else:
                    print(f"Failed processing {url} after {MAX_RETRIES} attempts. Skipping...")
        
        row_data['file'] = '|'.join(file_urls)
        with open('output.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())
            writer.writerow(row_data)

    await browser.close()

asyncio.get_event_loop().run_until_complete(main())