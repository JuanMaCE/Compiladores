class NodoAST:
    def traducir(self):
        raise NotImplementedError("Metodo traducir() no implementado")
    def generar_codigo(self):
        raise NotImplementedError("Metodo generar_codigo() no implementado")

class NodoPrograma(NodoAST):
    def __init__(self, funciones):
        self.funciones = funciones
        
    def traducir(self):
        return [f.traducir() for f in self.funciones]
    
    def generar_codigo(self):
        variables = set()
        for funcion in self.funciones:
            variables.update(self._collect_variables(funcion))
        
        codigo = [
            "; === Programa Generado ===",
            "section .data",
            "    newline db 10, 0",
            "    true_str db 'True', 0",
            "    false_str db 'False', 0",
            "    float_fmt db '%f', 0",
            "    num_buffer times 20 db 0",  
            "    float_buffer times 32 db 0", 
            "    read_buffer times 64 db 0",  
            "",
            "section .bss"
        ]
        
        for var in variables:
            codigo.append(f"    {var} resd 1")
            
        codigo.extend([
            "",
            "section .text",
            "    global _start",
            "    extern sprintf",
            "",
            "; === Funciones de ayuda ===",
            "strlen:",
            "    push ebp",
            "    mov ebp, esp",
            "    mov eax, 0",
            ".loop:",
            "    cmp byte [ecx+eax], 0",
            "    je .done",
            "    inc eax",
            "    jmp .loop",
            ".done:",
            "    mov esp, ebp",
            "    pop ebp",
            "    ret",
            "",
            "; Convierte entero a string",
            "; Entrada: EAX = número a convertir, ECX = buffer donde guardarlo",
            "; Salida: EAX = longitud del string resultante",
            "int_to_string:",
            "    push ebp",
            "    mov ebp, esp",
            "    push ebx",
            "    push edi",
            "    push esi",
            "    ",
            "    mov edi, ecx        ; Buffer de salida",
            "    mov esi, eax        ; Guardar número original",
            "    xor ecx, ecx        ; Contador de dígitos",
            "    ",
            "    ; Manejar el caso cero",
            "    test eax, eax",
            "    jnz .no_cero",
            "    mov byte [edi], '0'",
            "    inc edi",
            "    mov eax, 1  ; Longitud = 1",
            "    jmp .fin",
            "    ",
            ".no_cero:",
            "    ; Manejar negativos",
            "    cmp esi, 0",
            "    jge .positivo",
            "    neg esi",
            "    mov byte [edi], '-'",
            "    inc edi",
            "    inc ecx  ; Contar el signo como un dígito",
            "",
            ".positivo:",
            "    ; Convertir dígitos",
            "    mov ebx, 10",
            ".digito_loop:",
            "    xor edx, edx",
            "    mov eax, esi",
            "    div ebx",
            "    add dl, '0'",
            "    push edx",
            "    inc ecx",
            "    mov esi, eax",
            "    test eax, eax",
            "    jnz .digito_loop",
            "    ",
            "    ; Sacar dígitos de la pila",
            "    mov edx, ecx  ; Guardar longitud original",
            ".pop_loop:",
            "    pop eax",
            "    mov [edi], al",
            "    inc edi",
            "    dec ecx",
            "    jnz .pop_loop",
            "",
            "    mov byte [edi], 0   ; Terminador nulo",
            "    mov eax, edx        ; Devolver longitud",
            "",
            ".fin:",
            "    pop esi",
            "    pop edi",
            "    pop ebx",
            "    mov esp, ebp",
            "    pop ebp",
            "    ret",
            "",
            "; Función de lectura mejorada (scan)",
            "; Entrada: EDI = buffer para almacenar el valor leído",
            "; Salida: EAX = valor numérico",
            "read_int:",
            "    push ebp",
            "    mov ebp, esp",
            "    push ebx",
            "    push esi",
            "    push edi",
            "",
            "    ; Leer entrada",
            "    mov eax, 3",
            "    mov ebx, 0",
            "    mov ecx, read_buffer",
            "    mov edx, 64",
            "    int 0x80",
            "",
            "    ; Convertir string a número",
            "    mov esi, read_buffer",
            "    xor eax, eax",
            "    xor ebx, ebx",
            "    xor ecx, ecx",
            "",
            "    ; Verificar signo negativo",
            "    mov cl, [esi]",
            "    cmp cl, '-'",
            "    jne .convert_loop",
            "    inc esi",
            "    mov ebx, 1  ; Marcar como negativo",
            "",
            ".convert_loop:",
            "    mov cl, [esi]",
            "    cmp cl, 10  ; Salto de línea",
            "    je .convert_end",
            "    cmp cl, 0  ; Fin de string",
            "    je .convert_end",
            "",
            "    sub cl, '0'",
            "    cmp cl, 9",
            "    ja .next_char  ; Ignorar caracteres no numéricos",
            "",
            "    imul eax, 10",
            "    add eax, ecx",
            "",
            ".next_char:",
            "    inc esi",
            "    jmp .convert_loop",
            "",
            ".convert_end:",
            "    ; Aplicar signo si es negativo",
            "    test ebx, ebx",
            "    jz .done",
            "    neg eax",
            "",
            ".done:",
            "    ; Guardar resultado en la variable",
            "    mov [edi], eax",
            "",
            "    pop edi",
            "    pop esi",
            "    pop ebx",
            "    mov esp, ebp",
            "    pop ebp",
            "    ret",
            "",
            "_start:",
            "    ; Inicialización",
            "    mov ebp, esp",
            "    and esp, -16  ; Alinear stack a 16 bytes para llamadas a funciones C",
            "",
            "    ; Llamar a main",
            "    call main",
            "",
            "    ; Terminar programa",
            "    mov eax, 1",
            "    xor ebx, ebx",
            "    int 0x80",
        ])
        
        for funcion in self.funciones:
            codigo.append(funcion.generar_codigo())
        
        return "\n".join(codigo)

    def _collect_variables(self, node):
        variables = set()
        if isinstance(node, (NodoIdentificador, NodoDeclaracion, NodoAsignacion)):
            if isinstance(node.nombre, str):
                variables.add(node.nombre)
            elif isinstance(node.nombre, tuple):
                variables.add(node.nombre[1])
        elif isinstance(node, NodoLlamarFuncion):
            for arg in node.argumentos:
                variables.update(self._collect_variables(arg))
        
        if hasattr(node, '__dict__'):
            for attr in node.__dict__.values():
                if isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, NodoAST):
                            variables.update(self._collect_variables(item))
                elif isinstance(attr, NodoAST):
                    variables.update(self._collect_variables(attr))
        return variables

