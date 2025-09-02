from flask import Flask, render_template, request
from markupsafe import escape
import math

app = Flask(__name__)

def to_float(val, default=0.0):
    if val is None or str(val).strip() == "":
        return float(default)
    try:
        s = str(val).replace(",", ".")
        return float(s)
    except Exception:
        return float(default)

def conta_trilhos(valor):
    if valor <= 40:
        return 0
    for n in range(1, 7):
        if ((valor - (n * 3)) / (n + 1)) <= 40:
            return n + 1
    return 0

def calcular_componentes(dados):
    porta = dados.get("porta", "Simples")
    altura_total = to_float(dados.get("altura", 0))
    largura_porta = to_float(dados.get("largura", 0))
    profundidade_total = to_float(dados.get("profundidade", 0))
    altura_boca = to_float(dados.get("altura_boca", 70))
    pedra = dados.get("pedra", "Não")
    vidro = dados.get("vidro", "Não")

    altura_metalon_inox = 75  # Valor fixo, removido do formulário
    entrada_placa = 5         # Valor fixo, removido do formulário

    # -------------------------
    # Metalon Galvanizado 4x4
    # -------------------------
    if porta == "Simples":
        mg44 = 0
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        mg44 = 3 * (altura_total - altura_boca - 2) / 100
    elif porta == "Em U":
        mg44 = 4 * (altura_total - altura_boca - 2) / 100
    else:
        mg44 = 0

    # -------------------------
    # Metalon Galvanizado 4x2
    # -------------------------
    if porta == "Simples":
        mg42 = largura_porta / 100
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        mg42 = (largura_porta + (profundidade_total - 7)) / 100
    elif porta == "Em U":
        mg42 = (largura_porta + 2 * (profundidade_total - 7)) / 100
    else:
        mg42 = 0

    # -------------------------
    # Metalon Galvanizado 3x2
    # -------------------------
    valor_trilhos = altura_total - 11 - altura_boca
    qt_trilhos = conta_trilhos(valor_trilhos)
    if porta == "Simples":
        mg32 = largura_porta * qt_trilhos / 100
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        mg32 = (largura_porta + (profundidade_total - 11)) * qt_trilhos / 100
    elif porta == "Em U":
        mg32 = (largura_porta + 2 * (profundidade_total - 11)) * qt_trilhos / 100
    else:
        mg32 = 0

    # -------------------------
    # Metalon Inox 4x4
    # -------------------------
    if porta == "Simples":
        mi44 = 0
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        mi44 = (3 * altura_metalon_inox + 2 * (profundidade_total - 11)) / 100
    elif porta == "Em U":
        mi44 = (6 * altura_metalon_inox + 4 * (profundidade_total - 11)) / 100
    else:
        mi44 = 0

    # -------------------------
    # Metalon Inox 3x2
    # -------------------------
    if porta == "Simples":
        mi32 = largura_porta / 100
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        mi32 = (largura_porta + (profundidade_total - 11)) / 100
    elif porta == "Em U":
        mi32 = (largura_porta + 2 * (profundidade_total - 11)) / 100
    else:
        mi32 = 0

    # -------------------------
    # Baguete Inox 1.5x1.5
    # -------------------------
    base_baguete_unit = 75 if pedra == "Sim" else 72.5
    if porta == "Simples":
        baguete = (4*65 + 4*base_baguete_unit)/100
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        baguete = (4*65 + 4*base_baguete_unit + 2*(altura_boca - 8) + 2*(profundidade_total - 14))/100
    elif porta == "Em U":
        baguete = (4*65 + 4*base_baguete_unit + 4*(altura_boca - 8) + 4*(profundidade_total - 14))/100
    else:
        baguete = 0

    # -------------------------
    # Metalon Inox 4x2
    # -------------------------
    mi42 = 2 * altura_total / 100 if porta == "Simples" else 0

    # -------------------------
    # Placa Cimentícia (m²)
    # -------------------------
    altura_util = altura_total - altura_boca + entrada_placa
    if porta == "Simples":
        placa = (largura_porta/100) * (altura_util/100)
    elif porta in ["Em L Esquerda", "Em L Direita"]:
        placa = (largura_porta/100)*(altura_util/100) + ((profundidade_total - 1)/100)*(altura_util/100)
    elif porta == "Em U":
        placa = (largura_porta/100)*(altura_util/100) + 2*((profundidade_total - 1)/100)*(altura_util/100)
    else:
        placa = 0

    # -------------------------
    # Vidro (m²)
    # -------------------------
    if vidro == "Não":
        vidro_area = 0
    else:
        altura_vidro_frontal = altura_boca + 5
        if porta == "Simples":
            largura_vidro_frontal = largura_porta - 4.5
            altura_vidro_lat = 0
            largura_vidro_lat = 0
            multiplicador = 0
        elif porta in ["Em L Esquerda", "Em L Direita"]:
            largura_vidro_frontal = largura_porta - 8.5
            altura_vidro_lat = altura_boca - 8.5
            largura_vidro_lat = profundidade_total - 11.5
            multiplicador = 1
        elif porta == "Em U":
            largura_vidro_frontal = largura_porta - 8.5
            altura_vidro_lat = altura_boca - 8.5
            largura_vidro_lat = profundidade_total - 11.5
            multiplicador = 2
        else:
            largura_vidro_frontal = 0
            altura_vidro_lat = 0
            largura_vidro_lat = 0
            multiplicador = 0

        vidro_area = (altura_vidro_frontal/100) * (largura_vidro_frontal/100)
        vidro_area += multiplicador * (altura_vidro_lat/100) * (largura_vidro_lat/100)

    # -------------------------
    # Arredondamento para 2 casas decimais sempre para cima
    # -------------------------
    def ceil2(x):
        return math.ceil(x*100)/100

    return {
        "Metalon Galv. 4x4": ceil2(max(0, mg44)),
        "Metalon Galv. 4x2": ceil2(max(0, mg42)),
        "Metalon Galv. 3x2": ceil2(max(0, mg32)),
        "Metalon Inox 4x4": ceil2(max(0, mi44)),
        "Metalon Inox 3x2": ceil2(max(0, mi32)),
        "Baguete Inox 1.5x1.5": ceil2(max(0, baguete)),
        "Metalon Inox 4x2": ceil2(max(0, mi42)),
        "Placa Cimentícia/m²": ceil2(max(0, placa)),
        "Vidro": ceil2(max(0, vidro_area)),
    }

