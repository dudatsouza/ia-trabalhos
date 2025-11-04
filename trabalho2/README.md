[vscode-badge]: https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white
<a name="readme-topo"></a>

<h1 align='center'>
  Trabalho 2 - Busca Local no Problema das 8 Rainhas
</h1>

<div align='center'>

[![SO][Ubuntu-badge]][Ubuntu-url]
[![IDE][vscode-badge]][vscode-url]
[![Python][Python-badge]][Python-url]

<b>
  Guilherme Alvarenga de Azevedo<br>
  Maria Eduarda Teixeira Souza<br>
</b>

Inteligência Artificial <br>
Engenharia de Computação <br>
CEFET-MG Campus V <br>
2025/2

</div>

## 📚 O Projeto

Neste repositório você encontrará o código-fonte do Trabalho 2, que implementa e compara variantes de busca local aplicadas ao problema das 8 rainhas (Hill Climbing, Sideways Moves, Random Restarts e Simulated Annealing).

O projeto foi desenvolvido em Python e inclui: implementações dos algoritmos, utilitários para medir tempo e memória, geração de GIFs de visualização e scripts para comparação e plotagem de métricas.

O relatório do trabalho está disponível em `trabalho2/relatorio.pdf`.

De forma organizada, os arquivos e diretórios do trabalho2 seguem a estrutura abaixo:

```
trabalho2/
├── pyproject.toml
├── README.md
├── relatorio.pdf
├── data/
│   └── output/
│       ├── graphics/
│       │   └── hill_climbing/
│       └── metrics/
│           └── metrics_hill_climbing.json
└── src/
    ├── core/                 # representação do problema (8 rainhas)
    ├── local_search/         # hill_climbing, sideways_moves, random_restarts, simulated_annealing
    ├── comparisons/          # compare_hill_climbing.py, hill_climbing_plots.py
    ├── tools/                # main.py (CLI), run_gui.py (GUI), measure_time_memory.py
    └── visualization/        # geração de GIFs (queen_gif.py)
```

## Instalando
Para instalar e executar o Trabalho 2, siga os passos abaixo.

1. Clone o repositório no diretório desejado:

```console
git clone https://github.com/dudatsouza/ia-trabalhos.git
cd ia-trabalhos/trabalho2
```

