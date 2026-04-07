# 🗺️ Roadmap: Fundamentos de C++ (Silver Arrow)

Este guia foca nos alicerces sólidos de C++ necessários para dominar sistemas embarcados (ESP32) e lógica de alta performance.

---

## 🏗️ Nível 1: O Alicerce (Sintaxe e Tipos)
- [ ] **Variáveis e Tipos Primitivos**: `int`, `float`, `double`, `bool`, `char`. Diferença entre `uint8_t` (comum em drivers) e `int`.
- [ ] **Controle de Fluxo**: `if`, `else`, `switch`, `for`, `while`, `do-while`.
- [ ] **Funções**: Declaração vs Definição, Escopo de variáveis e Parâmetros.
- [ ] **Arrays e Strings em C**: Manipulação de buffers e por que evitar `String` no Arduino (fragmentação de memória).

---

## 🧠 Nível 2: O Cérebro do C++ (Ponteiros e Memória)
- [ ] **Ponteiros (`*`)**: Endereços de memória, desreferenciação e aritimética de ponteiros.
- [ ] **Referências (`&`)**: Passagem de parâmetros por referência (eficiência).
- [ ] **Memória Dinâmica**: `new` e `delete` (e por que quase nunca usá-los em microcontroladores).
- [ ] **Stack vs Heap**: Entender onde suas variáveis vivem.

---

## 📦 Nível 3: Organização (Orientação a Objetos)
- [ ] **Classes e Objetos**: Encapsulamento de drivers de hardware.
- [ ] **Construtores e Destrutores**: Inicialização de periféricos (SPI, I2C).
- [ ] **Herança e Polimorfismo**: Criação de uma interface genérica para "Sensores" ou "Displays".
- [ ] **Namespaces**: Evitar colisão de nomes em projetos grandes.

---

## ⚡ Nível 4: C++ Moderno e Hardware
- [ ] **Templates**: Funções genéricas para diferentes tipos de dados de sensores.
- [ ] **Smart Pointers**: `unique_ptr` e `shared_ptr` (para gerenciamento seguro de recursos).
- [ ] **Const e Constexpr**: Otimização de constantes em tempo de compilação (salva espaço no Flash).
- [ ] **Lambdas e Callbacks**: Tratamento assíncrono de interrupções (ISRs).

---

### 📚 Recursos Recomendados
1. **[LearnCpp.com](https://learncpp.com/)**: O melhor recurso gratuito do mundo para C++.
2. **[Hacking C++](https://hackingcpp.com/)**: Visualizações gráficas fantásticas de conceitos complexos.
3. **The C++ Programming Language** (Bjarne Stroustrup): A bíblia do criador da linguagem.

> [!TIP]
> No Project Silver Arrow, seu melhor aliado é o `sizeof()`. Sempre saiba quanto espaço seus dados ocupam na RAM limitada do ESP32!
