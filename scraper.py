# Example Code

def execute_scraping_process():
    current_time = datetime.now().strftime("%M mins %S secs")
    print(f"Task initiated at {current_time}")

    # Fetch the list of pool IDs
    pool_ids = fetch_pool_ids()

    for pool_id in pool_ids[0:1000]:  # Process from index 450 to 1000
        extracted_data = []
        print("Processing pool:", pool_id)
        page_url = f"https://dexscreener.com/solana/{pool_id}"

        try:
            # Open the webpage
            driver.get(page_url)
            time.sleep(1)  # Allow some time for the page to load

            print("Waiting for the 'Top Traders' button to become clickable")
            # Find and interact with the 'Top Traders' button
            top_traders_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Top Traders')]"))
            )

            print("Found button:", top_traders_btn)
            top_traders_btn.click()
            print("Clicked on 'Top Traders' button")

            # Give time for traders' data to load
            time.sleep(2)

            top_trader_addresses = []
            # Parse the page content using BeautifulSoup
            page_content = driver.page_source
            page_soup = BeautifulSoup(page_content, 'html.parser')
            trader_elements = page_soup.find_all('a', class_='chakra-link chakra-button custom-1hhf88o')[:10]

            for trader in trader_elements:
                link = trader['href']
                address = link.split("/")[-1]
                top_trader_addresses.append(address)

            print("Collected trader addresses:", top_trader_addresses)

            # Extract the holders' count from the button text
            holder_button_text = page_soup.find_all('button', class_='chakra-button custom-tv0t33')[1].get_text()

            if "Snipers" in holder_button_text:
                holder_button_text = page_soup.find_all('button', class_='chakra-button custom-tv0t33')[2].get_text()

            # Use regex to extract the holder count
            count_match = re.search(r'\((\d{1,3}(?:,\d{3})*)\)', holder_button_text)

            if count_match:
                clean_number = count_match.group(1).replace(',', '')
                holder_count = int(clean_number)
                print(f"Holder count for pool {pool_id}: {holder_count}")

                data_entry = {
                    'holders': holder_count,
                    'topTraders': top_trader_addresses
                }
                extracted_data.append(data_entry)

                # Insert or update the record in the MongoDB database
                collection.update_one(
                    {'poolID': pool_id},
                    {'$set': data_entry},
                    upsert=True
                )

        except Exception as error:
            print(f"An error occurred while processing pool {pool_id}: {error}")
            continue

execute_scraping_process()