class NodoFuncion(NodoAST):
    def __init__(self, tipo, nombre, parametros, cuerpo):
        self.tipo = tipo
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo
        
    def traducir(self):
        params = ", ".join(p.traducir() for p in self.parametros)
        cuerpo = "\n\t".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre}({params}):\n\t{cuerpo}\n"
    
    def generar_codigo(self):
        codigo = [
            f"; === Función: {self.nombre} ===",
            f"{self.nombre}:",
            "    push ebp",
            "    mov ebp, esp",
        ]
        
        local_vars = sum(1 for inst in self.cuerpo if isinstance(inst, NodoDeclaracion))
        if local_vars > 0:
            codigo.append(f"    sub esp, {4 * local_vars}")
        
        codigo.append("    push ebx")
        codigo.append("    push esi")
        codigo.append("    push edi")
        
        for inst in self.cuerpo:
            inst_code = inst.generar_codigo()
            if inst_code:
                codigo.append(inst_code)
        
        if self.nombre == "main":
            codigo.append("    xor eax, eax  ; Retornar 0 por defecto si es main")
        
        codigo.append(f".return:")    
            
        codigo.extend([
            "    pop edi",
            "    pop esi",
            "    pop ebx",
            "    mov esp, ebp",
            "    pop ebp",
            "    ret"
        ])
        
        return "\n".join(codigo)

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return f"{self.tipo} {self.nombre}"
    
    def generar_codigo(self):
        return f"; Parámetro: {self.tipo} {self.nombre}"

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre 
        self.expresion = expresion
        
    def traducir(self):
        return f"{self.nombre[1]} = {self.expresion.traducir()}"
    
    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
        
        if isinstance(self.nombre, tuple):
            var_name = self.nombre[1]
        else:
            var_name = self.nombre
            
        return codigo + f"\n    mov [{var_name}], eax ; asignar a {var_name}"

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"

    def generar_codigo(self):
        codigo = [
            self.derecha.generar_codigo(),
            "    push eax",
            self.izquierda.generar_codigo()
        ]
        
        codigo.append("    pop ebx  ; Valor derecho")
        
        if self.operador == '+':
            codigo.append("    add eax, ebx")
        elif self.operador == '-':
            codigo.append("    sub eax, ebx")
        elif self.operador == '*':
            codigo.append("    imul eax, ebx")
        elif self.operador == '/':
            codigo.extend([
                "    mov edx, 0",
                "    cdq",
                "    idiv ebx"
            ])
        
        return "\n".join(codigo)