def calcular_custo_total(dados):
    precos = {
        "Metalon Galv. 4x4": 20,
        "Metalon Galv. 4x2": 15,
        "Metalon Galv. 3x2": 13,
        "Metalon Inox 4x4": 45,
        "Metalon Inox 3x2": 30,
        "Baguete Inox 1.5x1.5": 20,
        "Metalon Inox 4x2": 35,
        "Placa Cimentícia/m²": 60,
        "Vidro": 500,
    }

    quantidades = calcular_componentes(dados)
    custo_total = 0.0
    detalhamento = []

    for item, qtd in quantidades.items():
        preco = precos.get(item, 0)
        custo = qtd * preco
        custo_total += custo
        detalhamento.append({
            "item": item,
            "quantidade": qtd,
            "preco_unit": preco,
            "custo": custo
        })

    # -------------------------
    # Novos cálculos de custos solicitados
    # -------------------------
    porta = dados.get("porta", "Simples")
    largura_porta = to_float(dados.get("largura", 0))
    altura_boca = to_float(dados.get("altura_boca", 70))
    vidro = dados.get("vidro", "Não")

    # Cálculo da área frontal do vidro (m²) — será usada apenas para contrapeso
    frontal_area_m2 = 0.0
    if vidro != "Não":
        altura_vidro_frontal = altura_boca + 5
        if porta == "Simples":
            largura_vidro_frontal = largura_porta - 4.5
        elif porta in ["Em L Esquerda", "Em L Direita"]:
            largura_vidro_frontal = largura_porta - 8.5
        elif porta == "Em U":
            largura_vidro_frontal = largura_porta - 8.5
        else:
            largura_vidro_frontal = 0

        largura_vidro_frontal = max(0, largura_vidro_frontal)
        frontal_area_m2 = (altura_vidro_frontal/100) * (largura_vidro_frontal/100)

    # Mão de obra
    mao_map = {
        "Simples": 780,
        "Em L Esquerda": 1080,
        "Em L Direita": 1080,
        "Em U": 1380,
    }
    mao_valor = mao_map.get(porta, 0)

    # Consumíveis (fixo)
    consumiveis_valor = 50

    # Deslocação (fixo)
    deslocacao_valor = 100

    # Contrapeso (apenas vidro frontal) R$300 / m²
    contrapeso_unit = 300
    contrapeso_valor = frontal_area_m2 * contrapeso_unit

    # Revestimento
    revest_base_map = {
        "Simples": 40,
        "Em L Esquerda": 80,
        "Em L Direita": 80,
        "Em U": 120,
    }
    revest_base = revest_base_map.get(porta, 0)
    revestimento_valor = revest_base + 1 * largura_porta

    # Parafusos
    parafusos_map = {
        "Simples": 20,
        "Em L Esquerda": 40,
        "Em L Direita": 40,
        "Em U": 60,
    }
    parafusos_valor = parafusos_map.get(porta, 0)

    # Adiciona ao total e detalhamento
    adicionais = [
        ("Mão de obra", 1, mao_valor, mao_valor),
        ("Consumíveis", 1, consumiveis_valor, consumiveis_valor),
        ("Deslocação", 1, deslocacao_valor, deslocacao_valor),
        ("Contrapeso (vidro frontal)", frontal_area_m2, contrapeso_unit, contrapeso_valor),
        ("Revestimento", 1, revestimento_valor, revestimento_valor),
        ("Parafusos", 1, parafusos_valor, parafusos_valor),
    ]

    for nome, qtd, unit, custo in adicionais:
        # garantir números válidos
        qtd = float(qtd)
        unit = float(unit)
        custo = float(custo)
        custo_total += custo
        detalhamento.append({
            "item": nome,
            "quantidade": qtd,
            "preco_unit": unit,
            "custo": custo
        })

    return custo_total, detalhamento

# -------------------------
# Rotas
# -------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", resultado=None, dados={})

@app.route("/calcular", methods=["POST"])
def calcular():
    dados = request.form.to_dict()
    try:
        custo_total, detalhamento = calcular_custo_total(dados)
    except Exception as e:
        return render_template("index.html", resultado={
            "erro": True,
            "mensagem": f"Erro ao calcular: {escape(str(e))}"
        }, dados=dados)

    def fmt(val):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    resumo = {
        "custo_total": custo_total,
        "custo_total_fmt": fmt(custo_total),
        "detalhamento": [
            {
                "item": d["item"],
                "quantidade": f"{d['quantidade']:.2f}",
                "preco_unit": f"R$ {d['preco_unit']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "custo": f"R$ {d['custo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            } for d in detalhamento
        ]
    }

    return render_template("index.html", resultado=resumo, dados=dados)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define a porta
    app.run(host="0.0.0.0", port=port, debug=True)
