import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request

app = Flask(__name__)

# Definición de palabras reservadas para cada lenguaje
reserved = {
    'custom': {
        'declaracion': 'DECLARACION',
        'flotante': 'FLOAT',
        'entero': 'INT',
        'cadena': 'STRING',
        'hacer': 'HACER',
        'mientras': 'MIENTRAS',
        'para': 'PARA',
        'en': 'EN',
        'presentar': 'PRESENTAR',
        'consola': 'CONSOLA',
        'sumatoria': 'SUMATORIA',
        'resta': 'SUBSTRACTION',
        'producto': 'PRODUCTO',
        'division': 'DIVISION',
        'almacenar': 'ALMACENAR',
    },
}

# Lista de tokens
tokens = [
    'IDENTIFICADOR',
    'ABIERTO',
    'CERRADO',
    'LLAVE_ABIERTA',
    'LLAVE_CERRADA',
    'PUNTO_Y_COMA',
    'IGUAL',
    'MAS',
    'RESTA',
    'DIVISION',
    'MENOR_IGUAL',
    'MAYOR_IGUAL',
    'PUNTO',
    'MAS_IGUAL',
    'COMILLAS',
    'CADENA',
    'NUMERO',
    'MENOR',
    'MAYOR',
    'COMA',
    'POR',
    'GATO',
] + list(set(sum([list(r.values()) for r in reserved.values()], [])))

# Reglas para tokens simples
t_ABIERTO = r'\('
t_CERRADO = r'\)'
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_PUNTO_Y_COMA = r';'
t_COMA = r','
t_IGUAL = r'='
t_MAS = r'\+'
t_RESTA = r'\-'
t_DIVISION = r'/'
t_MAS_IGUAL = r'\+='
t_POR = r'\*'
t_GATO = r'\#'
t_MENOR_IGUAL = r'<='
t_MAYOR_IGUAL = r'>='
t_MENOR = r'<'
t_MAYOR = r'>'
t_PUNTO = r'\.'
t_COMILLAS = r'\"'
t_CADENA = r'\".*?\"'

# Contadores
reserved_count = 0
identificador_count = 0
number_count = 0
symbol_count = 0
p_abierto_count = 0
p_cerrado_count = 0
ll_abierta_count = 0
ll_cerrada_count = 0
error_count = 0

out = ''
prints = []

def t_NUMERO(t):
    r'-?\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Lista para guardar declaraciones de variables
declared_variables = {}

