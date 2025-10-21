<a name="readme-topo"></a>

<h1 align='center'>
  Trabalho 1 -  Labirinto
</h1>

<div align='center'>

[![SO][Ubuntu-badge]][Ubuntu-url]
[![IDE][vscode-badge]][vscode-url]
[![Python][Python-badge]][Python-url]

<b>
  Guilherme Alvarenga de Azevedo<br>
  Maria Eduarda Teixeira Souza<br>
</b>
  
<br>
Inteligência Artificial <br>
Engenharia de Computação <br>
CEFET-MG Campus V <br>
2025/2 


</div>

## 📚 O Projeto

Neste repositório você encontrará o código fonte do projeto, bem como os dados utilizados para a análise. O projeto foi desenvolvido em Python. Este trabalho também tem a produção de um PDF para relatar o trabalho, que está disponível em [`Relatório 1`](trabalho1/relatorio.pdf) e [`Relatório 2`](trabalho2/relatorio.pdf).

De uma forma compacta e organizada, os arquivos e diretórios estão dispostos da seguinte forma:

  ```.
ai-trabalhos/
└── trabalho1/
    ├── data/
    │   ├── input/
    │   │   └── maze.txt
    │   ├── output/
    │   │   ├── graphics/
    │   │   │   ├── informed/
    │   │   │   │   ├── informed_avg_cost_by_heuristic.png
    │   │   │   │   ├── informed_avg_nodes_by_heuristic.png
    │   │   │   │   └── ... (e outros .png)
    │   │   │   └── uninformed/
    │   │   │       ├── uninformed_avg_cost.png
    │   │   │       ├── uninformed_avg_nodes.png
    │   │   │       └── ... (e outros .png)
    │   │   ├── metrics/
    │   │   │   ├── metrics_informed.json
    │   │   │   └── metrics_uninformed.json
    │   │   └── visualization/
    │   │       ├── informed/
    │   │       │   ├── visualization-a-star-chebyshev.gif
    │   │       │   ├── visualization-a-star-euclidean.gif
    │   │       │   └── ... (e outros .gif)
    │   │       └── uninformed/
    │   │           ├── visualization-bidirectional.gif
    │   │           └── visualization-dijkstra.gif
    │   |
    ├── src/
    │   ├── comparisons/
    │   │   ├── informed_plots.py
    │   │   └── uninformed_plots.py
    │   ├── core/
    │   │   ├── heuristics.py
    │   │   ├── maze_generator.py
    │   │   ├── maze_problem.py
    │   │   ├── maze_representation.py
    │   │   ├── node.py
    │   │   └── problem.py
    │   ├── informed/
    │   │   ├── a_star_search.py
    │   │   ├── generate_gifs_informed.py
    │   │   └── greedy_best_first_search.py
    │   ├── search/
    │   │   ├── measure_time_memory.py
    │   │   └── visualize_matrix.py
    │   ├── tools/
    │   │   ├── main.py
    │   │   └── run_gui.py
    │   └── uninformed/
    │       ├── best_first_search.py
    │       ├── bidirectional_best_first_search.py
    │       ├── dijkstra.py
    │       └── generate_gifs_uninformed.py
    ├── .gitignore
    ├── poetry.lock
    ├── pyproject.toml
    ├── README.md
    ├── relatorio.pdf
    └── requirements.txt
  ```

## Instalando
Para instalar o projeto, siga os passos abaixo:

<div align="justify">
  Com o ambiente preparado, os seguintes passos são para a instalação, compilação e execução do programa localmente:

  1. Clone o repositório no diretório desejado:
  ```console
  git clone https://github.com/dudatsouza/ia-trabalhos.git
  cd ia-trabalhos/trabalho1
  ```
  2. Crie e ative um ambiente virtual (recomendado):
  ```console
  python3 -m venv venv
  source venv/bin/activate   # Linux/macOS
  venv\Scripts\activate      # Windows
  ```

  3. Instale as dependências do Poetry: 
  ```console
    poetry install
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
          poetry run python -m tools.run_gui
        ```

      - **Windows** 
        ```console
          Usando Python diretamente
          set PYTHONPATH=src && python -m tools.run_gui
        ```
          
        ```console
          Usando Poetry
          poetry run python -m tools.run_gui
        ```

      ### Sem GUI (`main.py`)

      - **Linux/macOS**
        ```console
          # Usando Python diretamente
          # PYTHONPATH='src' python3 -m tools.main
        ```
          
        ```console
          # Usando Poetry
          # poetry run python -m tools.main
        ```

      - **Windows**
        ```console
          # Usando Python diretamente
          # set PYTHONPATH=src && python -m tools.main
        ```
        
        ```console
          # Usando Poetry
          # poetry run python -m tools.main
        ```
