import pandas as pd
import os

def limpar_eurostat(nome_ficheiro):
    # Caminhos
    caminho_entrada = f'../data_raw/{nome_ficheiro}'
    caminho_saida = f'../data_clean/{nome_ficheiro.replace(".tsv", ".csv")}'
    
    print(f"A processar: {nome_ficheiro}...")
    
    # 1. Ler o ficheiro TSV
    df = pd.read_csv(caminho_entrada, sep='\t')
    
    # 2. Separar a primeira coluna (ex: freq,unit,geo\TIME_PERIOD)
    col_cabecalho = df.columns[0]
    # Extrair as categorias e o nome da coluna geográfica
    categorias = col_cabecalho.split('\\')[0].split(',')
    
    # Criar novas colunas baseadas no split do primeiro campo
    df[categorias] = df[col_cabecalho].str.split(',', expand=True)
    
    # 3. Transformar de "Largo" para "Longo" (Anos em colunas para Anos em linhas)
    anos = [c for c in df.columns if any(char.isdigit() for char in c)]
    id_vars = categorias # ex: ['freq', 'unit', 'geo']
    
    df_longo = df.melt(id_vars=id_vars, value_vars=anos, var_name='Ano', value_name='Valor')
    
    # 4. Limpeza Crítica (Remover : , letras de observação u, b, p, e e espaços)
    df_longo['Valor'] = df_longo['Valor'].astype(str).str.replace(r'[a-zA-Z\s:]', '', regex=True)
    
    # Converter para numérico (o que for vazio vira NaN)
    df_longo['Valor'] = pd.to_numeric(df_longo['Valor'], errors='coerce')
    
    # Remover linhas sem dados para o dashboard não ficar com buracos
    df_longo = df_longo.dropna(subset=['Valor'])
    
    # 5. Guardar
    df_longo.to_csv(caminho_saida, index=False)
    print(f"Sucesso! Guardado em: {caminho_saida}")

# Executar para os ficheiros principais que selecionámos
ficheiros_para_limpar = [
    'estat_tsc00005.tsv', # Mulheres na Ciência (Inclusão)
    'estat_tgs00042.tsv'  # Investimento Regional (Inovação)
]

# Criar pasta data_clean se não existir
if not os.path.exists('../data_clean'):
    os.makedirs('../data_clean')

for f in ficheiros_para_limpar:
    try:
        limpar_eurostat(f)
    except Exception as e:
        print(f"Erro ao limpar {f}: {e}")