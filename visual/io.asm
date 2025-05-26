; io.asm - Versión 32 bits
section .data
    ; Formatos para printf
    fmt_int      db "%d", 0
    fmt_float    db "%.2f", 0
    fmt_string   db "%s", 0
    fmt_newline  db 10, 0
    
    ; Formatos para scanf
    scan_int     db "%d", 0
    scan_float   db "%f", 0
    scan_string  db "%63s", 0

section .text
    extern printf, scanf, exit

global print_int
print_int:
    push ebp
    mov ebp, esp
    
    push dword [ebp+8]  ; Valor a imprimir
    push fmt_int        ; Formato
    call printf
    add esp, 8          ; Limpiar stack
    
    pop ebp
    ret

global print_float
print_float:
    push ebp
    mov ebp, esp
    
    sub esp, 8          ; Espacio para double
    fld dword [ebp+8]   ; Cargar float
    fstp qword [esp]    ; Guardar como double
    
    push fmt_float      ; Formato
    call printf
    add esp, 12         ; Limpiar stack
    
    pop ebp
    ret

global print_string
print_string:
    push ebp
    mov ebp, esp
    
    push dword [ebp+8]  ; Puntero al string
    push fmt_string     ; Formato
    call printf
    add esp, 8          ; Limpiar stack
    
    pop ebp
    ret

global print_newline
print_newline:
    push ebp
    mov ebp, esp
    
    push fmt_newline
    call print_string
    add esp, 4
    
    pop ebp
    ret

global read_int
read_int:
    push ebp
    mov ebp, esp
    sub esp, 16         ; Espacio para variables locales
    
    lea eax, [ebp-4]
    push eax            ; Dirección donde guardar
    push scan_int       ; Formato
    call scanf
    add esp, 8
    
    mov eax, [ebp-4]    ; Retornar valor leído
    add esp, 16
    pop ebp
    ret

global read_float
read_float:
    push ebp
    mov ebp, esp
    sub esp, 8           ; Solo necesitamos 4 bytes, pero alineamos a 8 por seguridad
    
    ; Llamada a scanf("%f", &temp)
    lea eax, [ebp-4]     ; Dirección del float temporal (4 bytes)
    push eax
    push scan_float       ; Formato "%f"
    call scanf
    add esp, 8           ; Limpiar parámetros
    
    ; Cargar resultado a FPU
    fld dword [ebp-4]    ; ST0 = valor leído
    
    mov esp, ebp         ; Optimización: limpiamos el stack con ebp
    pop ebp
    ret

global read_string
read_string:
    push ebp
    mov ebp, esp
    
    push dword [ebp+8]  ; Buffer
    push scan_string
    call scanf
    add esp, 8
    
    push dword [ebp+8]  ; Calcular longitud
    call strlen
    add esp, 4
    
    pop ebp
    ret

global exit_program
exit_program:
    mov eax, 1          ; syscall exit (32 bits)
    xor ebx, ebx        ; código 0
    int 0x80

strlen:
    push ebp
    mov ebp, esp
    mov ecx, [ebp+8]    ; Puntero al string
    xor eax, eax        ; Contador
    
.loop:
    cmp byte [ecx+eax], 0
    je .done
    inc eax
    jmp .loop
    
.done:
    pop ebp
    ret