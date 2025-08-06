import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import RequestException

# Definimos un header común para simular navegador
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

st.set_page_config(page_title="Herramienta de Auditoría SEO para una Página", layout="centered")
st.title("🔎 Herramienta de Auditoría SEO para una Página")

st.write("""
Esta app permite realizar una auditoría técnica rápida para una sola página web.
Ideal para aprender sobre SEO técnico y detectar mejoras rápidas.
""")

url = st.text_input("1. Ingresá la URL que querés auditar:", placeholder="https://ejemplo.com")

if url:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Análisis Title y Meta Description
        st.subheader("🏷️ Etiqueta Title y Meta Description")
        title_tag = soup.title.string.strip() if soup.title else "No se encontró etiqueta <title>"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc_content = meta_desc['content'].strip() if meta_desc and 'content' in meta_desc.attrs else "No se encontró meta descripción"
        st.markdown(f"**Title:** {title_tag}")
        st.markdown(f"**Meta Description:** {meta_desc_content}")

        # 2. Revisión H1
        st.subheader("🔖 Etiquetas H1")
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        if h1_tags:
            for i, h1 in enumerate(h1_tags):
                st.markdown(f"**H1 #{i+1}:** {h1}")
        else:
            st.write("No se encontraron etiquetas H1")

        # 3. Enlaces internos y texto ancla
        st.subheader("🔗 Enlaces internos y texto ancla")
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        internal_links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            anchor_text = a.get_text(strip=True)
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == parsed_url.netloc:
                internal_links.append((full_url, anchor_text))

        st.markdown(f"Se encontraron {len(internal_links)} enlaces internos (mostrando hasta 20):")
        broken_links = []
        for link, anchor in internal_links[:20]:
            try:
                r = requests.head(link, headers=HEADERS, allow_redirects=True, timeout=5)
                status = r.status_code
                if status >= 400:
                    broken_links.append(link)
                    st.markdown(f"- ❌ [{anchor}]({link}) - Estado: {status}")
                else:
                    st.markdown(f"- ✅ [{anchor}]({link}) - Estado: {status}")
            except RequestException:
                broken_links.append(link)
                st.markdown(f"- ❌ [{anchor}]({link}) - Estado: no responde")

        if broken_links:
            st.warning(f"Se encontraron {len(broken_links)} enlaces internos rotos.")
        else:
            st.success("No se encontraron enlaces rotos entre los primeros 20 enlaces internos.")

        # 4. Diagnóstico de imágenes
        st.subheader("🖼️ Diagnóstico de imágenes")
        images = soup.find_all("img")
        if images:
            missing_alt = [img.get('src', '') for img in images if not img.get('alt')]
            st.markdown(f"Se encontraron {len(images)} imágenes (mostrando hasta 20):")
            for img in images[:20]:
                src = img.get('src', '')
                alt = img.get('alt', '')
                st.markdown(f"- {'⚠️' if not alt else '✅'} `{src}` - alt: '{alt}'")
        else:
            st.write("No se encontraron imágenes.")

        # 5. Accesibilidad básica
        st.subheader("♿ Evaluación básica de accesibilidad")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                st.success("La página es accesible (status 200).")
            else:
                st.warning(f"Respuesta HTTP: {r.status_code}")
        except Exception as e:
            st.error(f"No se pudo acceder a la página: {e}")

        # 6. Crawlabilidad básica: verificar robots.txt y sitemap.xml
        st.subheader("🕷️ Crawlabilidad básica")
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            robots = requests.get(robots_url, headers=HEADERS, timeout=5)
            if robots.status_code == 200:
                st.success("Archivo robots.txt encontrado:")
                st.code(robots.text[:500] + ('...' if len(robots.text) > 500 else ''))
            else:
                st.warning("No se encontró archivo robots.txt")
        except:
            st.warning("No se pudo verificar robots.txt")

        try:
            sitemap_url = urljoin(base_url, "/sitemap.xml")
            sitemap = requests.get(sitemap_url, headers=HEADERS, timeout=5)
            if sitemap.status_code == 200:
                st.success("Archivo sitemap.xml encontrado:")
                st.code(sitemap.text[:500] + ('...' if len(sitemap.text) > 500 else ''))
            else:
                st.warning("No se encontró archivo sitemap.xml")
        except:
            st.warning("No se pudo verificar sitemap.xml")

    except RequestException as e:
        st.error(f"No se pudo acceder a la URL. Error: {e}")

# CTA final
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>✨ Esta herramienta fue creada con fines educativos y de asistencia a profesionales que están comenzando en SEO.</p>
        <p>💌 ¿Te sirvió? ¿Tenés alguna sugerencia? ¿Querés charlar sobre SEO, educación digital o IA aplicada? Escribime a <a href="mailto:florencia@crawla.agency">florencia@crawla.agency</a></p>
        <br>
        <a href="https://www.linkedin.com/in/festevez3005/" target="_blank">
            <button style="background-color:#4B8BBE; color:white; padding:10px 20px; font-size:16px; border:none; border-radius:6px; cursor:pointer;">
                🌐 Conectá conmigo en LinkedIn
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
