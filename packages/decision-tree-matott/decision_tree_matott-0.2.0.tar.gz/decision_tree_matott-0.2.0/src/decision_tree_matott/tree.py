import pandas as pd
import math
#from . import rule
import rule

# Receber matriz completa de dados
def data_classification(data):
    # Separar matriz de dados em treino e teste
    train_data = data
    test_data = data
    # Separar coluna de resultados
    train_data = train_data
    train_result = train_data
    test_data = test_data
    test_result = test_data

def teste(valor):
    print(f"Testando {valor}")

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Criação do objeto

class ID3:
    # Criar árvore
    def __init__ (self, max_height, min_information, results):
        # Altura máxima
        # -1 significa que não tem máximo
        self.max_height = max_height
        self.current_height = 0
        # Regras para o ganho de informação
        self.min_information = min_information
        # Contar na coluna de resultados quantos há
        self.results_list = list(set(results))
        self.results_n = len(list(set(results)))
        # Definir raiz
        self.root = None
        # Teste
        #print(f"Criado árvore altura máxima {self.max_height}, informação mínima {self.min_information} com {self.results_n} tipos de resultados")

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Montagem da árvore

    # Montar árvore
    def create_tree(self, data, result):
        # Chamar método de montagem da árvore para a raiz
        self.root = self.define_rule(self.root, data, result, 0)

    # Método para montagem de árvore
    def define_rule(self, current_rule, data, result, level):
        # Chamar método de determinação de atributo e salvar regra de montagem
        #print(level)
        regra_resultante = self.define_attribute(data, result, level)
        #print(regra_resultante)
        #print("-     -------------------     -")
        #current_rule = regra_resultante
        # Se retorno tiver sido nulo ou ganho de informação for 0, parar
        # Retorno nulo significa que o ganho na regra não foi suficiente
        # Ganho de informação 0 implica que não há mais informação a ser extraída da árvore
        if ( (regra_resultante != None) and (regra_resultante.information_gain != 0.0) ):
            if level > self.current_height:
                self.current_height = level
            # Se ainda não tiver chegado no limite de altura 
            if ( (level < self.max_height) or (self.max_height == -1) ):
                # Para cada ramo, chamar método de montagem da árvore
                for ramo in regra_resultante.connections:
                        # Uma forma mais eficiente é adicionar quando corresponder ao critério
                        # ao invés de remover quando não corresponder, mas não sei implementar isso
                    # Tabela completa para remover atributos que não encaixarem
                    data_branch = data
                    result_branch = result
                    # Remover dados não pertencentes ao ramo
                    for row in data.index:
                        if data[regra_resultante.attribute][row] != ramo.result_name:
                            data_branch = data_branch.drop(index=row)
                            result_branch = result_branch.drop(index=row)
                    # Chamar método de montagem da regra
                    #print("\n\n"); #print(data_branch)
                    #print("\n");   #print(result_branch); #print("\n\n")
                    ramo.rule = self.define_rule(ramo.rule, data_branch, result_branch, level+1)
        return regra_resultante

    # Método de determinação de atributo (recebendo dados e resultados de treino)
    def define_attribute(self, data_unformatted, results, level):
        #print (f"define attribute level {level}\n")
        # Formatar dados para melhor uso
        data = pd.DataFrame(data_unformatted)
        #results = pd.DataFrame(results_unformatted)
        #print(results)
        #print(type(results))
        # Número de linhas
        n_instancias = len(data)
        #print(f"n_instancias: {n_instancias}")
        resultados_distintos = list(set(results))
        #print(resultados_distintos)
        n_resultados = len(list(set(results)))
        #print(f"n_instancias: {n_instancias} e n_resultados: {n_resultados}")

        # Caso só haja um resultado distinto, não é necessário determinar uma regra
        if n_resultados == 1:
            regra = rule.DecisionRuleID3('(Final)', 1.0, data, results, level)
            return regra

        # Cálculo da entropia da classe
        entropia_classe = 0
        for resultado in resultados_distintos:
            frequencia = 0
            for instancia in results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            #print(f"frequencia: {frequencia} | n_instancias: {n_instancias} | n_resultados: {n_resultados}")
            freq_div_instancias = (frequencia * 1.0)/(n_instancias * 1.0)
            #print(f"Cálculo de entropia de classe: {freq_div_instancias}, {n_resultados}")
            entropia_atual = freq_div_instancias * (math.log(freq_div_instancias, n_resultados))
            entropia_classe = entropia_classe + entropia_atual
        entropia_classe = entropia_classe * (-1)
        # Criar lista separada para contabilizar ganho de informação em cada coluna
        attributes_gain = []
        # Loop de for para cada coluna
        #data_formatted = pd.DataFrame(data)
        #num_columns = data_formatted.shape[1]
        for column in data.columns:
            #print(f"coluna atual: {column}")
            ganho = entropia_classe
            # Contar quantas entradas diferentes há na coluna
            #print(data[column])
            #print(type(data[column]))
            entradas = len(list(set(data[column])))
            # Variável do somatório
            somatorio = 0
            # Cálculo de entropia
            # Para cada entrada possível
            for entrada in list(set(data[column])):
                soma = 0
                frequencia_entrada = 0
                # Contabilizar instancias da entrada
                for instancia in data[column]:
                    if ( (instancia == entrada) ):
                        frequencia_entrada = frequencia_entrada + 1
                # Contabilizar quantos número em cada resultado
                for resultado in resultados_distintos:
                    frequencia = 0
                    #print(f"entrada: {entrada} e resultado: {resultado}")
                    for instancia in data.index:
                        #print(data[column][instancia])
                        #print(results[instancia])
                        if ( (data[column][instancia] == entrada) & (results[instancia] == resultado) ):
                            frequencia = frequencia + 1
                    # Probabilidade do resultado * Log 2 da probabilidade
                    # Somar ao dos demais resultados
                    #print(f"frequencia: {frequencia} | frequencia_entrada: {frequencia_entrada} | n_resultados: {n_resultados}")
                    # Se a frequência for zero, efetivamente somamos 0, o que significa nada
                    if frequencia != 0:
                        freq_div_freqentrada = (frequencia * 1.0)/(frequencia_entrada * 1.0)
                        entropia_atual = freq_div_freqentrada * (math.log(freq_div_freqentrada, n_resultados))
                        soma = soma + entropia_atual
                # Multiplicar por -1 (correção devido a como log funciona)
                soma = soma * (-1)
                # Multiplicar pelo n de ocorrencia da entrada e dividir pelo n total
                soma = soma * ( (frequencia_entrada * 1.0) / (n_instancias * 1.0) )
                # Somar resultado ao somatório
                #print(f"somatorio: {somatorio} e soma: {soma}")
                somatorio = somatorio + soma
                #print(f"somatorio novo: {somatorio}")
            # Ganho = 1 - Somatório
            ganho = ganho - somatorio
            #print(f"somatorio final: {somatorio} e ganho: {ganho}")
            #print("- - - - -")
            # Adicionar resultado à lista
            #print(f"ganho da coluna {column} de {ganho}")
            attributes_gain.append(AssociationID3(ganho, column))
        # Varrer lista e definir coluna que provém maior ganho de informação
        maior_ganho_coluna = ''
        maior_ganho = -1
        for atributo in attributes_gain:
            if atributo.ganho > maior_ganho:
                maior_ganho_coluna = atributo.coluna
                maior_ganho = atributo.ganho
        # Se o ganho de informação for abaixo do mínimo estabelecido, criar nó sem propagação
        if (maior_ganho < self.min_information):
            regra = rule.DecisionRuleID3('(Final)', maior_ganho, data, results, level)
            return regra
        # Criar regra resultado
        #print(f"maior_ganho: {maior_ganho}")
        regra = rule.DecisionRuleID3(maior_ganho_coluna, maior_ganho, data, results, level)
        #print(regra)
        #print("-     -------------------     -")
        # Criar conexões com nós seguintes da árvore para cada resultado possível do nó
        valores_coluna = list(set(data[maior_ganho_coluna]))
        for valor in valores_coluna:
            regra.connections.append(rule.Connection(valor))
        # Retornar resultado
        return regra
    
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Teste da árvore

    def test_tree(self, test_data, test_results):
        confusionMatrix = pd.DataFrame(index=self.results_list, columns=self.results_list)
        # Inicializar valores como 0
        for column in self.results_list:
            for row in self.results_list:
                confusionMatrix.loc[row, column] = 0
        for instancia in test_data.index:
            confusionMatrix = self.test_rule(self.root, test_data, test_results, instancia, confusionMatrix)
        return confusionMatrix

    def test_rule(self, rule, test_data, test_results, instancia, confusionMatrix):
        # Testar se o nó é final ou não
        if rule.attribute == '(Final)':
            # Adicionar mais um na matriz
            # Coluna é o resultado esperado
            # Linha é o real
            confusionMatrix.loc[test_results[instancia], rule.result] += 1
        else:
            # Checar a qual ramo a instância pertence
            for ramo in rule.connections:
                if ramo.result_name == test_data[rule.attribute][instancia]:
                    confusionMatrix = self.test_rule(ramo.rule, test_data, test_results, instancia, confusionMatrix)
        return confusionMatrix

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Print da árvore
    
    def __str__(self):
        return self.rule_to_str(self.root, "")

    def rule_to_str(self, current_rule, attribute_name):
        # Retornar vazio se regra for vazia
        if current_rule == None:
            #return f"{attribute_name}"
            return ""
        current_str = ""
        # Indentação em acordo com profundidade da árvore
        for i in range(current_rule.level):
            current_str = current_str + "  "
        # Adicionar valor de atributo que deriva de
        current_str = current_str + "{" + str(attribute_name) + "}" + "  "
        current_str = current_str + str(current_rule)
        #print(current_str)
        # Adicionar as ramificações
        # Falta inserir as conexões em si para exibir
        for branch in current_rule.connections:
            current_str = current_str + "\n" + self.rule_to_str(branch.rule, branch.result_name)
        return current_str

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Criação do objeto

