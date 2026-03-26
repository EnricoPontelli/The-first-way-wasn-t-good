import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time

def capturar_pld():
    with sync_playwright() as p:
        # Inicia o navegador (headless=True para o GitHub Actions)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Acessando o site da CCEE...")
        url = "https://www.ccee.org.br/en/web/guest/precos/painel-precos"
        page.goto(url, wait_until="networkidle")
        
        # O Power BI demora a carregar. Vamos esperar 15 segundos extras.
        time.sleep(15)
        
        # Tentativa de capturar o valor dentro dos cartões do Power BI
        # Nota: O seletor 'text' busca o valor que aparece na tela.
        try:
            # Procuramos por elementos que contenham valores de moeda (R$)
            # ou seletores específicos do dashboard
            valor_pld = page.locator('text=/R\$\s?\d+/').first.inner_text()
            print(f"Valor encontrado: {valor_pld}")
        except:
            valor_pld = "N/A"
            print("Não foi possível localizar o valor no tempo esperado.")

        browser.close()
        
        # Preparação dos dados para o seu DRE
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dados = {
            "Data": [agora],
            "PLD_Valor": [valor_pld.replace("R$", "").strip()],
            "Status": ["Fixos / sem danos" if valor_pld != "N/A" else "Erro"]
        }
        
        df = pd.DataFrame(dados)
        arquivo = 'historico_pld.csv'
        
        # Salva mantendo o histórico
        if os.path.isfile(arquivo):
            df.to_csv(arquivo, mode='a', index=False, header=False)
        else:
            df.to_csv(arquivo, index=False, header=True)
        
        print("Dados salvos no CSV.")

if __name__ == "__main__":
    capturar_pld()