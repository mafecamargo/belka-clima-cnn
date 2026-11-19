# Belka · Painel do clima

Olhar longe. Proteger perto.

Dashboard interativo que (1) usa uma rede neural convolucional (CNN) para dizer qual evento climático aparece em uma imagem, (2) consulta em tempo real os avisos e a previsão do INMET para uma cidade e (3) mostra as precauções para cada evento.

## Integrantes:
- Fernanda Kaory Saito RM551104
- João Pedro Borsato da Cruz RM550294
- Maria Fernanda Vieira de Camargo RM97956
- Pedro Lucas de Andrade Nunes RM550366

## Link da demonstração no YouTube: 


## O que tem na pasta

| Caminho | O que é |
|---|---|
| `dashboard/index.html` | O painel. Abra com dois cliques. Abas: Pesquisar, Tempo real, Precauções. |
| `dashboard/belkanet.js` | A CNN em JavaScript (só a inferência), usada na aba Pesquisar. |
| `dashboard/precaucoes.js` | Base de eventos e precauções, por nível de alerta. |
| `dashboard/modelo.js` | Pesos e métricas do modelo treinado. Gerado pelo passo 2. |
| `cnn/1_coletar_imagens.py` | Passo 1: baixa as imagens de treino para `dataset/`. |
| `cnn/2_treinar_cnn.py` | Passo 2: treina, testa e exporta a CNN. |
| `cnn/belkanet.py` | A CNN (BelkaNet) escrita em NumPy: camadas, perda e otimizador. |
| `dataset/` | Imagens por classe e `fontes.csv`. Criada pelo passo 1. |

## Como rodar

```bash
cd ~/Documents/belka-clima
python3 cnn/1_coletar_imagens.py      # ~2.300 miniaturas, ~60 MB, 10 a 15 minutos
python3 cnn/2_treinar_cnn.py          # precisa de numpy e Pillow; ~10 minutos
open dashboard/index.html
```

As abas Tempo real e Precauções funcionam sem o modelo. A aba Pesquisar passa a classificar imagens depois do passo 2.

## Imagens de treino

Fotografias em domínio público feitas por órgãos do governo dos EUA: FEMA, NOAA, USGS, Serviço Florestal, Serviço de Parques, BLM, USDA e FWS. São buscadas pela API do Wikimedia Commons, que guarda cópia dessas fotos com o órgão e a licença marcados. Os acervos originais não permitem coleta automática: o photolib.noaa.gov exige verificação humana, e a busca de imagens da NASA devolve principalmente cenas de satélite e de outros planetas para estes termos. Cada imagem baixada fica registrada em `dataset/fontes.csv` com título, órgão, licença e link.

Classes: enchente, deslizamento, incêndio, tempestade (raios), tornado, seca e neve. O rótulo vem do título do arquivo, com filtros que descartam mapas, gráficos, retratos e cerimônias. Alguns rótulos errados ainda passam; vale abrir as pastas e apagar o que não for foto do evento antes de treinar.

## A CNN (BelkaNet)

Baseada na MeteCNN de Xiao et al. (2021), em versão pequena para treinar em CPU:

- entrada 64×64 RGB, normalizada pela média e desvio do conjunto de treino;
- 4 blocos de convolução 3×3 + ReLU (16, 32, 64 e 96 filtros), com max-pooling entre eles;
- global average pooling no lugar de camadas totalmente conectadas, e classificador softmax;
- cerca de 79 mil parâmetros.

Protocolo, como no artigo: divisão 8:1:1 em treino, validação e teste; aumento de dados com recorte aleatório e espelhamento; weight decay 5e-4; taxa de aprendizado cortada pela metade quando a perda de validação para de cair por 5 épocas; o modelo com melhor acurácia de validação vai para o teste; métricas de acurácia, precisão, recall e F1 por classe e em macro-média, mais a matriz de confusão. Diferenças: a rede é bem menor que a MeteCNN (13 convoluções, 224×224), não usa SE nem convolução dilatada, e o otimizador é Adam em vez de SGD com momento.

## Tempo real

- Avisos: `https://apiprevmet3.inmet.gov.br/avisos/ativos` (INMET). O painel filtra pelo código IBGE da cidade.
- Previsão: `.../previsao/{codigo}`. Condição atual: `.../estacao/proxima/{codigo}`.
- Estados e cidades: API de localidades do IBGE.

A severidade do INMET vira o nível da Belka: perigo potencial = Fique de olho, perigo = Prepare-se, grande perigo = Aja agora. Sem aviso oficial, o painel aponta sinais da previsão (trovoadas, pancadas de chuva, máxima a partir de 35 °C, mínima até 5 °C, umidade até 30%) e deixa claro que não são avisos do INMET.

## Marca

Cores, tipografia (Space Grotesk e Atkinson Hyperlegible), escala de alerta, tom de voz e telefones seguem o Manual de marca da Belka v1.0.

## Referências

- Xiao, H. et al. (2021). Classification of Weather Phenomenon From Images by Using Deep Convolutional Neural Network. Earth and Space Science, 8. doi:10.1029/2020EA001604
- Bhosale, Y. H. (2026). AI-Driven Meteorology for Weather Detection, Classification, Nowcasting and Forecasting (1991–2025). National Academy Science Letters. doi:10.1007/s40009-026-02154-2