class C45:
    # Criar árvore
    def __init__ (self, max_height, min_information, results):
        # Altura máxima
        # -1 significa que não tem máximo
        self.max_height = max_height
        self.current_height = 0
        # Regras para o ganho de informação
        self.min_information = min_information
        # Contar na coluna de resultados quantos há
        self.results_list = list(set(results))
        self.results_n = len(list(set(results)))
        # Definir raiz
        self.root = None
        # Teste

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Montagem da árvore

    # Montar árvore
    def create_tree(self, data, result):
        # Chamar método de montagem da árvore para a raiz
        self.root = self.define_rule(self.root, data, result, 0)

    # Método para montagem de árvore
    def define_rule(self, current_rule, data, result, level):
        # Chamar método de determinação de atributo e salvar regra de montagem
        regra_resultante = self.define_attribute(data, result, level)
        # Se retorno tiver sido nulo ou ganho de informação for 0, parar
        # Retorno nulo significa que o ganho na regra não foi suficiente
        # Ganho de informação 0 implica que não há mais informação a ser extraída da árvore
        if ( (regra_resultante != None) and (regra_resultante.gain_ratio != 0.0) ):
            if level > self.current_height:
                self.current_height = level
            # Se ainda não tiver chegado no limite de altura 
            if ( (level < self.max_height) or (self.max_height == -1) ):
                # Para caso seja uma regra para atributo numérico
                if regra_resultante.value != None:
                    #print(f"regra coluna: {regra_resultante.attribute}")
                    regra_value = float(regra_resultante.value)
                    #print(f"regra value: {regra_value}")
                    # Para cada ramo, chamar método de montagem da árvore
                    for ramo in regra_resultante.connections:
                        # Tabela completa para remover atributos que não encaixarem
                        data_branch = data
                        result_branch = result
                        if (ramo.result_name == '>'):
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                current_data = float(data[regra_resultante.attribute][row])
                                if ((current_data <= regra_value) or (current_data == None)):
                                    #print(f"{regra_value} >= {current_data}")
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        else:
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                current_data = float(data[regra_resultante.attribute][row])
                                if ((current_data > regra_value) or (current_data == None)):
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        # Chamar método de montagem da regra
                        #if(len(data_branch) == 0):
                            #print(f"Original data: {len(data)}")
                            #print(regra_resultante); print(f"{ramo.result_name} {regra_resultante.value}")
                        ramo.rule = self.define_rule(ramo.rule, data_branch, result_branch, level+1)
                else:
                    # Para cada ramo, chamar método de montagem da árvore
                    for ramo in regra_resultante.connections:
                        # Tabela completa para remover atributos que não encaixarem
                        data_branch = data
                        result_branch = result
                        # Remover dados não pertencentes ao ramo
                        for row in data.index:
                            if data[regra_resultante.attribute][row] != ramo.result_name or data[regra_resultante.attribute][row] == None:
                                data_branch = data_branch.drop(index=row)
                                result_branch = result_branch.drop(index=row)
                        # Chamar método de montagem da regra
                        #if(len(data_branch) == 0):
                            #print(regra_resultante); print(ramo.result_name)
                        ramo.rule = self.define_rule(ramo.rule, data_branch, result_branch, level+1)
        return regra_resultante

    # Método de determinação de atributo (recebendo dados e resultados de treino)
    def define_attribute(self, data_unformatted, results, level):
        # Formatar dados para melhor uso
        data = pd.DataFrame(data_unformatted)
        # Número de linhas
        n_instancias = len(data)
        resultados_distintos = list(set(results))
        n_resultados = len(list(set(results)))

        #print(f"resultados distinto: {resultados_distintos}")

        # Caso só haja um resultado distinto, não é necessário determinar uma regra
        if n_resultados == 1:
            regra = rule.DecisionRuleC45('(Final)', 1.0, data, results, level)
            return regra

        # Cálculo da entropia da classe
        entropia_classe = 0
        for resultado in resultados_distintos:
            frequencia = 0
            for instancia in results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            freq_div_instancias = (frequencia * 1.0)/(n_instancias * 1.0)
            entropia_atual = freq_div_instancias * (math.log(freq_div_instancias, n_resultados))
            entropia_classe = entropia_classe + entropia_atual
        entropia_classe = entropia_classe * (-1)
        # Criar lista separada para contabilizar ganho de informação em cada coluna
        attributes_gain = []
        # Loop de for para cada coluna
        for column in data.columns:
            lista_resultados = list(set(data[column]))
            valor_teste = 0
            # Para evitar o teste a seguir com um valor de None
            # Supõe-se que terá ao menos um valor não nulo
            #print(f"n_total: {n_instancias}, coluna: {column}")
            #print(lista_resultados)
            while (type(lista_resultados[valor_teste]) == None):
                valor_teste = valor_teste + 1
            # Se forem valores numéricos, tratar de forma diferente
            # Supõe-se que o tipo é consistente, então não é necessário testar o tipo de todas possibilidades
            if type(lista_resultados[valor_teste]) == int or type(lista_resultados[valor_teste]) == float:
                #print(f"Coluna numérica: {column}")
                lista_ganhos_por_valor = []
                ganhoinfo = entropia_classe
                # Variável do somatório
                somatorio_ganhoinfo = 0
                # Número de instâncias nulas da coluna
                n_none = 0
                # Cálculo de entropia
                # Para cada entrada possível
                for entrada in lista_resultados:
                    if entrada != None:
                        soma_menorigual = 0
                        soma_maior = 0
                        soma_ganhoinfo = 0
                        frequenciat_menorigual = 0 # Frequência total
                        frequenciat_maior = 0      # Frequência total
                        # Contabilizar instancias da entrada menor/igual e maiores
                        for instancia in data[column]:
                            if ( instancia != None ):
                                if instancia > entrada:
                                    frequenciat_maior = frequenciat_maior + 1
                                else:
                                    frequenciat_menorigual = frequenciat_menorigual + 1
                        # Contabilizar quantos número em cada resultado
                        for resultado in resultados_distintos:
                            frequencia = 0
                            frequencia_menorigual = 0
                            frequencia_maior = 0
                            for instancia in data.index:
                                if ( (results[instancia] == resultado) ):
                                    frequencia = frequencia + 1
                                    if (data[column][instancia] <= entrada):
                                        frequencia_menorigual = frequencia_menorigual + 1
                                    else:
                                        frequencia_maior = frequencia_maior + 1
                            # Probabilidade do resultado * Log 2 da probabilidade
                            # Somar ao dos demais resultados
                            # Se a frequência for zero, efetivamente somamos 0, o que significa nada
                            if frequencia != 0:
                                #print(n_resultados)
                                #print(f"freqt_menorigual: {frequenciat_menorigual}, freqt_maior: {frequenciat_maior}")
                                #print(f"freq_menorigual: {frequencia_menorigual}, freq_maior: {frequencia_maior}")
                                #print("")
                                # Menor/Igual
                                if frequencia_menorigual != 0:
                                    freq_div_menorigual = (frequencia_menorigual * 1.0)/(frequenciat_menorigual * 1.0)
                                    entropia_menorigual = freq_div_menorigual * (math.log(freq_div_menorigual, n_resultados))
                                    soma_menorigual = soma_menorigual + entropia_menorigual
                                # Maior
                                if frequencia_maior != 0:
                                    freq_div_maior = (frequencia_maior * 1.0)/(frequenciat_maior * 1.0)
                                    entropia_maior = freq_div_maior * (math.log(freq_div_maior, n_resultados))
                                    soma_maior = soma_maior + entropia_maior
                        # Multiplicar por -1 (correção devido a como log funciona)
                        soma_menorigual = soma_menorigual * (-1)
                        soma_maior = soma_maior * (-1)
                        # Multiplicar pelo n de ocorrencia da entrada e dividir pelo n total
                        soma_menorigual = soma_menorigual * ( (frequenciat_menorigual * 1.0) / (n_instancias * 1.0) )
                        soma_maior = soma_maior * ( (frequenciat_maior * 1.0) / (n_instancias * 1.0) )
                        # Somar resultado
                        soma_ganhoinfo = soma_menorigual + soma_maior
                        # Salvar resultado em lista (ainda em forma de entropia para não calcular desnecessariamente)
                        associacao = AssociationC45(soma_ganhoinfo, column)
                        associacao.value = entrada
                        lista_ganhos_por_valor.append(associacao)
                    else:
                        # Se entrada for None, contabilizar quantidade
                        for instancia in data[column]:
                            if ( (instancia == None) ):
                                n_none = n_none + 1
                # Obter valor numérico de menor entropia
                associacao_final = lista_ganhos_por_valor[0]
                for associacao in lista_ganhos_por_valor:
                    if (associacao.ganho < associacao_final.ganho):
                        associacao_final = associacao
                somatorio_ganhoinfo = associacao_final.ganho
                # Ganho = Ganho da classe - Somatório
                ganhoinfo = ganhoinfo - somatorio_ganhoinfo
                # Corrigir ganho de informação para contabilizar atributos nulos
                # Ganho é proporcional ao número não nulo
                ganhoinfo = ganhoinfo * ((n_instancias-n_none)/n_instancias)
                # Adicionar resultado à lista
                associacao_final.ganho = ganhoinfo
                attributes_gain.append(associacao_final)
            # Atributos que não sejam numéricos
            else:
                #print(f"Coluna não numérica: {column}")
                ganhoinfo = entropia_classe
                # Variável do somatório
                somatorio_ganhoinfo = 0
                somatorio_splitinfo = 0
                # Número de instâncias nulas da coluna
                n_none = 0
                # Cálculo de entropia
                # Para cada entrada possível
                for entrada in lista_resultados:
                    #print(f"c4.5, calculating for entrada {entrada}")
                    if entrada != None:
                        soma_ganhoinfo = 0
                        soma_splitinfo = 0
                        frequencia_entrada = 0
                        # Contabilizar instancias da entrada
                        for instancia in data[column]:
                            if ( (instancia == entrada) ):
                                frequencia_entrada = frequencia_entrada + 1
                        # Contabilizar quantos número em cada resultado
                        for resultado in resultados_distintos:
                            #print(f"calculating for entrada {entrada} resultado {resultado}")
                            frequencia = 0
                            for instancia in data.index:
                                if ( (data[column][instancia] == entrada) & (results[instancia] == resultado) ):
                                    frequencia = frequencia + 1
                            #print(f"frequencia_entrada = {frequencia_entrada} e frequencia = {frequencia}")
                            # Probabilidade do resultado * Log 2 da probabilidade
                            # Somar ao dos demais resultados
                            # Se a frequência for zero, efetivamente somamos 0, o que significa nada
                            if frequencia != 0:
                                #print("frequencia != 0")
                                # frequencia é a entrada com o valor atual que também tem o resultado atual
                                # frequencia_entrada é a entrada com o valor atual
                                # n_instancias é o total do dataset
                                freq_div_freqentrada = (frequencia * 1.0)/(frequencia_entrada * 1.0)
                                entropia_atual = freq_div_freqentrada * (math.log(freq_div_freqentrada, n_resultados))
                                soma_ganhoinfo = soma_ganhoinfo + entropia_atual
                                #print(f"div {freq_div_freqentrada} e soma_ganhoinfo {soma_ganhoinfo}")
                                #
                                prob_splitinfo = (frequencia_entrada * 1.0)/(n_instancias * 1.0)
                                splitinfo = prob_splitinfo * (math.log(prob_splitinfo, n_resultados))
                                soma_splitinfo = soma_splitinfo + splitinfo
                                #print(f"prob {prob_splitinfo} e soma_splitinfo {soma_splitinfo}")
                        # Multiplicar por -1 (correção devido a como log funciona)
                        soma_ganhoinfo = soma_ganhoinfo * (-1)
                        soma_splitinfo = soma_splitinfo * (-1)
                        # Multiplicar pelo n de ocorrencia da entrada e dividir pelo n total
                        soma_ganhoinfo = soma_ganhoinfo * ( (frequencia_entrada * 1.0) / (n_instancias * 1.0) )
                        # Somar resultado ao somatório
                        somatorio_ganhoinfo = somatorio_ganhoinfo + soma_ganhoinfo
                        somatorio_splitinfo = somatorio_splitinfo + soma_splitinfo
                    else:
                        # Se entrada for None, contabilizar quantidade
                        for instancia in data[column]:
                            if ( (instancia == None) ):
                                n_none = n_none + 1
                # Ganho = Ganho da classe - Somatório
                ganhoinfo = ganhoinfo - somatorio_ganhoinfo
                # Corrigir ganho de informação para contabilizar atributos nulos
                # Ganho é proporcional ao número não nulo
                ganhoinfo = ganhoinfo * ((n_instancias-n_none)/n_instancias)
                # Razão de ganho = Ganho / SplitInfo
                #print(f"gainratio = {ganhoinfo} / {somatorio_splitinfo}")
                if (somatorio_splitinfo == 0):
                    attributes_gain.append(AssociationC45(0.0, column))
                else:
                    gainratio = ganhoinfo/somatorio_splitinfo
                    # Adicionar resultado à lista
                    attributes_gain.append(AssociationC45(gainratio, column))
        # Varrer lista e definir coluna que provém maior razão de ganho
        associacao_final = attributes_gain[0]
        for associacao in attributes_gain:
            if associacao.ganho > associacao_final.ganho:
                associacao_final = associacao
        #print(f"C4.5 Associação final ganho: {associacao_final.ganho}")
        # Se a razão de ganho for abaixo do mínimo estabelecido, criar nó sem propagação
        if (associacao_final.ganho < self.min_information):
            regra = rule.DecisionRuleC45('(Final)', associacao_final.ganho, data, results, level)
            return regra
        # Criar regra resultado
        regra = rule.DecisionRuleC45(associacao_final.coluna, associacao_final.ganho, data, results, level)
        # Caso seja coluna de valor numérico
        if associacao_final.value != None:
            regra.value = associacao_final.value
            # Uma conexão para valores maiores e uma para menores
            regra.connections.append(rule.Connection('>'))
            regra.connections.append(rule.Connection('<='))
        else:
            # Criar conexões com nós seguintes da árvore para cada resultado possível do nó
            valores_coluna = list(set(data[associacao_final.coluna]))
            for valor in valores_coluna:
                regra.connections.append(rule.Connection(valor))
        # Retornar resultado
        #print(f"C4.5 Gain Ratio: {regra.gain_ratio}")
        return regra
    
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Teste da árvore

    def test_tree(self, test_data, test_results):
        confusionMatrix = pd.DataFrame(index=self.results_list, columns=self.results_list)
        # Inicializar valores como 0
        for column in self.results_list:
            for row in self.results_list:
                confusionMatrix.loc[row, column] = 0
        for instancia in test_data.index:
            confusionMatrix = self.test_rule(self.root, test_data, test_results, instancia, confusionMatrix)
        return confusionMatrix

    def test_rule(self, rule, test_data, test_results, instancia, confusionMatrix):
        # Testar se o nó é final ou não
        if rule.attribute == '(Final)':
            # Adicionar mais um na matriz
            # Coluna é o resultado esperado
            # Linha é o real
            confusionMatrix.loc[test_results[instancia], rule.result] += 1
        else:
            # Checar a qual ramo a instância pertence
            for ramo in rule.connections:
                # Ramo numérico
                if rule.value != None:
                    if test_data[rule.attribute][instancia] != None:
                        if ramo.result_name == '>' and test_data[rule.attribute][instancia] > rule.value:
                            confusionMatrix = self.test_rule(ramo.rule, test_data, test_results, instancia, confusionMatrix)
                        elif ramo.result_name == '<=' and test_data[rule.attribute][instancia] <= rule.value:
                            confusionMatrix = self.test_rule(ramo.rule, test_data, test_results, instancia, confusionMatrix)
                    else:
                        confusionMatrix.loc[test_results[instancia], rule.result] += 1
                # Não numérico
                else:
                    if ramo.result_name == test_data[rule.attribute][instancia]:
                        confusionMatrix = self.test_rule(ramo.rule, test_data, test_results, instancia, confusionMatrix)
        return confusionMatrix

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Print da árvore
    
    def __str__(self):
        return self.rule_to_str(self.root, "")

    def rule_to_str(self, current_rule, attribute_name):
        # Retornar vazio se regra for vazia
        if current_rule == None:
            #return f"{attribute_name}"
            return ""
        current_str = ""
        # Indentação em acordo com profundidade da árvore
        for i in range(current_rule.level):
            current_str = current_str + "  "
        # Adicionar valor de atributo que deriva de
        if current_rule.value != None:
            current_str = current_str + "{" + str(attribute_name) + str(current_rule.value) + "}  "
        else:
            current_str = current_str + "{" + str(attribute_name) + "}  "
        current_str = current_str + str(current_rule)
        #print(current_str)
        # Adicionar as ramificações
        # Falta inserir as conexões em si para exibir
        for branch in current_rule.connections:
            current_str = current_str + "\n" + self.rule_to_str(branch.rule, branch.result_name)
        return current_str

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Criação do objeto

