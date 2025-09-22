#!/usr/bin/env python3
import argparse
import requests
import os
import mimetypes
import getpass
from pathlib import Path
import uuid
import urllib3
from tqdm import tqdm
from . import __version__

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --------- Utils ---------
def guess_type(filename):
    mtype, _ = mimetypes.guess_type(filename)
    if not mtype:
        return "arquivo"
    if mtype.startswith("image"):
        return "imagem"
    if mtype.startswith("video"):
        return "video"
    if mtype.startswith("audio"):
        return "audio"
    if mtype == "text/markdown":
        return "artigo"
    return "arquivo"

def autenticar(api_url, usuario, senha, verify=True):
    resp = requests.post(
        f"{api_url}/token",
        data={"username": usuario, "password": senha},
        verify=verify
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def listar_galaxias(api_url, token, verify=True):
    resp = requests.get(f"{api_url}/galaxia", headers={"Authorization": f"Bearer {token}"}, verify=verify)
    resp.raise_for_status()
    return resp.json()

def escolher_galaxia_mucua(api_url, token, galaxia_arg=None, mucua_arg=None, verify=True):
    galaxias = listar_galaxias(api_url, token, verify)

    if not galaxia_arg:
        print("== Galaxias disponíveis ==")
        for i, g in enumerate(galaxias):
            nome = g.get("name") or g.get("slug") or str(g)
            print(f"{i+1}. {nome} ({g.get('slug')})")

        idx = int(input("Escolha a galaxia: ")) - 1
        galaxia = galaxias[idx]["slug"]
        mucua = galaxias[idx].get("default_mucua")
    else:
        galaxia = galaxia_arg
        mucua = mucua_arg

    if not mucua:
        print("⚠️ Nenhuma mucua listada, usando default_mucua.")
        mucua = galaxias[0].get("default_mucua")
    return galaxia, mucua


# --------- Criação ---------

def criar_midia(api_url, token, galaxia, mucua, titulo, descricao=None, tipo="arquivo", extra=None, verify=True):
    url = f"{api_url}/{galaxia}/{mucua}/acervo/midia"
    payload = {
        "title": titulo,
        "description": descricao or "",
        "type": tipo,
        "is_public": True,
    }
    if extra:
        payload.update(extra)

    # Para mídias, tags devem ser lista
    if "tags" in payload and isinstance(payload["tags"], str):
        payload["tags"] = [t.strip() for t in payload["tags"].split(",") if t.strip()]

    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, verify=verify)
    if not resp.ok:
        print(f"❌ Erro criar mídia: {resp.text}")
    resp.raise_for_status()
    midia = resp.json()
    print(f"🎞️ Mídia criada ({tipo}): {titulo}")
    return midia


def criar_artigo(api_url, token, galaxia, mucua, titulo, descricao=None, extra=None, verify=True):
    url = f"{api_url}/{galaxia}/{mucua}/blog/artigo"
    payload = {
        "title": titulo,
        "description": descricao or "",
        "is_public": True,
    }
    if extra:
        payload.update(extra)

    # Para artigos, tags devem ser string com vírgulas + espaço
    if "tags" in payload:
        if isinstance(payload["tags"], list):
            payload["tags"] = ", ".join(payload["tags"])
        elif isinstance(payload["tags"], str):
            payload["tags"] = ", ".join([t.strip() for t in payload["tags"].split(",") if t.strip()])

    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, verify=verify)
    if not resp.ok:
        print(f"❌ Erro criar artigo: {resp.text}")
    resp.raise_for_status()
    artigo = resp.json()
    print(f"📝 Artigo criado: {titulo}")
    return artigo


# --------- Upload ---------

class ProgressFile:
    def __init__(self, path, bar):
        self.f = open(path, "rb")
        self.bar = bar

    def read(self, size=-1):
        chunk = self.f.read(size)
        if chunk:
            self.bar.update(len(chunk))
        return chunk

    def __getattr__(self, attr):
        return getattr(self.f, attr)

def upload_arquivo(api_url, token, galaxia, mucua, smid, caminho, tipo="midia", verify=True):
    if tipo == "midia":
        url = f"{api_url}/{galaxia}/{mucua}/acervo/upload/{smid}"
    else:
        url = f"{api_url}/{galaxia}/{mucua}/blog/content/{smid}"

    file_size = os.path.getsize(caminho)
    with tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=os.path.basename(caminho),
    ) as bar:
        pf = ProgressFile(caminho, bar)
        files = {"arquivo": (os.path.basename(caminho), pf)}
        resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, verify=verify)
        pf.close()

    if not resp.ok:
        print(f"❌ Erro upload {tipo}: {resp.text}")
    resp.raise_for_status()

# --------- Extra fields ---------
def coletar_extra(args, tipo):
    extra = {}
    campos = [
        "tags","status","is_public","language","rights","date",
        "publisher","contributor","relation","location","mocambo"
    ]
    for campo in campos:
        val = getattr(args, campo, None)
        if val:
            if campo == "tags":
                tags = [t.strip() for t in val.split(",") if t.strip()]
                if tipo == "artigo":
                    # Artigo precisa string com vírgula+espaço
                    extra["tags"] = ", ".join(tags)
                else:
                    # Mídia usa lista
                    extra["tags"] = tags
            elif campo == "contributor":
                # aceitar tanto lista (de interactive) quanto string
                if isinstance(val, list):
                    extra["contributor"] = val
                else:
                    extra["contributor"] = [c.strip() for c in val.split(",") if c.strip()]
            elif campo == "is_public":
                extra["is_public"] = val.lower() in ("true","1","yes","sim") if isinstance(val, str) else bool(val)
            else:
                extra[campo] = val
    return extra

