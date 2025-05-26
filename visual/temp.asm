; === Programa Generado ===
%include 'io.asm'
%include 'mathop.asm'

section .data
    newline db 10, 0
    true_str db 'True', 0
    num_buffer times 20 db 0

section .bss
    a resd 1
    resultado resd 1
    b resd 1

section .text
    global main

; === Función: main ===
main:
    push ebp
    mov ebp, esp
    sub esp, 12
    mov dword [a], 0 ; declarar a
    mov dword [b], 0 ; declarar b
    mov dword [resultado], 0 ; declarar resultado
    call read_int
    mov [a], eax
    call read_int
    mov [b], eax
    mov eax, [ebp+8]

    add eax, [ebp+12]
    mov [resultado], eax  ; asignar a resultado
    push dword [resultado]
    call print_int
    add esp, 4
    ; Nueva línea
    push newline
    call print_string
    add esp, 4
    ; Terminar programa
    call exit_program