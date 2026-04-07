# Notas de Estudo - Argentum Core

## 1. Injeção de Dependência (DI)
No `ArgentumEngine`, o provedor de dados (`TelemetryProvider`) é injetado via construtor. 
- **Benefício:** Podemos trocar o `MockData` pelo `AssettoCorsaProvider` sem alterar a lógica de loop ou a UI.
- **Conceito:** "Programar para interfaces, não para implementações".

## 2. Comunicação entre Processos (IPC) e Shared Memory
O Assetto Corsa utiliza **Memory Mapped Files**. 
- O jogo reserva um bloco de memória RAM.
- O Python "espelha" esse bloco como um objeto acessível.
- **Vantagem:** Latência quase zero. Não há overhead de rede (TCP/UDP).

## 4. O Sucesso da Conexão (Lições Aprendidas)
A conexão com o Assetto Corsa funciona através de **Memory Mapping**.
- **acphysics:** Dados voláteis (60Hz).
- **acstatic:** Dados de configuração (identidade).

### Decodificação de Strings (UTF-16)
O AC armazena nomes como `wchar_t`. No Python, isso exige:
```python
name_bytes.decode('utf-16').split('\0')[0]
```
Isso remove os caracteres nulos (`\0`) que o C++ usa para terminar strings, evitando sujeira visual no Python.
