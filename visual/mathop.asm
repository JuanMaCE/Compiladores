section .text

; Suma de enteros (32 bits)
; Parámetros: [ebp+8] = a, [ebp+12] = b
; Retorna: eax = a + b
global suma_enteros
suma_enteros:
    push ebp
    mov ebp, esp
    
    mov eax, [ebp+8]    ; Cargar primer parámetro (a)
    add eax, [ebp+12]   ; Sumar segundo parámetro (b)
    
    pop ebp
    ret

; Suma de floats (32 bits)
; Parámetros: ST0 = a, ST1 = b (pila FPU)
; Retorna: ST0 = a + b
global suma_floats
suma_floats:
    push ebp
    mov ebp, esp
    
    fld dword [ebp+8]   ; Cargar primer float (a) a ST0
    fadd dword [ebp+12] ; Sumar segundo float (b) a ST0
    
    pop ebp
    ret

; Suma de doubles (64 bits)
; Parámetros: ST0 = a, ST1 = b (pila FPU)
; Retorna: ST0 = a + b
global suma_doubles
suma_doubles:
    push ebp
    mov ebp, esp
    
    fld qword [ebp+8]   ; Cargar primer double (a) a ST0
    fadd qword [ebp+16] ; Sumar segundo double (b) a ST0
    
    pop ebp
    ret