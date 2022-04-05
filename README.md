# smart_contracts_scraper
Scrape Smart Contract addresses inside source code of website. Useful for finding contracts before token launches !  
# Installation
Install Python, create a venv, activate it and install requirements.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
# Usage
Edit settings.json according to your preferences: add rpc_endpoint corresponding to the blockchain the contract is deployed on, then add the website you want to scrape.  
Now, you can launch the script:
```
python main.py
```
You can see scrapped contracts (if found) in results.txt.
# Problems
The script may stop because of rate limits. I will add proxy supports and sleeps to avoid that issue.
