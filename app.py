import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

def scrape_sitemap(url):
    if not urlparse(url).scheme:
        url = "https://" + url
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        urls = [loc.text for loc in soup.find_all("loc")]
        return urls
    except Exception as e:
        st.error(f"Error al acceder al sitemap: {e}")
        return []

def main():
    st.title("Auditor de Sitemap Simple")
    input_url = st.text_input("Ingresa la URL del sitemap (por ejemplo: https://tusitio.com/sitemap.xml)")
    
    if st.button("Extraer URLs"):
        if input_url:
            urls = scrape_sitemap(input_url)
            total = len(urls)
            
            if not urls:
                st.warning("No se encontraron URLs.")
                return

            st.success(f"Se encontraron {total} URLs.")
            
            results = []
            table_placeholder = st.empty()
            progress = st.progress(0)
            progress_text = st.empty()

            for i, url in enumerate(urls, start=1):
                results.append({"URL": url})
                df = pd.DataFrame(results)
                table_placeholder.dataframe(df)
                progress.progress(i / total)
                progress_text.text(f"{i}/{total} URLs procesadas")

            progress.empty()
            progress_text.empty()

            st.download_button(
                label="Descargar como CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="sitemap_urls.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
