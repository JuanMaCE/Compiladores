class NodoAST:
    countermsg=1
    hay_float = False
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
            "%include 'io.asm'",
            "%include 'mathop.asm'",
            "",
            "section .data",
            "    newline db 10, 0",
            "    true_str db 'True', 0",
            "    num_buffer times 20 db 0"
        ]
        i=1
        for var in reversed(list(variables)):
            if var.startswith('"') and var.endswith('"'):
                if '%' not in var:
                    codigo.append(f"    msg_{i} db {var}, 0")
                    i+=1

        codigo.extend([
            "",
            "section .bss"
        ])

        for var in variables:
            if var.startswith('"') and var.endswith('"'):
                continue
            else:
                codigo.append(f"    {var} resd 1")
            
        codigo.extend([
            "",
            "section .text",
            "    global main",
            ""
        ])
        
        for funcion in self.funciones:
            codigo.append(funcion.generar_codigo())
        
        return "\n".join(codigo)

    def _collect_variables(self, node):
        variables = set()
        if isinstance(node, NodoString):
            variables.add(node.valor[1])
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
        
        if self.nombre == 'main':
            local_vars = sum(1 for inst in self.cuerpo if isinstance(inst, NodoDeclaracion))
            if local_vars > 0:
                codigo.append(f"    sub esp, {4 * local_vars}")
        for inst in self.cuerpo:
            inst_code = ''
            if self.tipo[1]=='float':
                self.__class__.hay_float = True
            if isinstance(inst, NodoRetorno):
                inst_code = inst.generar_codigo(self.tipo[1])
            elif isinstance(inst, NodoOperacion):
                inst_code = inst.generar_codigo(self.tipo[1])
            elif isinstance(inst, NodoAsignacion):
                if self.__class__.hay_float:
                    inst_code = inst.generar_codigo('float')
                    self.__class__.hay_float = False
                else:
                    inst_code = inst.generar_codigo()
            else:
                inst_code = inst.generar_codigo()
            if inst_code:
                codigo.append(inst_code)
        
        if self.nombre == "main":
            codigo.extend([
                "    ; Terminar programa",
                "    call exit_program"
            ])
            return "\n".join(codigo)
        
        return "\n".join(codigo)

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return f"{self.nombre}: {self.tipo}"
    
    def generar_codigo(self):
        return f"; Parámetro: {self.tipo} {self.nombre}"

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre 
        self.expresion = expresion
        
    def traducir(self):
        return f"{self.nombre[1]} = {self.expresion.traducir()}"
    
    def generar_codigo(self, tipo='int'):
        var_name = self.nombre[1] if isinstance(self.nombre, tuple) else self.nombre
        if tipo == 'float':
            return f"{self.expresion.generar_codigo()}\n    fstp dword [{var_name}]"
        return f"{self.expresion.generar_codigo()}\n    mov [{var_name}], eax  ; asignar a {var_name}"

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"

    def generar_codigo(self, tipo='int'):
        codigo = []
        if tipo == 'float':
            codigo.append(f"    call suma_floats")
            return "\n".join(codigo)
        if isinstance(self.izquierda, NodoIdentificador):
            var_name = self.izquierda.nombre[1] if isinstance(self.izquierda.nombre, tuple) else self.izquierda.nombre
            codigo.append(f"    mov eax, [ebp+8]")
        else:
            codigo.append(self.izquierda.generar_codigo())
            codigo.append("    push eax")
        
        if isinstance(self.derecha, NodoIdentificador):
            var_name = self.derecha.nombre[1] if isinstance(self.derecha.nombre, tuple) else self.derecha.nombre
            codigo.append(f"")
        else:
            codigo.append(self.derecha.generar_codigo())
            codigo.append("    mov ebx, eax")
            codigo.append("    pop eax")
        
        if self.operador == '+':
            codigo.append("    add eax, [ebp+12]")
        elif self.operador == '-':
            codigo.append("    sub eax, [ebp+12]")
        elif self.operador == '*':
            codigo.append("    imul eax, [ebp+12]")
        elif self.operador == '/':
            codigo.extend([
                "    cdq           ; Extender EAX a EDX:EAX",
                "    idiv ebx      ; Dividir EDX:EAX por EBX"
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
        codigo = [
            self.izquierda.generar_codigo(),
            f"    cmp eax, {self.derecha.valor[1]}"
        ]
        
        set_instructions = {
            '==': "    sete al",
            '!=': "    setne al",
            '<': "    setl al",
            '<=': "    setle al",
            '>': "    setg al",
            '>=': "    setge al"
        }
        
        codigo.append(set_instructions[self.operador])
        
        return "\n".join(codigo)

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"return {self.expresion.traducir()}"
    
    def generar_codigo(self, tipo='int'):
        if isinstance(self.expresion, NodoNumero):
            if self.expresion and self.expresion.valor[1] == '0':
                return ''
            if self.expresion:
                expr_code = self.expresion.generar_codigo()
                return f"{expr_code}\n    mov esp, ebp\n    pop ebp\n    ret  ; Saltar a la etiqueta de retorno"
            else:
                return "    xor eax, eax\n    ret  ; Saltar a la etiqueta de retorno con 0"
        else:
            if self.expresion:
                expr_code = self.expresion.generar_codigo(tipo) if isinstance(self.expresion, NodoOperacion) else self.expresion.generar_codigo()
                if tipo == 'float':
                    return f"{expr_code}\n    pop ebp\n    ret  ; Saltar a la etiqueta de retorno"
                return f"{expr_code}\n    mov esp, ebp\n    pop ebp\n    ret  ; Saltar a la etiqueta de retorno"
            else:
                return "    xor eax, eax\n    ret  ; Saltar a la etiqueta de retorno con 0"

class NodoBreak(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"\tbreak"

    def generar_codigo(self):
        return "    jmp .nearest_loop_end  ; break (32 bits)"

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
        
    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        var_name = self.nombre[1] if isinstance(self.nombre, tuple) else self.nombre
        return f"    mov eax, [{var_name}]  ; cargar variable {var_name}"

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return str(self.valor[1])
        
    def generar_codigo(self):
        val = self.valor[1] if isinstance(self.valor, tuple) else self.valor
        if '.' in str(val):
            return f"""
        push dword {val.split('.')[1]}  ; Parte decimal
        push dword {val.split('.')[0]}  ; Parte entera
        fild dword [esp]     ; Cargar parte entera
        fild dword [esp+4]   ; Cargar parte decimal
        faddp                ; Sumar (ST0 = valor)
        add esp, 8           ; Limpiar stack
        ; El float queda en ST0"""
        else:
            return f"    mov eax, {val}  ; cargar entero {val} (32 bits)"

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
        
        return f"""
        mov eax, {1 if val == 'true' else 0}  ; Cargar {val} en EAX (32 bits)
        ; (1 = true, 0 = false)"""

class NodoLlamarFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
        
    def traducir(self):
        params = ", ".join(p.traducir() for p in self.argumentos)
        return f"{self.nombre[1]}({params})"
    
    def generar_codigo(self):
        codigo = []
        param_registers = ['edi', 'esi', 'edx', 'ecx', 'e8', 'e9']
        
        for i, arg in enumerate(self.argumentos):
            if i < 6:
                codigo.append(f"    push dword [{arg.nombre[1]}]")
        
        func_name = self.nombre[1] if isinstance(self.nombre, tuple) else self.nombre
        codigo.append(f"    call {func_name}")
        
        codigo.append(f"    add esp, {4 * (len(self.argumentos))}  ; limpiar stack")
        
        return "\n".join(codigo)

class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return self.valor[1]
        
    def generar_codigo(self):
        return f''

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
            "; === IF statement (32 bits) ===",
            self.condicion.generar_codigo(),
            "    test eax, eax",
            f"    jz .else_{label_id}"
        ]
        
        for inst in self.cuerpo_if:
            if inst_code := inst.generar_codigo():
                codigo.append(inst_code)
        
        if self.cuerpo_else:
            codigo.append(f"    jmp .endif_{label_id}")
            codigo.append(f".else_{label_id}:")
            
            for inst in self.cuerpo_else:
                if inst_code := inst.generar_codigo():
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
            f"; === WHILE loop (32 bits) ===",
            f".while_start_{label_id}:",
            self.condicion.generar_codigo(),
            "    test al, al               ; Verificar AL",
            f"    jz .while_end_{label_id} ; Saltar si es falso",
        ]
        
        for inst in self.cuerpo:
            if inst_code := inst.generar_codigo():
                codigo.append(inst_code)
        
        codigo.extend([
            f"    jmp .while_start_{label_id} ; Repetir",
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
            "    test rax, rax",
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
                f"    mov rax, [{var}]",
                f"    inc rax",
                f"    mov [{var}], rax"
            ])
        elif "--" in self.incremento:
            var = self.incremento.replace("--", "").strip()
            codigo.extend([
                f"    ; Decremento {var}--",
                f"    mov rax, [{var}]",
                f"    dec rax",
                f"    mov [{var}], rax"
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
        self.i = 1
        
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
            if isinstance(arg, NodoIdentificador):
                tip = 'str'
                for v, tipo in self.argumentos:
                    print(tipo)
                    if isinstance(v, NodoIdentificador):
                        if v.nombre[1] == arg.nombre[1]:
                            tip = tipo.__name__
                if tip == 'int':
                    codigo.append(f"    push dword [{arg.nombre[1]}]\n    call print_int\n    add esp, 4")
                elif tip == 'float':
                    codigo.append(f"    sub esp, 8\n    fld dword [{arg.nombre[1]}]\n    fstp qword [esp]\n    call print_float\n    add esp, 8")
                elif tip == 'bool':
                    codigo.extend([
                        "    ; Imprimir booleano",
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
                else:
                    codigo.extend([
                        "    ; Imprimir String",
                        f"    push {arg.nombre[1]}",
                        "    call print_string",
                        "    add esp, 4"
                    ])
            elif isinstance(arg, NodoNumero) and '.' not in arg.valor[1]:
                codigo.append(f"    push dword [{arg.valor[1]}]\n    call print_int\n    add esp, 4")
            elif isinstance(arg, NodoBooleano):
                codigo.extend([
                    "    ; Imprimir booleano",
                    "    test eax, eax",
                    f"    jz .print_false_{label_id}",
                    "    mov ecx, true_str",
                    "    mov edx, 4",   # Longitud de 'True'
                    f"    jmp .do_print_{label_id}",
                    f".print_false_{label_id}:",
                    "    mov ecx, false_str",
                    "    mov edx, 5",   # Longitud de 'False'
                    f".do_print_{label_id}:",
                    "    mov eax, 4",   # syscall write
                    "    mov ebx, 1",   # stdout
                    "    int 0x80"
                ])
            elif isinstance(arg, NodoString):
                if '%' not in arg.valor[1]:
                    codigo.extend([
                            "    ; Imprimir String",
                            f"    push msg_{self.__class__.countermsg}",
                            "    call print_string",
                            "    add esp, 4"
                        ])
                    self.__class__.countermsg+=1
            elif isinstance(arg, NodoNumero) and '.' in arg.valor[1]:
                codigo.append(f"    sub esp, 8\n    fld dword [{arg.valor[1]}]\n    fstp qword [esp]\n    call print_float\n    add esp, 8")
                
        codigo.extend([
            "    ; Nueva línea",
            "    push newline",
            "    call print_string",
            "    add esp, 4"
        ])
        
        return "\n".join(codigo)

class NodoScan(NodoAST):
    def __init__(self, argumentos, verfTipo):
        self.argumentos = argumentos
        self.variab = verfTipo
        
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
        
        for var in self.variab:
            if isinstance(var, NodoNumero) and '.' not in var.valor[1]:
                codigo.extend([
                    f"    ; Leer entero en {var.valor[1]}",
                    "    call read_int",
                    f"    mov [{var.valor[1]}], eax"
                ])
            elif isinstance(var, NodoNumero) and '.' in var.valor[1]:
                codigo.extend([
                    f"    ; Leer flotante en {var.valor[1]} (implementación básica)",
                    "    call read_float",
                    f"    fstp dword [{var.valor[1]}]"
                ])
            elif isinstance(var, NodoIdentificador):
                tip = 'str'
                for v, tipo in self.argumentos:
                    if v[1] == var.nombre[1]:
                        tip = tipo.__name__
                if tip == 'int':
                    codigo.append(f"    call read_int\n    mov [{var.nombre[1]}], eax")
                elif tip == 'float':
                    codigo.append(f"    call read_float\n    fstp dword [{var.nombre[1]}]")
                else:
                    codigo.extend([
                        f"    ; Leer string en {var.nombre[1]}",
                        f"    push dword {var.nombre[1]}",
                        f"    call read_string"
                        f"    add esp, 4"
                    ])
        
        return "\n".join(codigo)

class NodoIncremento(NodoAST):
    def __init__(self, var, incremento):
        self.var = var
        self.incremento = incremento
    
    def traducir(self):
        return f'{self.var+self.incremento}'
    
    def generar_codigo(self):
        if self.incremento == '++':
            return f'    inc dword [{self.var}]'
        elif self.incremento == '--':
            return f'    dec dword [{self.var}]'

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