# --------- Processamento ---------
def carregar_arquivos(caminhos):
    arquivos = []
    for c in caminhos:
        p = Path(c).expanduser()
        if p.is_dir():
            arquivos.extend(list(p.rglob("*")))
        else:
            arquivos.append(p)
    return [str(a) for a in arquivos if a.is_file()]

def processar(api_url, arquivos, token, galaxia, mucua, titulo, descricao, args, verify=True):
    grupos = {}
    for arq in arquivos:
        tipo = guess_type(arq)
        if tipo == "artigo":
            extra = coletar_extra(args, "artigo")
            sugestao = os.path.splitext(os.path.basename(arq))[0]
            t = titulo or input(f"Título para artigo '{os.path.basename(arq)}' [{sugestao}]: ").strip() or sugestao
            d = descricao or input(f"Descrição opcional para '{t}' (Enter para pular): ").strip() or None
            artigo = criar_artigo(api_url, token, galaxia, mucua, titulo=t, descricao=d, extra=extra, verify=verify)
            smid = artigo.get("smid") or artigo.get("smid")  # tentar obter
            print(f"📝 Artigo criado: {t}")
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="artigo", verify=verify)
        else:
            grupos.setdefault(tipo, []).append(arq)

    for tipo, lista in grupos.items():
        if not lista:
            continue
        extra = coletar_extra(args, "midia")
        sugestao_grp = f"{tipo.capitalize()}s"
        t = titulo or input(f"Título para grupo '{tipo}' ({len(lista)} arquivos) [{sugestao_grp}]: ").strip() or sugestao_grp
        d = descricao or input(f"Descrição opcional para grupo '{t}' (Enter para pular): ").strip() or None
        midia = criar_midia(api_url, token, galaxia, mucua, t, descricao=d, tipo=tipo, extra=extra, verify=verify)
        smid = midia.get("smid")
        print(f"🎞️ Mídia criada ({tipo}): {t}")
        for arq in lista:
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="midia", verify=verify)

# --------- Interactive extras helper ---------
def perguntar_atributos_interativos():
    """
    Menu simples para preencher atributos opcionais.
    Retorna um dicionário com chaves correspondentes aos argumentos (strings).
    """
    extra = {}
    while True:
        print("\n== Atributos extras ==")
        print("1. Tags")
        print("2. Status")
        print("3. Publisher")
        print("4. Contributor")
        print("5. Language")
        print("6. Rights")
        print("7. Relation")
        print("8. Location")
        print("9. Mocambo")
        print("0. Finalizar")
        escolha = input("Escolha um atributo para adicionar (0 para sair): ").strip()
        if escolha == "0":
            break
        if escolha == "1":
            extra["tags"] = input("Tags (separadas por vírgula): ").strip()
        elif escolha == "2":
            extra["status"] = input("Status (ex: draft/published): ").strip()
        elif escolha == "3":
            extra["publisher"] = input("Publisher: ").strip()
        elif escolha == "4":
            v = input("Contributors (separados por vírgula): ").strip()
            extra["contributor"] = v  # deixa como string; coletar_extra lida com string e lista
        elif escolha == "5":
            extra["language"] = input("Language (ex: pt-br): ").strip()
        elif escolha == "6":
            extra["rights"] = input("Rights: ").strip()
        elif escolha == "7":
            extra["relation"] = input("Relation: ").strip()
        elif escolha == "8":
            extra["location"] = input("Location (lat,lon;lat,lon ou texto): ").strip()
        elif escolha == "9":
            extra["mocambo"] = input("Mocambo: ").strip()
        else:
            print("Opção inválida.")
    return extra

# --------- Main ---------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("caminho", nargs="+", help="Arquivos ou pastas para enviar")
    parser.add_argument("--url", help="URL da API (se não passada, pergunta interativamente)")
    parser.add_argument("--usuario")
    parser.add_argument("--senha")
    parser.add_argument("--galaxia")
    parser.add_argument("--mucua")
    parser.add_argument("--titulo")
    parser.add_argument("--descricao")
    parser.add_argument("--tags")
    parser.add_argument("--status")
    parser.add_argument("--is-public")
    parser.add_argument("--language")
    parser.add_argument("--rights")
    parser.add_argument("--date")
    parser.add_argument("--publisher")
    parser.add_argument("--contributor")
    parser.add_argument("--relation")
    parser.add_argument("--location")
    parser.add_argument("--mocambo")
    parser.add_argument("--insecure", action="store_true", help="Ignorar verificação SSL")

    args = parser.parse_args()

    # Determina api_url (pergunta se não foi passada)
    if args.url and args.url.strip():
        api_url = args.url.strip()
    else:
        entrada = input("URL da API [https://baobaxia.net/api/v2]: ").strip()
        api_url = entrada if entrada else "https://baobaxia.net/api/v2"
        verify = False

    usuario = args.usuario or input("Usuário: ")
    senha = args.senha or getpass.getpass("Senha: ")

    token = autenticar(api_url, usuario, senha, verify=verify)
    galaxia, mucua = escolher_galaxia_mucua(api_url, token, args.galaxia, args.mucua, verify=verify)

    arquivos = carregar_arquivos(args.caminho)

    # Se nenhum atributo opcional foi passado, oferecemos o menu interativo
    campos_passados = any([
        args.tags, args.status, args.publisher, args.contributor,
        args.language, args.rights, args.relation, args.location, args.mocambo
    ])

    if not campos_passados:
        usar_extra = input("Deseja adicionar atributos extras? [s/N]: ").strip().lower()
        if usar_extra == "s":
            extra_interativos = perguntar_atributos_interativos()
            # coloca no args para processar()/coletar_extra() usar
            for k, v in extra_interativos.items():
                setattr(args, k, v)

    processar(api_url, arquivos, token, galaxia, mucua, args.titulo, args.descricao, args, verify=verify)
