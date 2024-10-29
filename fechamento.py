import pandas as pd
import streamlit as st

# Adicionar um título ao aplicativo
st.title("Análise de Reclamações Mensais")

# Solicitar ao usuário que faça upload do arquivo CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    # Carregar o arquivo CSV
    df = pd.read_csv(uploaded_file, delimiter=";")

    # Renomear a coluna 'mês' para 'mes'
    if 'mês' in df.columns:
        df.rename(columns={'mês': 'mes'}, inplace=True)

    # Dicionário para mapear meses abreviados para nomes completos
    meses_completos = {
        'jan': 'janeiro',
        'fev': 'fevereiro',
        'mar': 'março',
        'abr': 'abril',
        'mai': 'maio',
        'jun': 'junho',
        'jul': 'julho',
        'ago': 'agosto',
        'set': 'setembro',
        'out': 'outubro',
        'nov': 'novembro',
        'dez': 'dezembro'
    }

    # Converter os valores da coluna mes para minúsculas e substituir os meses abreviados pelos nomes completos
    df['mes'] = df['mes'].str.lower().map(meses_completos)

    # Verificar se houve algum valor NaN após a conversão
    #st.write("Valores após conversão:", df['mes'].unique())

    # Filtrar ano
    ano_atual = st.selectbox('Selecione o ano atual', df['ano'].unique())

    # Filtrar mês atual e anterior
    mes_atual = st.selectbox('Selecione o mês atual', df['mes'].unique())
    mes_anterior = st.selectbox('Selecione o mês anterior', df['mes'].unique())

    # Filtro para o mês atual e anterior
    df_atual = df[(df['mes'] == mes_atual) & (df['ano'] == ano_atual)]
    df_anterior = df[(df['mes'] == mes_anterior) & (df['ano'] == ano_atual)]

    # Filtros por canal (geral, procon e sem procon)
    canal_opcao = st.selectbox('Selecione o canal', ['Todos', 'PROCON', 'OUVIDORIA'])

    if canal_opcao == 'PROCON':
        df_atual = df_atual[df_atual['DS_CANAL'] == 'PROCON']
        df_anterior = df_anterior[df_anterior['DS_CANAL'] == 'PROCON']
    elif canal_opcao == 'OUVIDORIA':
        df_atual = df_atual[df_atual['DS_CANAL'] != 'PROCON']
        df_anterior = df_anterior[df_anterior['DS_CANAL'] != 'PROCON']

    # Calcular a variação total de reclamações
    total_atual_geral = df_atual.shape[0]
    total_anterior_geral = df_anterior.shape[0]

    variacao_percentual_geral = ((total_atual_geral - total_anterior_geral) / total_anterior_geral * 100) if total_anterior_geral != 0 else 0

    # Exibir análise geral
    if variacao_percentual_geral > 0:
        st.write(f"No geral, tivemos um aumento de **{variacao_percentual_geral:.2f}%** nas reclamações ao comparar **{mes_anterior.capitalize()}** com **{mes_atual.capitalize()}**.")
    else:
        st.write(f"No geral, tivemos uma redução de **{-variacao_percentual_geral:.2f}%** nas reclamações ao comparar **{mes_anterior.capitalize()}** com **{mes_atual.capitalize()}**.")

    # Análise por Diretoria
    diretorias = df['Diretoria'].unique()

    for diretoria in diretorias:
        st.write(f"## Diretoria: {diretoria}")
        
        # Total de reclamações acumuladas até o mês atual para a diretoria e total geral
        meses_ate_atual = list(meses_completos.values())[:list(meses_completos.values()).index(mes_atual) + 1]
        
        total_acumulado_diretoria = df[
            (df['ano'] == ano_atual) &
            (df['Diretoria'] == diretoria) &
            (df['mes'].isin(meses_ate_atual))
        ].shape[0]
        
        total_acumulado_geral = df[
            (df['ano'] == ano_atual) &
            (df['mes'].isin(meses_ate_atual))
        ].shape[0]

        # Cálculo de representatividade da diretoria
        porcentagem_diretoria = (total_acumulado_diretoria / total_acumulado_geral) * 100 if total_acumulado_geral != 0 else 0
        
        st.write(f"Neste ano, até **{mes_atual.capitalize()}**, a Diretoria {diretoria} representa **{porcentagem_diretoria:.2f}%** do total de reclamações acumuladas. Isso nos dá uma ideia clara do impacto dessa diretoria no cenário geral.")

        # Total de reclamações no mês atual e anterior
        total_atual = df_atual[df_atual['Diretoria'] == diretoria].shape[0]
        total_anterior = df_anterior[df_anterior['Diretoria'] == diretoria].shape[0]
        
        # Variação percentual
        variacao_percentual = ((total_atual - total_anterior) / total_anterior) * 100 if total_anterior != 0 else 0
        
        # Explicação da variação de reclamações
        mes_atual_nome = mes_atual.capitalize()
        mes_anterior_nome = mes_anterior.capitalize()

        if variacao_percentual > 0:
            st.write(f"\nNo mês de **{mes_atual_nome}**, observamos um aumento de **{variacao_percentual:.2f}%** nas reclamações, passando de **{total_anterior}** em **{mes_anterior_nome}** para **{total_atual}** em **{mes_atual_nome}**. Isso indica uma piora na situação, que merece nossa atenção.")
        else:
            st.write(f"\nNo mês de **{mes_atual_nome}**, observamos uma queda de **{-variacao_percentual:.2f}%** nas reclamações, reduzindo de **{total_anterior}** em **{mes_anterior_nome}** para **{total_atual}** em **{mes_atual_nome}**. Isso é um sinal positivo e indica que estamos avançando na resolução dos problemas.")

        # Comparar as naturezas entre os dois meses
        naturezas_atual = df_atual[df_atual['Diretoria'] == diretoria]['Natureza'].value_counts()
        naturezas_anterior = df_anterior[df_anterior['Diretoria'] == diretoria]['Natureza'].value_counts()

        # Juntando os dados de ambos os meses para calcular a variação por natureza
        df_naturezas = pd.DataFrame({'Atual': naturezas_atual, 'Anterior': naturezas_anterior}).fillna(0)
        df_naturezas['Variação'] = df_naturezas['Atual'] - df_naturezas['Anterior']

        # Ordenar as naturezas por maior variação absoluta
        df_naturezas = df_naturezas.sort_values(by='Variação', ascending=False, key=abs)

        # Selecionar as 3 naturezas mais relevantes (maior variação)
        naturezas_relevantes = df_naturezas.head(3)

        # Loop para exibir até 3 naturezas mais relevantes
        for index, row in naturezas_relevantes.iterrows():
            total_natureza_atual = row['Atual']
            total_natureza_anterior = row['Anterior']
            variacao_natureza = row['Variação']
            variacao_percentual_natureza = (variacao_natureza / total_natureza_anterior) * 100 if total_natureza_anterior != 0 else 0
            
            if variacao_natureza > 0:
                st.write(f"\nA natureza **'{index}'** apresentou uma piora significativa, com um aumento de **{variacao_percentual_natureza:.2f}%**, passando de **{total_natureza_anterior}** para **{total_natureza_atual}**.")
            elif variacao_natureza < 0:
                st.write(f"\nA natureza **'{index}'** melhorou consideravelmente, com uma diminuição de **{-variacao_percentual_natureza:.2f}%**, reduzindo de **{total_natureza_anterior}** para **{total_natureza_atual}**.")
            else:  # Quando não há variação (empate)
                st.write(f"\nA natureza **'{index}'** não teve variação, mantendo-se em **{total_natureza_anterior}**.")

            # Identificar os motivos dentro da natureza
            motivos_atual = df_atual[(df_atual['Natureza'] == index) & (df_atual['Diretoria'] == diretoria)]['Motivo'].value_counts()
            motivos_anterior = df_anterior[(df_anterior['Natureza'] == index) & (df_anterior['Diretoria'] == diretoria)]['Motivo'].value_counts()

            # Juntando os dados de ambos os meses para os motivos
            df_motivos = pd.DataFrame({'Atual': motivos_atual, 'Anterior': motivos_anterior}).fillna(0)
            df_motivos['Variação'] = df_motivos['Atual'] - df_motivos['Anterior']

            # Ordenar os motivos por maior variação absoluta
            df_motivos = df_motivos.sort_values(by='Variação', ascending=False, key=abs)

            # Exibir os 3 principais motivos com maior variação
            st.write(f"\nMotivos relacionados à natureza **'{index}'**:")
            for motivo_index, motivo_row in df_motivos.head(3).iterrows():
                total_motivo_atual = motivo_row['Atual']
                total_motivo_anterior = motivo_row['Anterior']
                variacao_motivo = motivo_row['Variação']
                
                if variacao_motivo > 0:
                    st.write(f"- O motivo '{motivo_index}' piorou, aumentando de **{total_motivo_anterior}** para **{total_motivo_atual}**.")
                elif variacao_motivo < 0:
                    st.write(f"- O motivo '{motivo_index}' melhorou, reduzindo de **{total_motivo_anterior}** para **{total_motivo_atual}**.")
                else:  # Quando não há variação (empate)
                    st.write(f"- O motivo '{motivo_index}' não teve variação, mantendo-se em **{total_motivo_anterior}**.")