class CART:
    # Criar árvore
    def __init__ (self, max_height, min_information, results):
        # Altura máxima
        # -1 significa que não tem máximo
        self.max_height = max_height
        self.current_height = 0
        # Regras para o ganho de informação
        self.min_information = min_information
        # Contar na coluna de resultados quantos há
        self.results_list = list(set(results))
        self.results_n = len(list(set(results)))
        # Definir raiz
        self.root = None
        # Teste

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Montagem da árvore

    # Montar árvore
    def create_tree(self, data, result):
        # Chamar método de montagem da árvore para a raiz
        self.root = self.define_rule(self.root, data, result, 0)

    # Método para montagem de árvore
    def define_rule(self, current_rule, data, result, level):
        # Chamar método de determinação de atributo e salvar regra de montagem
        regra_resultante = self.define_attribute(data, result, level)
        # Se retorno tiver sido nulo ou ganho de informação for 0, parar
        # Retorno nulo significa que o ganho na regra não foi suficiente
        # Ganho de informação 0 implica que não há mais informação a ser extraída da árvore
        if ( (regra_resultante != None) and (regra_resultante.gini != 0.0) ):
            if level > self.current_height:
                self.current_height = level
            # Se ainda não tiver chegado no limite de altura 
            if ( (level < self.max_height) or (self.max_height == -1) ):
                # Para caso seja uma regra para atributo numérico
                if ( (type(regra_resultante.value) == float) ):
                    # Para cada ramo, chamar método de montagem da árvore
                    for ramo in regra_resultante.connections:
                        # Tabela completa para remover atributos que não encaixarem
                        data_branch = data
                        result_branch = result
                        if (ramo.result_name == '>'):
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                if data[regra_resultante.attribute][row] <= regra_resultante.value or data[regra_resultante.attribute][row] == None:
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        else:
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                if data[regra_resultante.attribute][row] > regra_resultante.value or data[regra_resultante.attribute][row] == None:
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        #if len(data_branch) == 0:
                            #print(f"All data dropped in subsequent branch of: {ramo.result_name} {regra_resultante.value}")
                            #print(regra_resultante)
                            #print("Data:")
                            #print(data)
                            #print(".-.-.-.-.")
                        # Chamar método de montagem da regra
                        ramo.rule = self.define_rule(ramo.rule, data_branch, result_branch, level+1)
                else:
                    # Para cada ramo, chamar método de montagem da árvore
                    for ramo in regra_resultante.connections:
                        # Tabela completa para remover atributos que não encaixarem
                        data_branch = data
                        result_branch = result
                        if (ramo.result_name == '=='):
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                if data[regra_resultante.attribute][row] != regra_resultante.value or data[regra_resultante.attribute][row] == None:
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        else:
                            # Remover dados não pertencentes ao ramo
                            for row in data.index:
                                if data[regra_resultante.attribute][row] == regra_resultante.value or data[regra_resultante.attribute][row] == None:
                                    data_branch = data_branch.drop(index=row)
                                    result_branch = result_branch.drop(index=row)
                        #if len(data_branch) == 0:
                            #print(f"All data dropped in subsequent branch of: {ramo.result_name}")
                            #print(regra_resultante)
                            #print(".-.-.-.-.")
                        # Chamar método de montagem da regra
                        ramo.rule = self.define_rule(ramo.rule, data_branch, result_branch, level+1)
        return regra_resultante

    # Método de determinação de atributo (recebendo dados e resultados de treino)
    def define_attribute(self, data, results, level):
        # Número de linhas
        n_instancias = len(data)
        resultados_distintos = list(set(results))
        n_resultados = len(list(set(results)))
        #print(f"n_instancias = {n_instancias}, n_resultados = {n_resultados}")

        # Caso só haja um resultado distinto, não é necessário determinar uma regra
        if n_resultados == 1:
            #print("Cart (Final), apenas um resultado distinto")
            regra = rule.DecisionRuleCART('(Final)', 1.0, data, results, level)
            return regra
        
        # Cálculo do gini da classe
        gini_classe = 0
        for resultado in resultados_distintos:
            frequencia = 0
            for instancia in results:
                if instancia == resultado:
                    frequencia = frequencia + 1
            probabilidade_classe = (frequencia * 1.0)/(n_instancias * 1.0)
            gini_atual = pow(probabilidade_classe, 2)
            gini_classe = gini_classe + gini_atual
        gini_classe = 1 - gini_classe
        #print(f"gini_classe {gini_classe} in level {level}")

        # Criar lista separada para contabilizar ganho de informação em cada coluna
        attributes_gain = []
        # Loop de for para cada coluna
        for column in data.columns:
            lista_resultados = list(set(data[column]))
            valor_teste = 0
            # Para evitar o teste a seguir com um valor de None
            # Supõe-se que terá ao menos um valor não nulo
            while type(lista_resultados[valor_teste]) == None:
                valor_teste = valor_teste + 1
            # Se forem valores numéricos, tratar de forma diferente
            #print(f"{lista_resultados[valor_teste]} da coluna {column} tem tipo {type(lista_resultados[valor_teste])}")
            # Supõe-se que o tipo é consistente, então não é necessário testar o tipo de todas possibilidades
            if type(lista_resultados[valor_teste]) == float:
                #print("numeric value")
                lista_ganhos_por_valor = []
                # Número de instâncias nulas da coluna
                n_none = 0
                # Cálculo de gini
                # Para cada entrada possível
                for entrada in lista_resultados:
                    if entrada != None:
                        gini_maior = 1
                        gini_menorigual = 1
                        frequenciat_maior = 0       # Frequência total
                        frequenciat_menorigual = 0  # Frequência total
                        # Contabilizar instancias da entrada menor/igual e maiores
                        for instancia in data[column]:
                            if ( instancia != None ):
                                if instancia <= entrada:
                                    frequenciat_menorigual = frequenciat_menorigual + 1
                                else:
                                    frequenciat_maior = frequenciat_maior + 1
                        # Contabilizar quantos em cada resultado
                        for resultado in resultados_distintos:
                            frequencia = 0
                            frequencia_maior = 0
                            frequencia_menorigual = 0
                            for instancia in data.index:
                                if ( (results[instancia] == resultado) ):
                                    frequencia = frequencia + 1
                                    if (data[column][instancia] <= entrada):
                                        frequencia_menorigual = frequencia_menorigual + 1
                                    else:
                                        frequencia_maior = frequencia_maior + 1
                            # Probabilidade do resultado ^ 2
                            # Somar ao dos demais resultados
                            # Se a frequência for zero, efetivamente somamos 0, o que significa nada
                            if frequencia != 0:
                                if ((frequenciat_menorigual != 0) and (frequencia_menorigual != 0)):
                                    # Menor/Igual
                                    gini_menorigual = gini_menorigual - pow((frequencia_menorigual/frequenciat_menorigual), 2)
                                if ((frequenciat_maior != 0) and (frequencia_maior != 0)):
                                    # Maior
                                    gini_maior = gini_maior - pow((frequencia_maior/frequenciat_maior), 2)
                        # Pesar em acordo com a frequencia
                        gini_menorigual = gini_menorigual * (frequenciat_menorigual/n_instancias)
                        gini_maior = gini_maior * (frequenciat_maior/n_instancias)
                        # Ganho de gini
                        gini_entrada = gini_classe - (gini_menorigual + gini_maior)
                        # Salvar resultado em lista
                        #associacao = AssociationCART(gini_entrada, column)
                        associacao = AssociationCART((gini_menorigual + gini_maior), column)
                        associacao.value = entrada
                        lista_ganhos_por_valor.append(associacao)
                    else:
                        # Se entrada for None, contabilizar quantidade
                        for instancia in data[column]:
                            if ( (instancia == None) ):
                                n_none = n_none + 1
                # Obter valor numérico de maior ganho de gini
                associacao_final = lista_ganhos_por_valor[0]
                for associacao in lista_ganhos_por_valor:
                    if (associacao.gini < associacao_final.gini):
                        associacao_final = associacao
                # Adicionar resultado à lista
                attributes_gain.append(associacao_final)
            # Atributos que não sejam numéricos
            else:
                #print("non-numeric value")
                lista_ganhos_por_valor = []
                # Número de instâncias nulas da coluna
                n_none = 0
                # Cálculo de gini
                # Para cada entrada possível
                for entrada in lista_resultados:
                    if entrada != None:
                        gini_diferente = 1
                        gini_igual = 1
                        frequenciat_diferente = 0  # Frequência total
                        frequenciat_igual = 0      # Frequência total
                        # Contabilizar instancias da entrada iguais e diferentes
                        for instancia in data[column]:
                            if ( instancia != None ):
                                if instancia == entrada:
                                    frequenciat_igual = frequenciat_igual + 1
                                else:
                                    frequenciat_diferente = frequenciat_diferente + 1
                        # Contabilizar quantos em cada resultado
                        for resultado in resultados_distintos:
                            frequencia = 0
                            frequencia_diferente = 0
                            frequencia_igual = 0
                            for instancia in data.index:
                                if ( (results[instancia] == resultado) ):
                                    frequencia = frequencia + 1
                                    if (data[column][instancia] == entrada):
                                        frequencia_igual = frequencia_igual + 1
                                    else:
                                        frequencia_diferente = frequencia_diferente + 1
                            # Probabilidade do resultado ^ 2
                            # Somar ao dos demais resultados
                            # Se a frequência for zero, efetivamente somamos 0, o que significa nada
                            if frequencia != 0:
                                if ((frequenciat_igual != 0) and (frequencia_igual != 0)):
                                    # Menor/Igual
                                    gini_igual = gini_igual - pow((frequencia_igual/frequenciat_igual), 2)
                                if ((frequenciat_diferente != 0) and (frequencia_diferente != 0)):
                                    # Maior
                                    gini_diferente = gini_diferente - pow((frequencia_diferente/frequenciat_diferente), 2)
                        # Pesar em acordo com a quantidade/frequência
                        gini_igual = gini_igual * (frequenciat_igual/n_instancias)
                        gini_diferente = gini_diferente * (frequenciat_diferente/n_instancias)
                        # Ganho de gini
                        gini_entrada = gini_classe - (gini_igual + gini_diferente)
                        # Salvar resultado em lista
                        #associacao = AssociationCART(gini_entrada, column)
                        associacao = AssociationCART((gini_igual + gini_diferente), column)
                        associacao.value = entrada
                        lista_ganhos_por_valor.append(associacao)
                    else:
                        # Se entrada for None, contabilizar quantidade
                        for instancia in data[column]:
                            if ( (instancia == None) ):
                                n_none = n_none + 1
                # Obter valor numérico de maior ganho de gini
                associacao_final = lista_ganhos_por_valor[0]
                for associacao in lista_ganhos_por_valor:
                    if (associacao.gini < associacao_final.gini):
                        associacao_final = associacao
                # Adicionar resultado à lista
                attributes_gain.append(associacao_final)
        # Varrer lista e definir coluna que provém maior gini
        associacao_final = attributes_gain[0]
        for associacao in attributes_gain:
            if associacao.gini < associacao_final.gini:
                associacao_final = associacao
        #print(f"ganho de gini final: {associacao_final.gini}")
        # Se o índice de gini for abaixo do mínimo estabelecido, criar nó sem propagação
        if (associacao_final.gini < self.min_information):
            #print("Cart (Final), abaixo do mínimo")
            regra = rule.DecisionRuleCART('(Final)', associacao_final.gini, data, results, level)
            return regra
        # Se índice de gini for a máxima impureza, não há informação a ser extraída
        if ( associacao_final.gini == (1-(1/n_resultados)) ):
            #print("Cart (Final), ganho de informação com gini mínimo")
            regra = rule.DecisionRuleCART('(Final)', associacao_final.gini, data, results, level)
            return regra
        # Caso já tenha chegado na altura máxima, retornar nó final
        if (level == self.max_height):
            #print("Cart (Final), altura máxima")
            regra = rule.DecisionRuleCART('(Final)', associacao_final.gini, data, results, level)
            return regra
        # Criar regra resultado
        regra = rule.DecisionRuleCART(associacao_final.coluna, associacao_final.gini, data, results, level)
        # Caso seja coluna de valor numérico
        if ( type(associacao_final.value) == float ):
            regra.value = float(associacao_final.value)
            # Uma conexão para valores maiores e uma para menores
            regra.connections.append(rule.Connection('>'))
            regra.connections.append(rule.Connection('<='))
        else:
            regra.value = associacao_final.value
            # Uma conexão para valores diferentes e uma para iguais
            regra.connections.append(rule.Connection('=='))
            regra.connections.append(rule.Connection('!='))
        # Retornar resultado
        return regra
    
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Teste da árvore

    def test_tree(self, test_data, test_results):
        confusionMatrix = pd.DataFrame(index=self.results_list, columns=self.results_list)
        # Inicializar valores como 0
        for column in self.results_list:
            for row in self.results_list:
                confusionMatrix.loc[row, column] = 0
        for instancia in test_data.index:
            confusionMatrix = self.test_rule(self.root, test_data.loc[instancia], test_results.loc[instancia], confusionMatrix)
        return confusionMatrix

    def test_rule(self, rule, instancia, instancia_result, confusionMatrix):
        # Testar se o nó é final ou não
        if rule.attribute == '(Final)':
            # Adicionar mais um na matriz
            # Coluna é o resultado esperado
            # Linha é o real
            confusionMatrix.loc[instancia_result, rule.result] += 1
        else:
            # Checar a qual ramo a instância pertence
            for ramo in rule.connections:
                #print(" - - - - - ")
                #print(instancia)
                #print(f"result {instancia_result}")
                #print("")
                #print(rule)
                #print("")
                if instancia[rule.attribute] != None:
                    if   ( (ramo.result_name == '>')  and (float(instancia[rule.attribute]) >  float(rule.value)) ):
                        confusionMatrix = self.test_rule(ramo.rule, instancia, instancia_result, confusionMatrix)
                    elif ( (ramo.result_name == '<=') and (float(instancia[rule.attribute]) <= float(rule.value)) ):
                        confusionMatrix = self.test_rule(ramo.rule, instancia, instancia_result, confusionMatrix)
                    elif ( (ramo.result_name == '==') and (instancia[rule.attribute] == rule.value) ):
                        confusionMatrix = self.test_rule(ramo.rule, instancia, instancia_result, confusionMatrix)
                    elif ( (ramo.result_name == '!=') and (instancia[rule.attribute] != rule.value) ):
                        confusionMatrix = self.test_rule(ramo.rule, instancia, instancia_result, confusionMatrix)
                    #else:
                        #print(f"ramo result_name = {ramo.result_name}, rule.value = {rule.value}")
                else:
                    confusionMatrix.loc[instancia_result, rule.result] += 1
        return confusionMatrix

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Print da árvore
    
    def __str__(self):
        return self.rule_to_str(self.root, "")

    def rule_to_str(self, current_rule, attribute_name):
        # Retornar vazio se regra for vazia
        if current_rule == None:
            #return f"{attribute_name}"
            return ""
        current_str = ""
        # Indentação em acordo com profundidade da árvore
        for i in range(current_rule.level):
            current_str = current_str + "  "
        # Adicionar valor de atributo que deriva de
        if current_rule.value != None:
            current_str = current_str + "{" + str(attribute_name) + str(current_rule.value) + "}  "
        else:
            current_str = current_str + "{" + str(attribute_name) + "}  "
        current_str = current_str + str(current_rule)
        #print(current_str)
        # Adicionar as ramificações
        # Falta inserir as conexões em si para exibir
        for branch in current_rule.connections:
            current_str = current_str + "\n" + self.rule_to_str(branch.rule, branch.result_name)
        return current_str

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# Classe de suporte

class AssociationID3:
    def __init__(self, ganho, coluna):
        self.ganho = ganho
        self.coluna = coluna

# A árvore C4.5 precisa de um atributo extra para registrar em qual valor há a divisão
class AssociationC45:
    def __init__(self, ganho, coluna):
        self.ganho = ganho
        self.coluna = coluna
        # Valor para divisão em caso de valor numérico
        # None por padrão para caso de Strings e outros
        self.value = None

class AssociationCART:
    def __init__(self, gini, coluna):
        self.gini = gini
        self.coluna = coluna
        # Valor para divisão em caso de valor numérico
        # None por padrão para caso de Strings e outros
        self.value = None

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_