</div> 

  > [!NOTE]
  > Caso estaja usando o PowerShell subistitua o operador `&&` por `;`

<div align="justify">
  
  ## Dependências

  O projeto utiliza as seguintes bibliotecas:

  - numpy
  - matplotlib
  - memory-profiler
  - networkx
  - tkinter (já incluso no Python, instalar manualmente se necessário)
    
</div>

> [!NOTE]
> No arquivo [`requirements.txt`](trabalho1/requirements.txt) tem todas essas informações.




<p align="right">(<a href="#readme-topo">voltar ao topo</a>)</p>

## 🧪 Ambiente de Compilação e Execução

<div align="justify">

  O trabalho foi desenvolvido e testado em várias configurações de hardware. Podemos destacar algumas configurações de Sistema Operacional e Compilador, pois as demais configurações não influenciam diretamente no desempenho do programa.

</div>

<div align='center'>

[![SO][Ubuntu-badge]][Ubuntu-url]
[![IDE][vscode-badge]][vscode-url]
[![Python][Python-badge]][Python-url]

| *Hardware* | *Especificações* |
|:------------:|:-------------------:|
| *Laptop*   | Dell Inspiron 13 5330 |
| *Processador* | Intel Core i7-1360P |
| *Memória RAM* | 16 GB DDR5 |
| *Sistema Operacional* | Ubuntu 24.04 |
| *IDE* | Visual Studio Code |
| *Placa de Vídeo* | Intel Iris Xe Graphics |

</div>

> [!IMPORTANT] 
> Para que os testes tenham validade, considere as especificações
> do ambiente de compilação e execução do programa.

<p align="right">(<a href="#readme-topo">voltar ao topo</a>)</p>

## 📨 Contato

<div align="center">
  <br><br>
     <i>Guilherme Alvarenga de Azevedo - Graduando - 4º Período de Engenharia de Computação @ CEFET-MG</i>
  <br><br>
  
  [![Gmail][gmail-badge]][gmail-autor1]
  [![Linkedin][linkedin-badge]][linkedin-autor1]
  [![Telegram][telegram-badge]][telegram-autor1]
  
  
  <br><br>
     <i>Maria Eduarda Teixeira Souza - Graduando - 4º Período de Engenharia de Computação @ CEFET-MG</i>
  <br><br>
  
  [![Gmail][gmail-badge]][gmail-autor2]
  [![Linkedin][linkedin-badge]][linkedin-autor2]
  [![Telegram][telegram-badge]][telegram-autor2]

</div>

<p align="right">(<a href="#readme-topo">voltar ao topo</a>)</p>

<a name="referencias">📚 Referências</a>

1. AZEVEDO, Guilherme A. SOUZA, Maria E. T. **IA-Trabalhos**: Trabalho 1 - Labirinto. 2025. Disponível em: [https://github.com/dudatsouza/ia-trabalhos](https://github.com/dudatsouza/ia-trabalhos) Acesso em: 19 out. 2025.

2. OLIVEIRA, Tiago A. **Inteligência Artificial 04**: Estruturas e Estratégias de Busca. Slides de Aula. 2025.

3. RUSSELL, Stuart J; NORVIG, Peter. **Inteligência Artificial: Uma Abordagem Moderna**. 4. ed. Pearson, 2021.

<!-- [^1]: Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. (https://www.staff.city.ac.uk/~sbrp622/idfpapers/ksj_orig.pdf)

[^2]: Philip L.H. Yu, Wai Ming Wan, and Paul H. Lee. Decision Tree Modeling for Ranking Data. (https://www.researchgate.net/publication/252998138_Decision_Tree_Modeling_for_Ranking_Data)

[^3]: Ming Zhong, Mengchi Liu. Ranking the answer trees of graph search by both structure and content. (https://dl.acm.org/doi/abs/10.1145/2379307.2379314)

[^4]: Claudio Lucchese, Franco Maria Nardini, salvatore Orlando, Raffaele Perego, Nicola Tonellotto, Rossano Venturini. QuickScorer: a Fast Algorithm to Rank Documents with
Additive Ensembles of Regression Trees. (https://iris.unive.it/bitstream/10278/3661259/7/paper.pdf)

[^5]: Rada Mihalcea. Graph-based Ranking Algorithms for Sentence Extraction, Applied to Text Summarization. (https://dl.acm.org/doi/pdf/10.3115/1219044.1219064) -->






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
