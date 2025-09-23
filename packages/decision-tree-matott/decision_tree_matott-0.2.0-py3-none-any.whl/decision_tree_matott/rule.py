#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Determinação de classe para regras em árvore ID3
class DecisionRuleID3:
    def __init__(self, attribute, information_gain, data, data_results, level):
        # Nome da coluna determinante
        self.attribute = attribute
        # Ganho de informação
        self.information_gain = information_gain
        # Matriz de dados usada
        self.data = data
        # Coluna de resultados usada
        self.data_results = data_results
        # Altura na árvore
        self.level = level
        
        # N de instancias na matriz
        self.data_n = len(data)
        # N de cada resultado da matriz (lista)
        # Se der errado fazer um for
        resultados = list(set(data_results))
        # Para cada valor em resultados, contar quantos tem e salvar em result_ns
        maior_frequencia = -1
        maior_resultado = ""
        self.result_ns = []
        for resultado in resultados:
            frequencia = 0
            for instancia in data_results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            if (frequencia > maior_frequencia):
                maior_frequencia = frequencia
                maior_resultado = resultado
            self.result_ns.append(Cell(resultado, frequencia))
        # Resultado predominante
        self.result = maior_resultado
        self.result_frequencia = maior_frequencia
        # Conexões com regras abaixo
        self.connections = []

    def __str__(self):
        resultados = ""
        for resultado in self.result_ns:
            resultados = resultados + "/'" + str(resultado.name) + "' " + str(resultado.frequency) + "/"
        return (f"{self.level} - {self.result} ({resultados}) | Informacao: {self.information_gain} | Regra derivada: {self.attribute}")
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Determinação de classe para regras em árvore C45
class DecisionRuleC45:
    def __init__(self, attribute, gain_ratio, data, data_results, level):
        # Nome da coluna determinante
        self.attribute = attribute
        # Ganho de informação
        self.gain_ratio = gain_ratio
        # Matriz de dados usada
        self.data = data
        # Coluna de resultados usada
        self.data_results = data_results
        # Altura na árvore
        self.level = level
        # Caso seja uma coluna de valor numérico,
        #  salvar o valor que provém maior ganho
        self.value = None
        
        # N de instancias na matriz
        self.data_n = len(data)
        # N de cada resultado da matriz (lista)
        # Se der errado fazer um for
        resultados = list(set(data_results))
        # Para cada valor em resultados, contar quantos tem e salvar em result_ns
        maior_frequencia = -1
        maior_resultado = ""
        self.result_ns = []
        for resultado in resultados:
            frequencia = 0
            for instancia in data_results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            if (frequencia > maior_frequencia):
                maior_frequencia = frequencia
                maior_resultado = resultado
            self.result_ns.append(Cell(resultado, frequencia))
        # Resultado predominante
        self.result = maior_resultado
        self.result_frequencia = maior_frequencia
        # Conexões com regras abaixo
        self.connections = []

    def __str__(self):
        resultados = ""
        for resultado in self.result_ns:
            resultados = resultados + "/" + str(resultado.name) + " " + str(resultado.frequency) + "/"
        return (f"{self.level} - {self.result} ({resultados}) | Razão de ganho: {self.gain_ratio} | Regra derivada: {self.attribute}")
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
class DecisionRuleCART:
    def __init__(self, attribute, gini, data, data_results, level):
        # Nome da coluna determinante
        self.attribute = attribute
        # Gini
        self.gini = gini
        # Matriz de dados usada
        self.data = data
        # Coluna de resultados usada
        self.data_results = data_results
        # Altura na árvore
        self.level = level
        # Salvar o valor da divisão binária
        self.value = None
        
        # N de instancias na matriz
        self.data_n = len(data)
        # N de cada resultado da matriz (lista)
        # Se der errado fazer um for
        resultados = list(set(data_results))
        # Para cada valor em resultados, contar quantos tem e salvar em result_ns
        maior_frequencia = -1
        maior_resultado = ""
        self.result_ns = []
        for resultado in resultados:
            frequencia = 0
            for instancia in data_results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            if (frequencia > maior_frequencia):
                maior_frequencia = frequencia
                maior_resultado = resultado
            self.result_ns.append(Cell(resultado, frequencia))
        # Resultado predominante
        self.result = maior_resultado
        self.result_frequencia = maior_frequencia
        # Conexões com regras abaixo
        self.connections = []

    def __str__(self):
        resultados = ""
        for resultado in self.result_ns:
            resultados = resultados + "/" + str(resultado.name) + " " + str(resultado.frequency) + "/"
        return (f"{self.level} - {self.result} ({resultados}) | Gini: {self.gini} | Regra derivada: {self.attribute}")
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Classes de suporte

# Conexão entre regras
class Connection:
    def __init__(self, result_name):
        self.result_name = result_name
        self.rule = None

# Célula
class Cell:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
