def scrape_sitemap(url):
    if not urlparse(url).scheme:
        url = "https://" + url

    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error(f"El servidor respondió con un error: {response.status_code}")
            return []

        content_type = response.headers.get("Content-Type", "")
        if "xml" not in content_type:
            st.error("La URL no devolvió un sitemap XML válido.")
            return []

        tree = ET.fromstring(response.content)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in tree.findall(".//ns:loc", ns)]
        return urls

    except ET.ParseError as pe:
        st.error(f"Error al parsear el XML: {pe}")
        return []
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return []

