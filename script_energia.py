import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time

def capturar_pld():
    with sync_playwright() as p:
        # Abre o navegador
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Acessando CCEE (Painel de Preços)...")
        url = "https://www.ccee.org.br/en/web/guest/precos/painel-precos"
        
        try:
            # 1. Navega até a URL
            page.goto(url, wait_until="load", timeout=90000)
            
            # 2. O Power BI da CCEE fica dentro de iframes. 
            # Vamos esperar o frame principal do relatório aparecer.
            print("Aguardando os gráficos do Power BI...")
            page.wait_for_selector("iframe", timeout=60000)
            
            # 3. Dá um tempo generoso para o banco de dados da CCEE responder
            time.sleep(40) 
            
            # 4. Tenta capturar qualquer valor que pareça preço (formato XX,XX)
            # Vamos buscar por seletores de "visual" do Power BI
            content = page.content()
            
            # Buscamos por valores dentro das tags de texto do Power BI
            # O PLD geralmente está em elementos com a classe 'visual-card'
            card_values = page.locator(".cardValue, .visual-card").all_inner_texts()
            
            if not card_values:
                # Se não achou por classe, tenta por texto que contenha vírgula (preço)
                valor_pld = page.get_by_text(",").first.inner_text()
            else:
                valor_pld = card_values[0]

            status_captura = "Sucesso"
            print(f"Valor Extraído: {valor_pld}")

        except Exception as e:
            print(f"Erro: {e}")
            valor_pld = "0.00"
            status_captura = "Erro no Carregamento"

        browser.close()
        
        # Salvando para o seu DRE e Eficiência Logística
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dados = {
            "Data": [agora],
            "PLD_Valor": [valor_pld.replace("R$", "").strip()],
            "Status": [status_captura]
        }
        
        df = pd.DataFrame(dados)
        arquivo = 'historico_pld.csv'
        
        if os.path.isfile(arquivo):
            df.to_csv(arquivo, mode='a', index=False, header=False)
        else:
            df.to_csv(arquivo, index=False, header=True)
        
        print("Log atualizado no GitHub.")

if __name__ == "__main__":
    capturar_pld()