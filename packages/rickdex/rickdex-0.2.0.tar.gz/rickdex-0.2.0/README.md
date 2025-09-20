> us [English version](README_EN.md)

# rickdex

Biblioteca Python para facilitar o acesso à [API Rick and Morty](https://rickandmortyapi.com/) de forma simples e intuitiva, permitindo a busca de informações sobre personagens, episódios e localizações diretamente no seu código Python.

### Requisitos

- Python 3.8 ou superior

### Instalação

Para instalar, execute:

```bash
pip install rickdex
```

### Como Usar

Importe as classes principais:

```python
from rickdex import Character, Location, Episode
```

#### Exemplos de Uso

- Buscar informações gerais da API:

```python
character = Character()
info = character.info()
print(info)
```

- Buscar por ID:

```python
rick = character.get_one(1)
print(rick)
```

- Buscar vários por lista de IDs:

```python
lista = character.get_all([1, 2, 3])
print(lista)
```

- Filtrar API:

```python
resultado = character.api_filter(name="Rick", status="alive")
print(resultado)
```

- Filtrar elemento da API:

```python
nome = character.item_filter(1, "name")
print(nome)
```

### Estrutura

- **Rickdex**: Classe para interação com API contendo os metódos genéricos.
- **Character**: Herda os metódos da classe Rickdex.
- **Location**: Herda os metódos da classe Rickdex.
- **Episode**: Herda os metódos da classe Rickdex.

### Licença

Consulte a política de uso da API Rick and Morty. Recomenda-se utilizar esta biblioteca para fins pessoais ou acadêmicos, respeitando as diretrizes da API e do seu repositório de código.