# Regla para identificadores y palabras reservadas
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    global current_language
    t.type = reserved[current_language].get(t.value.lower(), 'IDENTIFICADOR')
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Función para manejar errores léxicos
def t_error(t):
    global error_count
    error_count += 1
    print(f"Caracter no válido: {t.value[0]}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

def p_program(p):
    '''program : statement_list'''

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    
def p_statement(p):
    '''statement : 
                 | variable_declaration
                 | assignment_statement
                 | condition_statement
                 | increment_statement
                 | condition
                 | print_statement
                 | suma_statement
                 | resta_statement
                 | product_statement
                 | division_statement'''

def p_variable_declaration(p):
    '''variable_declaration : DECLARACION INT IDENTIFICADOR NUMERO PUNTO_Y_COMA
                            | DECLARACION INT IDENTIFICADOR PUNTO_Y_COMA
                            | DECLARACION FLOAT IDENTIFICADOR NUMERO PUNTO_Y_COMA
                            | DECLARACION STRING IDENTIFICADOR CADENA PUNTO_Y_COMA'''
    global out
    if p[3] in declared_variables:
        raise SemanticError(f"Variable '{p[3]}' ya declarada")
    if p[2] == 'entero' and len(p) == 6:
        print(f"Declaración de variable: {p[3]} = {p[4]}")  # Debugging output
        out = f"Declaración de variable: {p[3]} = {p[4]}"
        declared_variables[p[3]] = {'tipo': 'int', 'valor': int(p[4])}
    elif p[2] == 'entero' and len(p) == 5:
        print(f"Declaración de variable: {p[3]}")
        out = f"Declaración de variable: {p[3]}"
        declared_variables[p[3]] = {'tipo': 'int', 'valor': 0}
    elif p[2] == 'flotante':
        print(f"Declaración de variable: {p[3]} = {p[4]}")  # Debugging output
        out = f"Declaración de variable: {p[3]} = {p[4]}"
        declared_variables[p[3]] = {'tipo': 'float', 'valor': p[4]}
    elif p[2] == 'cadena':
        print(f"Declaración de variable: {p[3]} = {p[4]}")  # Debugging output
        out = f"Declaración de variable: {p[3]} = {p[4]}"
        declared_variables[p[3]] = {'tipo': 'string', 'valor': p[4]}

def p_suma_operation(p):
    '''suma_statement : ALMACENAR EN IDENTIFICADOR SUMATORIA IDENTIFICADOR MAS IDENTIFICADOR PUNTO_Y_COMA
                      | ALMACENAR EN IDENTIFICADOR SUMATORIA NUMERO MAS IDENTIFICADOR PUNTO_Y_COMA
                      | ALMACENAR EN IDENTIFICADOR SUMATORIA IDENTIFICADOR MAS NUMERO PUNTO_Y_COMA
                      | ALMACENAR EN IDENTIFICADOR SUMATORIA NUMERO MAS NUMERO PUNTO_Y_COMA '''

    value1 = get_value(p[5])
    value2 = get_value(p[7])
    type1 = get_type(p[5])
    type2 = get_type(p[7])
    
    if type1 == 'int' and type2 == 'int':
        result = (int(value1)) + (int(value2))
        result_type = 'int'
    elif type1 == 'float' or type2 == 'float':
        result = float(value1) + float(value2)
        result_type = 'float'
    else:
        raise SemanticError("Tipos de datos no válidos para la suma")

    # Acumulación
    if p[3] in declared_variables:
        current_value = declared_variables[p[3]]['valor']
        current_type = declared_variables[p[3]]['tipo']
        
        if current_type == 'int' and result_type == 'int':
            accumulated_result = int(current_value) + result
            accumulated_type = 'int'
        else:
            accumulated_result = float(current_value) + float(result)
            accumulated_type = 'float'
        
        declared_variables[p[3]] = {'tipo': accumulated_type, 'valor': accumulated_result}
    else:
        declared_variables[p[3]] = {'tipo': result_type, 'valor': result}

def p_substraction_operation(p):
    '''resta_statement : ALMACENAR EN IDENTIFICADOR SUBSTRACTION IDENTIFICADOR RESTA IDENTIFICADOR PUNTO_Y_COMA
                       | ALMACENAR EN IDENTIFICADOR SUBSTRACTION NUMERO RESTA IDENTIFICADOR PUNTO_Y_COMA
                       | ALMACENAR EN IDENTIFICADOR SUBSTRACTION IDENTIFICADOR RESTA NUMERO PUNTO_Y_COMA
                       | ALMACENAR EN IDENTIFICADOR SUBSTRACTION NUMERO RESTA NUMERO PUNTO_Y_COMA '''

    value1 = get_value(p[5])
    value2 = get_value(p[7])
    type1 = get_type(p[5])
    type2 = get_type(p[7])

    if type1 == 'int' and type2 == 'int':
        result = int(value1) - int(value2)
        result_type = 'int'
    elif type1 == 'float' or type2 == 'float':
        result = float(value1) - float(value2)
        result_type = 'float'
    else:
        raise SemanticError("Tipos de datos no válidos para la suma")

    # Acumulación
    if p[3] in declared_variables:
        current_value = declared_variables[p[3]]['valor']
        current_type = declared_variables[p[3]]['tipo']
        
        if current_type == 'int' and result_type == 'int':
            accumulated_result = int(current_value) + result
            accumulated_type = 'int'
        else:
            accumulated_result = float(current_value) + float(result)
            accumulated_type = 'float'
        
        declared_variables[p[3]] = {'tipo': accumulated_type, 'valor': accumulated_result}
    else:
        declared_variables[p[3]] = {'tipo': result_type, 'valor': result}

def p_product_operation(p):
    '''product_statement : ALMACENAR EN IDENTIFICADOR PRODUCTO IDENTIFICADOR POR IDENTIFICADOR PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR PRODUCTO NUMERO POR IDENTIFICADOR PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR PRODUCTO IDENTIFICADOR POR NUMERO PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR PRODUCTO NUMERO POR NUMERO PUNTO_Y_COMA '''

    value1 = get_value(p[5])
    value2 = get_value(p[7])
    type1 = get_type(p[5])
    type2 = get_type(p[7])

    if type1 == 'int' and type2 == 'int':
        result = int(value1) * int(value2)
        result_type = 'int'
    elif type1 == 'float' or type2 == 'float':
        result = float(value1) * float(value2)
        result_type = 'float'
    else:
        raise SemanticError("Tipos de datos no válidos para la suma")

    # Acumulación
    if p[3] in declared_variables:
        current_value = declared_variables[p[3]]['valor']
        current_type = declared_variables[p[3]]['tipo']
        
        if current_type == 'int' and result_type == 'int':
            accumulated_result = int(current_value) + result
            accumulated_type = 'int'
        else:
            accumulated_result = float(current_value) + float(result)
            accumulated_type = 'float'
        
        declared_variables[p[3]] = {'tipo': accumulated_type, 'valor': accumulated_result}
    else:
        declared_variables[p[3]] = {'tipo': result_type, 'valor': result}

def p_division_operation(p):
    '''division_statement : ALMACENAR EN IDENTIFICADOR DIVISION IDENTIFICADOR DIVISION IDENTIFICADOR PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR DIVISION NUMERO DIVISION IDENTIFICADOR PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR DIVISION IDENTIFICADOR DIVISION NUMERO PUNTO_Y_COMA
                         | ALMACENAR EN IDENTIFICADOR DIVISION NUMERO DIVISION NUMERO PUNTO_Y_COMA '''

    value1 = get_value(p[5])
    value2 = get_value(p[7])
    type1 = get_type(p[5])
    type2 = get_type(p[7])

    if type1 == 'int' and type2 == 'int':
        result = int(value1) / int(value2)
        result_type = 'int'
    elif type1 == 'float' or type2 == 'float':
        result = float(value1) / float(value2)
        result_type = 'float'
    else:
        raise SemanticError("Tipos de datos no válidos para la suma")

    # Acumulación
    if p[3] in declared_variables:
        current_value = declared_variables[p[3]]['valor']
        current_type = declared_variables[p[3]]['tipo']
        
        if current_type == 'int' and result_type == 'int':
            accumulated_result = int(current_value) + result
            accumulated_type = 'int'
        else:
            accumulated_result = float(current_value) + float(result)
            accumulated_type = 'float'
        
        declared_variables[p[3]] = {'tipo': accumulated_type, 'valor': accumulated_result}
    else:
        declared_variables[p[3]] = {'tipo': result_type, 'valor': result}
    
def p_print_statement(p):
    '''print_statement : PRESENTAR IDENTIFICADOR EN CONSOLA PUNTO_Y_COMA
                       | PRESENTAR EN CONSOLA CADENA PUNTO_Y_COMA'''
    
    global out, prints
    if p[2] == 'en':
        print(p[4].split('"')[1])
        out = declared_variables[p[4]].split('"')[1]
        prints.append(out)
    elif p[2] in declared_variables:
        if declared_variables[p[2]]['tipo'] == "string":
            print(declared_variables[p[2]]['valor'].split('"')[1])
            out = declared_variables[p[2]]['valor'].split('"')[1]
            prints.append(out)
        else:
            print(declared_variables[p[2]]['valor'])
            out = declared_variables[p[2]]['valor']
            prints.append(out)
    elif p[2] not in declared_variables:
        raise SemanticError(f"Variable '{p[2]}' no declarada")

def p_condition(p):
    '''condition : INT IDENTIFICADOR IGUAL IGUAL NUMERO
                 | IDENTIFICADOR IGUAL IGUAL NUMERO'''
    if len(p) == 6:
        if p[2] not in declared_variables:
            raise SemanticError(f"Variable '{p[2]}' no declarada.")
    # Caso cuando la condición es del tipo "IDENTIFICADOR IGUAL IGUAL NUMERO"
    if len(p) == 5:
        identificador = p[1]
        valor_esperado = p[4]
        if identificador in declared_variables:
            # Obtiene el valor actual de la variable
            valor_actual = declared_variables[identificador]['valor']
            # Compara el valor actual con el valor esperado en la condición
            if valor_actual == valor_esperado:
                # La condición se cumple
                pass
            else:
                raise SemanticError(f"La condicion es falsa para '{identificador}' = {valor_esperado}.")
        else:
            raise SemanticError(f"Variable '{identificador}' no declarada.")

def p_assignment_statement(p):
    '''assignment_statement : IDENTIFICADOR IGUAL NUMERO
                            | IDENTIFICADOR IGUAL IDENTIFICADOR MAS IDENTIFICADOR'''
    if len(p) == 5:
        if p[1] not in declared_variables:
            raise SemanticError(f"Variable '{p[1]}' no declarada")
        if p[3] not in declared_variables:
            raise SemanticError(f"Variable '{p[3]}' no declarada")
        if p[5] not in declared_variables:
            raise SemanticError(f"Variable '{p[5]}' no declarada")
    else:
        if p[1] not in declared_variables:
            raise SemanticError(f"Variable '{p[1]}' no declarada")

def p_condition_statement(p):
    '''condition_statement : IDENTIFICADOR MENOR_IGUAL NUMERO
                           | IDENTIFICADOR IGUAL IGUAL NUMERO
                           | IDENTIFICADOR MAYOR NUMERO
                           | IDENTIFICADOR MAYOR_IGUAL NUMERO'''
    identificador = p[1]
    valor_esperado = p[3]
    if identificador in declared_variables:
        # Obtiene el valor actual de la variable
        valor_actual = declared_variables[identificador]['valor']
        print(valor_actual)
        # Compara el valor actual con el valor esperado en la condición
        if valor_actual <= valor_esperado:
            # La condición se cumple
            pass
        elif valor_actual == valor_esperado:
            pass
        else:
            raise SemanticError(f"La condicion es falsa para '{identificador}' con {valor_esperado}.")
    else:
        raise SemanticError(f"Variable '{identificador}' no declarada.")

def p_increment_statement(p):
    '''increment_statement : IDENTIFICADOR MAS MAS
                           | IDENTIFICADOR MAS_IGUAL NUMERO'''
    if p[1] not in declared_variables:
        raise SemanticError(f"Variable '{p[1]}' no declarada")
    if declared_variables[p[1]]['tipo'] != 'int':
        if declared_variables[p[1]]['tipo'] != 'float':
            raise SemanticError(f"Variable '{p[1]}' no es de tipo entero o flotante")
    
    declared_variables[p[1]]['valor'] += 1 if p[2] == '+' and p[3] == '+' else int(p[3])

def p_error(p):
    if p:
        error_message = f"Error sintáctico en el token anterior a {p.value}"
        print(declared_variables)
    else:
        error_message = "Error sintáctico: Fin inesperado del archivo"
    raise SyntaxError(error_message)

def get_value(item):
        if isinstance(item, str):
            if item.startswith('-'):
                return -float(item[1:]) if '.' in item else -int(item[1:])
            elif item.isdigit() or (item.count('.') == 1 and item.replace('.', '').isdigit()):
                return float(item) if '.' in item else int(item)
            elif item in declared_variables:
                return declared_variables[item]['valor']
            else:
                raise SemanticError(f"Variable '{item}' no declarada")
        return item

def get_type(item):
    if isinstance(item, str):
        if item.startswith('-'):
            item = item[1:]
        if '.' in item:
            return 'float'
        elif item.isdigit():
            return 'int'
        elif item in declared_variables:
            return declared_variables[item]['tipo']
        else:
            raise SemanticError(f"Variable '{item}' no declarada")
    elif isinstance(item, int):
        return 'int'
    elif isinstance(item, float):
        return 'float'
    else:
        raise SemanticError(f"Tipo de dato no válido: {type(item)}")

# Construir el parser
parser = yacc.yacc(debug=True)

# Excepcion personalizada para el análisis semántico
class SemanticError(Exception):
    pass

@app.route('/', methods=['GET', 'POST'])
def index():
    global reserved_count, identificador_count, number_count, symbol_count, p_abierto_count, p_cerrado_count, ll_abierta_count, ll_cerrada_count, error_count, current_language
    reserved_count = 0
    identificador_count = 0
    number_count = 0
    symbol_count = 0
    p_abierto_count = 0
    p_cerrado_count = 0
    ll_abierta_count = 0
    ll_cerrada_count = 0
    error_count = 0

    global out, prints
    out = ''
    prints = []
    content = ''
    if request.method == 'POST':
        current_language = 'custom'
        content = request.form.get('code', '')
        
        syntax_result = []
        try:
            declared_variables.clear()
            parser.parse(content)
            print(prints)
            syntax_result = [("Análisis Sintáctico Exitoso", "", prints, False)]
        except SyntaxError as e:
            result = "Error en Análisis Sintáctico"
            out = str(e)
            syntax_result = [(result, out, prints, True)]
        except SemanticError as e:  # Captura el SemanticError para evitar que el programa truene
            result = "Analisis Sintactico Exitoso, posible error Semántico detectado" 
            out = str(e)
            syntax_result = [(result, out, prints, True)]
        return render_template('index.html', tokens=None, syntax_result=syntax_result, content=content, abierto_count=p_abierto_count, cerrado_count=p_cerrado_count, ll_abierta_count=ll_abierta_count, ll_cerrada_count=ll_cerrada_count)

    return render_template('index.html', tokens=None, syntax_result=None, content=content, abierto_count=p_abierto_count, cerrado_count=p_cerrado_count)

if __name__ == "__main__":
    app.run(debug=True)