class NodoOperacionLogica(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"
    
    def generar_codigo(self):
        label_id = abs(hash(self)) % 1000
        
        codigo = [
            self.izquierda.generar_codigo(),
            "    push eax",
            self.derecha.generar_codigo(),
            "    mov ecx, eax",  
            "    pop eax",       
            "    cmp eax, ecx"   
        ]
        
        if self.operador == '==':
            codigo.append("    sete al")
        elif self.operador == '!=':
            codigo.append("    setne al")
        elif self.operador == '<':
            codigo.append("    setl al")
        elif self.operador == '<=':
            codigo.append("    setle al")
        elif self.operador == '>':
            codigo.append("    setg al")
        elif self.operador == '>=':
            codigo.append("    setge al")
        
        codigo.append("    movzx eax, al  ; Extender al a 32 bits")
        return "\n".join(codigo)

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"return {self.expresion.traducir()}"
    
    def generar_codigo(self):
        if self.expresion:
            expr_code = self.expresion.generar_codigo()
            return f"{expr_code}\n    jmp .return  ; Saltar a la etiqueta de retorno"
        else:
            return "    xor eax, eax\n    jmp .return  ; Saltar a la etiqueta de retorno con 0"

class NodoBreak(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"\tbreak"

    def generar_codigo(self):
        return "    jmp .nearest_loop_end ; break"

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
        
    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        if isinstance(self.nombre, tuple):
            var_name = self.nombre[1]
        else:
            var_name = self.nombre
        return f"    mov eax, [{var_name}] ; cargar variable {var_name}"

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return str(self.valor[1])
        
    def generar_codigo(self):
        if isinstance(self.valor, tuple):
            val = self.valor[1]
        else:
            val = self.valor
        return f"    mov eax, {val} ; cargar constante {val}"

class NodoBooleano(NodoAST):
    def __init__(self, valor):
        self.valor = valor

    def traducir(self):
        return str(self.valor[1]).capitalize()

    def generar_codigo(self):
        if isinstance(self.valor, tuple):
            val = self.valor[1].lower()
        else:
            val = str(self.valor).lower()
        return f"    mov eax, {1 if val == 'true' else 0} ; cargar booleano {val}"

class NodoLlamarFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
        
    def traducir(self):
        params = ", ".join(p.traducir() for p in self.argumentos)
        return f"{self.nombre[1]}({params})"
    
    def generar_codigo(self):
        codigo = []
        
        codigo.append("    push ebp  ; Guardar frame pointer")
        
        for arg in reversed(self.argumentos):
            codigo.append(arg.generar_codigo())
            codigo.append("    push eax")
        
        if isinstance(self.nombre, tuple):
            func_name = self.nombre[1]
        else:
            func_name = self.nombre
            
        codigo.append(f"    call {func_name}")
        
        if self.argumentos:
            codigo.append(f"    add esp, {4 * len(self.argumentos)}")
        
        codigo.append("    pop ebp  ; Restaurar frame pointer")
        return "\n".join(codigo)

class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return self.valor[1]
        
    def generar_codigo(self):
        return f'   mov eax, {self.valor[1]} ; cargar string'

class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        if self.tipo == 'int':
            return f"{self.nombre}: {self.tipo} = 0"
        elif self.tipo == 'float':
            return f"{self.nombre}: {self.tipo} = 0.00"
        else:
            return f"{self.nombre}: {self.tipo} = ''"
        
    def generar_codigo(self):
        if isinstance(self.nombre, tuple):
            var_name = self.nombre[1]
        else:
            var_name = self.nombre
        return f"    mov dword [{var_name}], 0 ; declarar {var_name}"

class NodoIf(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else if cuerpo_else else []
        
    def traducir(self):
        if_part = f"if {self.condicion.traducir()}:\n"
        if_part += "\n".join(f"\t\t{inst.traducir()}" for inst in self.cuerpo_if)
        
        if not self.cuerpo_else:
            return if_part
            
        else_part = "else:\n"
        else_part += "\n".join(f"\t\t{inst.traducir()}" for inst in self.cuerpo_else)
        
        return f"{if_part}\n{else_part}"

    def generar_codigo(self):
        label_id = abs(hash(self)) % 1000
        
        codigo = [
            "; === IF statement ===",
            self.condicion.generar_codigo(),
            "    test eax, eax",
            f"    jz .else_{label_id}"
        ]
        
        for inst in self.cuerpo_if:
            inst_code = inst.generar_codigo()
            if inst_code:
                codigo.append(inst_code)
        
        if self.cuerpo_else:
            codigo.append(f"    jmp .endif_{label_id}")
            codigo.append(f".else_{label_id}:")
            
            for inst in self.cuerpo_else:
                inst_code = inst.generar_codigo()
                if inst_code:
                    codigo.append(inst_code)
                    
            codigo.append(f".endif_{label_id}:")
        else:
            codigo.append(f".else_{label_id}:")
        
        return "\n".join(codigo)

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
        
    def traducir(self):
        cuerpo = "\n\t".join(inst.traducir() for inst in self.cuerpo)
        return f"while {self.condicion.traducir()}:\n\t\t{cuerpo}"
    
    def generar_codigo(self):
        label_id = abs(hash(self)) % 1000
        
        codigo = [
            "; === WHILE loop ===",
            f".while_start_{label_id}:"
        ]
        
        codigo.append(self.condicion.generar_codigo())
        codigo.extend([
            "    test eax, eax",
            f"    jz .while_end_{label_id}"
        ])
        
        for inst in self.cuerpo:
            inst_code = inst.generar_codigo()
            if inst_code:
                codigo.append(inst_code)
        
        codigo.extend([
            f"    jmp .while_start_{label_id}",
            f".while_end_{label_id}:"
        ])
        
        return "\n".join(codigo)

class NodoFor(NodoAST):
    def __init__(self, inicializacion, condicion, incremento, cuerpo):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo
        
    def traducir(self):
        init = self.inicializacion.traducir()
        cond = self.condicion.traducir()
        incr = self.incremento.rstrip(';')
        cuerpo = "\n\t".join(inst.traducir() for inst in self.cuerpo)
        return f"for ({init}; {cond}; {incr}):\n\t\t{cuerpo}"
    
    def generar_codigo(self):
        label_id = abs(hash(self)) % 1000

        codigo = [
            "; === FOR loop ===",
            self.inicializacion.generar_codigo(),
            f".for_cond_{label_id}:"
        ]
        
        codigo.append(self.condicion.generar_codigo())
        codigo.extend([
            "    test eax, eax",
            f"    jz .for_end_{label_id}"
        ])
        
        for inst in self.cuerpo:
            inst_code = inst.generar_codigo()
            if inst_code:
                codigo.append(inst_code)
        
        if "++" in self.incremento:
            var = self.incremento.replace("++", "").strip()
            codigo.extend([
                f"    ; Incremento {var}++",
                f"    mov eax, [{var}]",
                f"    inc eax",
                f"    mov [{var}], eax"
            ])
        elif "--" in self.incremento:
            var = self.incremento.replace("--", "").strip()
            codigo.extend([
                f"    ; Decremento {var}--",
                f"    mov eax, [{var}]",
                f"    dec eax",
                f"    mov [{var}], eax"
            ])
        
        codigo.extend([
            f"    jmp .for_cond_{label_id}",
            f".for_end_{label_id}:"
        ])
        
        return "\n".join(codigo)

class NodoPrintf(NodoAST):
    def __init__(self, argumentos, formato_str, verfTipo):
        self.argumentos = argumentos
        self.cadenaFormato = formato_str
        self.variables = verfTipo
        
    def traducir(self):
        import re

        variables = [nombre.nombre[1] for (nombre, _) in self.argumentos]
        partes = re.split(r'(%[dfscl])', self.cadenaFormato.strip('"'))

        resultado = []
        var_index = 0
        for parte in partes:
            if re.fullmatch(r'%[dfscl]', parte):
                if var_index < len(variables):
                    resultado.append(f"{{{variables[var_index]}}}")
                    var_index += 1
                else:
                    resultado.append(parte)
            else:
                resultado.append(parte)

        cuerpo = ''.join(resultado)
        return f'print(f"{cuerpo}")'
    
    def generar_codigo(self):
        codigo = []
        
        label_id = abs(hash(self)) % 10000
        
        for arg in self.variables:
            codigo.append(arg.generar_codigo())
            
            if isinstance(arg, NodoNumero) and '.' not in arg.valor[1]:
                codigo.extend([
                    "; Imprimir entero",
                    "    mov ecx, num_buffer",
                    "    call int_to_string",
                    "    mov edx, eax",      
                    "    mov eax, 4",        
                    "    mov ebx, 1",        
                    "    mov ecx, num_buffer",
                    "    int 0x80"
                ])
            elif isinstance(arg, NodoBooleano):
                codigo.extend([
                    "; Imprimir booleano",
                    "    test eax, eax",
                    f"    jz .print_false_{label_id}",
                    "    mov ecx, true_str",
                    "    mov edx, 4",   
                    f"    jmp .do_print_{label_id}",
                    f".print_false_{label_id}:",
                    "    mov ecx, false_str",
                    "    mov edx, 5",   
                    f".do_print_{label_id}:",
                    "    mov eax, 4",   
                    "    mov ebx, 1",   
                    "    int 0x80"
                ])
            elif isinstance(arg, NodoString):
                codigo.extend([
                    "; Imprimir string",
                    "    mov ecx, eax",  
                    "    call strlen",   
                    "    mov edx, eax",  
                    "    mov eax, 4",    
                    "    mov ebx, 1",    
                    "    ; ECX ya tiene la dirección del string",
                    "    int 0x80"
                ])
            elif isinstance(arg, NodoNumero) and '.' in arg.valor[1]:
                codigo.extend([
                    "; Imprimir flotante (usando conversión)",
                    "    sub esp, 8",          
                    "    fstp qword [esp]",    
                    "    push float_fmt",      
                    "    push float_buffer",   
                    "    call sprintf",        
                    "    add esp, 16",         
                    "    mov ecx, float_buffer",
                    "    call strlen",         
                    "    mov edx, eax",        
                    "    mov eax, 4",          
                    "    mov ebx, 1",          
                    "    mov ecx, float_buffer",
                    "    int 0x80"
                ])
                
        codigo.extend([
            "; Nueva línea",
            "    mov eax, 4",     
            "    mov ebx, 1",     
            "    mov ecx, newline",
            "    mov edx, 1",     
            "    int 0x80"
        ])
        
        return "\n".join(codigo)

class NodoScan(NodoAST):
    def __init__(self, argumentos):
        self.argumentos = argumentos
        
    def traducir(self):
        lineas = []

        for variable, tipo_dato in self.argumentos:
            if variable[0] == 'IDENTIFIER':
                if tipo_dato == str:
                    lineas.append(f"{variable[1]} = input()")
                else:
                    lineas.append(f"{variable[1]} = {tipo_dato.__name__}(input())")

        return '\n'.join(lineas)

    def generar_codigo(self):
        codigo = []
        
        for var, tipo in self.argumentos:
            if isinstance(var, tuple):
                var_name = var[1]
            else:
                var_name = var
                
            if tipo == 'int':
                codigo.extend([
                    f"; Leer entero en {var_name}",
                    f"    mov edi, {var_name}",
                    "    call read_int"
                ])
            elif tipo == 'float':
                codigo.extend([
                    f"; Leer flotante en {var_name} (implementación básica)",
                    "    mov eax, 3",        
                    "    mov ebx, 0",        
                    "    mov ecx, read_buffer",
                    "    mov edx, 64",       
                    "    int 0x80",
                    f"    ; Convertir a flotante y guardar en {var_name}",
                    "    ; Nota: Esta implementación es simplificada"
                ])
            elif tipo == 'string':
                codigo.extend([
                    f"; Leer string en {var_name}",
                    "    mov eax, 3",        
                    "    mov ebx, 0",        
                    f"    mov ecx, {var_name}",
                    "    mov edx, 64",       
                    "    int 0x80",
                ])
        
        return "\n".join(codigo)

class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre, expresion=None):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion
        
    def traducir(self):
        if self.expresion:
            return f"{self.nombre}: {self.tipo} = {self.expresion.traducir()};"
        if self.tipo == 'int':
            return f"{self.nombre}: {self.tipo} = 0"
        elif self.tipo == 'float':
            return f"{self.nombre}: {self.tipo} = 0.00"
        else:
            return f"{self.nombre}: {self.tipo} = ''"
        
    def generar_codigo(self):
        if self.expresion:
            codigo = self.expresion.generar_codigo()
            if isinstance(self.nombre, tuple):
                var_name = self.nombre[1]
            else:
                var_name = self.nombre
            return codigo + f"\n    mov [{var_name}], eax ; inicializar {var_name}"
        else:
            if isinstance(self.nombre, tuple):
                var_name = self.nombre[1]
            else:
                var_name = self.nombre
            return f"    mov dword [{var_name}], 0 ; declarar {var_name}"