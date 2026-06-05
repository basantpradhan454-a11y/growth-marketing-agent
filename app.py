import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import json
from groq import Groq

st.set_page_config(page_title="Growth Marketing AI Agent", page_icon="🚀", layout="wide")

st.title("🚀 Growth Marketing AI Agent")
st.markdown("**Enter any website URL and get a complete 4-phase growth marketing strategy instantly!**")

# API Key input
groq_key = st.sidebar.text_input("🔑 Groq API Key", type="password", help="Get free key at console.groq.com")
st.sidebar.markdown("[Get free Groq API key →](https://console.groq.com)")

def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            meta_desc = meta.get("content", "")
        
        # Get main text content
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text().split())[:3000]
        
        return {"title": title, "meta": meta_desc, "content": text, "url": url}
    except Exception as e:
        return {"error": str(e)}

def generate_report(scraped_data, api_key):
    client = Groq(api_key=api_key)
    
    prompt = f"""You are a world-class growth marketing strategist. Analyze this website and create a comprehensive 4-phase growth marketing report.

Website URL: {scraped_data['url']}
Title: {scraped_data['title']}
Meta Description: {scraped_data['meta']}
Content: {scraped_data['content']}

Generate a detailed report with these 4 phases:

## 📊 PHASE 1: WEBSITE & PRODUCT ANALYSIS
- Core Value Proposition
- Target Audience (3-5 personas)
- Top 5 Core Features
- Problem Statement
- Competitive Advantage

## ✍️ PHASE 2: PREMIUM AD COPY
Write 3 high-converting ad copies:
- Ad 1: Problem-Solver Ad
- Ad 2: Feature-Highlight Ad  
- Ad 3: Short & Punchy Ad

## 📱 PHASE 3: MULTI-CHANNEL CONTENT
Write ready-to-post content for:
- LinkedIn Post (detailed, professional)
- Instagram Caption (with hashtags)
- Facebook Post
- Twitter/X Thread (5 tweets)

## 🎯 PHASE 4: LEAD GEN & COLD EMAIL STRATEGY
- Target Persona Description
- LinkedIn Boolean Search Strings (3 strings)
- Cold Email Sequence (3 emails: Opener, Follow-up, Breakup)

Make everything specific to THIS website, not generic. Be creative and compelling."""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content

# Main UI
url = st.text_input("🌐 Enter Website URL", placeholder="https://example.com")

if st.button("🚀 Generate Growth Marketing Report", type="primary", use_container_width=True):
    if not url:
        st.error("Please enter a URL!")
    elif not groq_key:
        st.error("Please enter your Groq API key in the sidebar!")
    else:
        with st.spinner("🔍 Scraping website..."):
            data = scrape_website(url)
        
        if "error" in data:
            st.error(f"Could not scrape website: {data['error']}")
        else:
            st.success(f"✅ Scraped: **{data['title']}**")
            
            with st.spinner("🤖 AI is generating your 4-phase strategy (30-60 seconds)..."):
                try:
                    report = generate_report(data, groq_key)
                    
                    st.markdown("---")
                    st.markdown("## 📋 Your Growth Marketing Report")
                    st.markdown(report)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"growth_report_{url.replace('https://','').replace('/','_')[:30]}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"AI Error: {str(e)}")

st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit + Groq AI | Free to use*")
