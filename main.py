import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import trafilatura
import smtplib # Biblioteca nativa de email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CARREGAMENTO DO .ENV ---
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

def search_web(topic):
    """Busca notícias usando o RSS do Bing."""
    print(f"🔎 Consultando Bing News RSS para: {topic}...")
    rss_url = f"https://www.bing.com/news/search?q={topic}&format=rss&setmkt=pt-BR"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        results = []
        for item in items[:5]:
            results.append({'title': item.title.text, 'href': item.link.text})
            
        print(f"   ✅ Encontrados {len(results)} links no Bing.")
        return results
    except Exception as e:
        print(f"❌ Erro ao baixar RSS: {e}")
        return []

def scrape_content(url):
    """Usa Trafilatura para extrair apenas o texto útil"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None: return ""
        text = trafilatura.extract(downloaded, include_comments=False)
        return text[:10000] if text and len(text) > 100 else ""
    except Exception:
        return ""

def send_email(html_content):
    """Envia o email usando SMTP do Gmail"""
    sender = os.getenv("EMAIL_FROM")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_TO")

    if not sender or not password or not receiver:
        print("❌ Credenciais de email não configuradas no .env")
        return

    print("📧 Enviando email...")
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"Resumo Tech Diário - {datetime.now().strftime('%d/%m/%Y')}"

    # Anexa o corpo em HTML
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Conecta ao servidor do Gmail (porta 587 é a padrão segura)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Criptografa a conexão
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("✅ Email enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")

def generate_newsletter():
    print("\n🤖 Iniciando o Agente de Notícias...")
    
    topic = os.getenv("TOPIC", "tecnologia")
    links = search_web(topic)
    
    if not links: return

    context = ""
    print("📖 Lendo conteúdos...")
    for item in links:
        content = scrape_content(item['href'])
        if content:
            print(f"     ✅ Lido: {item['title'][:30]}...")
            context += f"\n\nFONTE: {item['title']}\nLINK: {item['href']}\nCONTEÚDO: {content}"
    
    if not context:
        print("❌ Nenhuma notícia lida.")
        return

    print("\n🧠 Enviando para o Gemini processar...")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prompt alterado para retornar HTML direto
    prompt = f"""
    Você é um editor de Newsletter sobre {topic}.
    Use os textos abaixo para criar um resumo.
    
    TEXTOS:
    {context}
    
    IMPORTANTE:
    - Retorne APENAS o código HTML (sem ```html no inicio, apenas o código cru).
    - Use tags <h2> para titulos, <p> para texto e <a> para links.
    - Deixe o design limpo e fácil de ler.
    - No final, coloque uma frase engraçada de despedida.
    """
    
    try:
        response = model.generate_content(prompt)
        html_output = response.text.replace("```html", "").replace("```", "") # Limpeza de segurança
        
        # Envia o email com o resultado
        send_email(html_output)
        
    except Exception as e:
        print(f"❌ Erro no Gemini: {e}")

if __name__ == "__main__":
    generate_newsletter()