# baobaxia-publica

Ferramenta de linha de comando para publicar mídias e artigos no **Baobáxia** via API.

## Instalação

Clone o repositório ou baixe o tarball e instale com `pip`:

```bash
pip install .
```

Ou instale direto do tarball:

```bash
pip install baobaxia-publica-0.1.0.tar.gz
```

## Uso

```bash
publica [opções] caminho...
```

### Exemplos

Enviar uma imagem:
```bash
publica --usuario vince --senha livre ~/imagens/foto.png
```

Enviar várias imagens de uma vez:
```bash
publica --usuario vince --senha livre ~/imagens/*.jpg
```

Enviar um artigo Markdown:
```bash
publica --usuario vince --senha livre --titulo "Meu artigo" --descricao "teste" artigo.md
```

### Opções principais

- `--url` : URL da API (default: https://baobaxia.net/api/v2)
- `--usuario` : usuário para autenticação
- `--senha` : senha do usuário
- `--galaxia` : galaxia destino (slug ou smid)
- `--mucua` : mucua destino
- `--titulo` : título (obrigatório se não interativo)
- `--descricao` : descrição
- `--tags` : lista de tags (mídias = lista, artigos = string separada por vírgulas)
- `--insecure` : desabilitar verificação SSL

Para mais detalhes, rode:

```bash
publica -h
```
