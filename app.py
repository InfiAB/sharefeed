from turtle import heading
import spacy
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf

import streamlit as st

st.title("Buzzing stocks :zap:")

nlp = spacy.load("en_core_web_sm")

def extract_text_from_rss(rss_link):
	# parses the xml and extracts the headings 
	# form the links in a python list 
	headings = []
	r1 = requests.get("https://www.moneycontrol.com/rss/buzzingstocks.xml")
	r2 = requests.get(rss_link)

	soup1 = BeautifulSoup(r1.content, features='lxml')
	soup2 = BeautifulSoup(r2.content, features='lxml')

	headings1 = soup1.findAll('title')
	headings2 = soup2.findAll('title')

	return headings1 + headings2

def generate_stock_info(headings):
    """
    Goes over each heading to find out the entities and link them with the nifty companies data
    Extract the market data using yahoo finanace ticker function 

    Return: data frame containing all the buzzing stocks and their stats
    """
    stock_info_dict = {
        'Org': [],
        'Symbol': [],
        'currentPrice': [],
        'dayHigh': [],
        'dayLow': [],
        'forwardPE': [],
        'dividendYield': [],
    }

    stocks_df = pd.read_csv("./data/ind_nifty500list.csv")
    for title in headings:
        doc = nlp(title.text)
        for ent in doc.ents: 
            try: 
                if stocks_df['Company Name'].str.contains(ent.text).sum():
                    symbol = stocks_df[stocks_df['Company Name'].str.\
                        conatins(ent.text)]['Symbol'].values[0]
                    org_name = stocks_df[stocks_df['Company Name'].str.\
                        conatins(ent.text)]['Company Name'].values[0]

                    # sending yfinance the symbol for stock info
                    stock_info = yf.Ticker(symbol+".NS").info()

                    stock_info_dict['Org'].append(org_name)
                    stock_info_dict['Symbol'].append(symbol)
                    stock_info_dict['currentPrice'].append(stock_info['currentPrice'])
                    stock_info_dict['dayHigh'].append(stock_info['dayHigh'])
                    stock_info_dict['dayLow'].append(stock_info['dayLow'])
                    stock_info_dict['forwardPE'].append(stock_info['forwardPE'])
                    stock_info_dict['dividendYield'].append(stock_info['dividendYield'])
                else: 
                    pass
            except: 
                pass
    
    output_df = pd.DataFrame(stock_info_dict)
    return output_df

# add and input field to pass the RSS link 
user_input = st.text_input("Add your RSS link here!", "https://www.moneycontrol.com/rss/buzzingstocks.xml")

# get the financial headlines 
fin_headings = extract_text_from_rss(user_input) 

# output the financial info 
output_df = generate_stock_info(fin_headings)
output_df.drop_duplicates(inplace=True)
st.dataframe(output_df)

# display the headlines as well 
with st.expander("Expand for financial stocks new!"):
    for head in fin_headings: 
        st.markdown("* " + head.text)