2. Crie e ative um ambiente virtual (recomendado) - garanta que já possui o [Python](https://www.python.org/downloads/), no mínimo na versão 3.11.9:
  ```console
  python3 -m venv venv
  source venv/bin/activate   # Linux/macOS
  venv\Scripts\activate      # Windows
  ```

  3. Instale as dependências do Poetry - garanta que possui o [Poetry](https://python-poetry.org/docs/) instalado: 
  ```console
    poetry install
  ```

  3.1. Alternativamente, instale as dependências com pip: 
  ```console
    pip install -r requirements.txt
  ```

  4. Caso você não tenha o `tkinter` instalado (necessário para a interface gráfica), instale manualmente:
  ```console
    sudo apt-get install python3-tk # Linux (Debian/Ubuntu) 
  ```
</div>

  > [!TIP]
  > Windows e macOS: o tkinter já vem incluso na instalação do Python.

<div align="justify">
  
  5. Execute o programa:
    - Com GUI (`run_gui.py`)
      - **Linux/macOS**
        ```console
          Usando Python diretamente
          PYTHONPATH='src' python3 -m tools.run_gui
        ```
        
        ```console
          Usando Poetry
          poetry run python src/tools/run_gui.py
        ```

      - **Windows** 
        ```console
          Usando Python diretamente
          set PYTHONPATH=src && python -m tools.run_gui
        ```
          
        ```console
          Usando Poetry
          poetry run python src/tools/run_gui.py
        ```

      ### Sem GUI (`main.py`)

      - **Linux/macOS**
        ```console
          # Usando Python diretamente
          # PYTHONPATH='src' python3 -m tools.main
        ```
          
        ```console
          # Usando Poetry
          # poetry run python src/tools/main.py
        ```

      - **Windows**
        ```console
          # Usando Python diretamente
          # set PYTHONPATH=src && python -m tools.main
        ```
        
        ```console
          # Usando Poetry
          # poetry run python src/tools/main.py
        ```
</div> 

  > [!NOTE]
  > Caso estaja usando o PowerShell subistitua o operador `&&` por `;`

<div align="justify">
  
  ## Dependências

  O projeto utiliza as seguintes bibliotecas:

  - matplotlib
  - tkinter (já incluso no Python, instalar manualmente se necessário)
    
</div>

> [!NOTE]
> No arquivo [`requirements.txt`](trabalho1/requirements.txt) tem todas essas informações.

## 🧪 Ambiente de Compilação e Execução

O trabalho foi desenvolvido e testado no Ubuntu e em ambiente local com as seguintes especificações de referência:

| Hardware | Especificações |
|:-------:|:---------------:|
| Laptop | Dell Inspiron 13 5330 |
| Processador | Intel Core i7-1360P |
| Memória RAM | 16 GB |
| Sistema Operacional | Ubuntu 24.04 |
| IDE | Visual Studio Code |

> [!IMPORTANT] 
> Para que os testes tenham validade, considere as especificações
> do ambiente de compilação e execução do programa.

<p align="right">(<a href="#readme-topo">voltar ao topo</a>)</p>

## 📨 Contato

<div align="center">
  <br><br>
     <i>Guilherme Alvarenga de Azevedo - Graduando - 6º Período de Engenharia de Computação @ CEFET-MG</i>
  <br><br>
  
  [![Gmail][gmail-badge]][gmail-autor1]
  [![Linkedin][linkedin-badge]][linkedin-autor1]
  [![Telegram][telegram-badge]][telegram-autor1]
  
  
  <br><br>
     <i>Maria Eduarda Teixeira Souza - Graduando - 6º Período de Engenharia de Computação @ CEFET-MG</i>
  <br><br>
  
  [![Gmail][gmail-badge]][gmail-autor2]
  [![Linkedin][linkedin-badge]][linkedin-autor2]
  [![Telegram][telegram-badge]][telegram-autor2]

</div>

<p align="right">(<a href="#readme-topo">voltar ao topo</a>)</p>

<a name="referencias">📚 Referências</a>

1. AZEVEDO, Guilherme A. SOUZA, Maria E. T. **IA-Trabalhos**: Trabalho 1 - Labirinto. 2025. Disponível em: [https://github.com/dudatsouza/ia-trabalhos](https://github.com/dudatsouza/ia-trabalhos) Acesso em: 19 out. 2025.

2. OLIVEIRA, Tiago A. **Inteligência Artificial 04**: Estruturas e Estratégias de Busca - Busca em Ambientes Complexos. Slides de Aula. 2025.

3. RUSSELL, Stuart J; NORVIG, Peter. **Inteligência Artificial: Uma Abordagem Moderna**. 4. ed. Pearson, 2021.

[vscode-badge]: https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white
[vscode-url]: https://code.visualstudio.com/docs/?dv=linux64_deb
[make-badge]: https://img.shields.io/badge/_-MAKEFILE-427819.svg?style=for-the-badge
[make-url]: https://www.gnu.org/software/make/manual/make.html
[cpp-badge]: https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white
[cpp-url]: https://en.cppreference.com/w/cpp
[trabalho-url]: https://drive.google.com/file/d/1-IHbGaA1BIC6_CMBydOC-NbV2bCERc8r/view?usp=sharing
[github-prof]: https://github.com/mpiress
[main-ref]: src/main.cpp
[branchAMM-url]: https://github.com/alvarengazv/trabalhosAEDS1/tree/AlgoritmosMinMax
[makefile]: ./makefile
[bash-url]: https://www.hostgator.com.br/blog/o-que-e-bash/
[lenovo-badge]: https://img.shields.io/badge/lenovo%20laptop-E2231A?style=for-the-badge&logo=lenovo&logoColor=white
[ubuntu-badge]: https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white
[Ubuntu-url]: https://ubuntu.com/
[ryzen5500-badge]: https://img.shields.io/badge/AMD%20Ryzen_5_5500U-ED1C24?style=for-the-badge&logo=amd&logoColor=white
[ryzen3500-badge]: https://img.shields.io/badge/AMD%20Ryzen_5_3500X-ED1C24?style=for-the-badge&logo=amd&logoColor=white
[windows-badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white
[gcc-badge]: https://img.shields.io/badge/GCC-5C6EB8?style=for-the-badge&logo=gnu&logoColor=white
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/


[linkedin-autor1]: https://www.linkedin.com/in/guilherme-alvarenga-de-azevedo-959474201/
[telegram-autor1]: https://t.me/alvarengazv
[gmail-autor1]: mailto:gui.alvarengas234@gmail.com

[linkedin-autor2]: https://www.linkedin.com/in/dudatsouza/
[telegram-autor2]: https://t.me/dudat_18
[gmail-autor2]: mailto:dudateixeirasouza@gmail.com

[linkedin-badge]: https://img.shields.io/badge/-LinkedIn-0077B5?style=for-the-badge&logo=Linkedin&logoColor=white
[telegram-badge]: https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[gmail-badge]: https://img.shields.io/badge/-Gmail-D14836?style=for-the-badge&logo=Gmail&logoColor=white