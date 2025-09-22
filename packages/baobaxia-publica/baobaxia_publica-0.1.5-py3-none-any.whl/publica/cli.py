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
            print(f"{i+1}. {g['name']} ({g['slug']})")

        idx = int(input("Escolha a galaxia: ")) - 1
        galaxia = galaxias[idx]["slug"]
        mucua = galaxias[idx].get("default_mucua")
    else:
        galaxia = galaxia_arg
        mucua = mucua_arg

    if not mucua:
        print("⚠️ Nenhuma mucua listada, usando default_mucua.")
        mucua = galaxias[0]["default_mucua"]

    return galaxia, mucua


# --------- Criação ---------
def criar_midia(api_url, token, galaxia, mucua, titulo, descricao=None, tipo="arquivo", extra=None, verify=True):
    payload = {
        "title": titulo,
        "description": descricao,
        "type": tipo,
#        "slug_smid": str(uuid.uuid4())
    }
    if extra:
        payload.update(extra)

    resp = requests.post(
        f"{api_url}/{galaxia}/{mucua}/acervo/midia",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        verify=verify
    )
    if resp.status_code >= 400:
        print(f"❌ Erro criar mídia: {resp.text}")
    resp.raise_for_status()
    return resp.json()

def criar_artigo(api_url, token, galaxia, mucua, titulo, descricao=None, extra=None, verify=True):
    payload = {
        "title": titulo,
        "description": descricao,
        "slug_smid": str(uuid.uuid4())
    }
    if extra:
        payload.update(extra)

    resp = requests.post(
        f"{api_url}/{galaxia}/{mucua}/blog/artigo",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        verify=verify
    )
    if resp.status_code >= 400:
        print(f"❌ Erro criar artigo: {resp.text}")
    resp.raise_for_status()
    return resp.json()

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
        val = getattr(args, campo)
        if val:
            if campo == "tags":
                tags = [t.strip() for t in val.split(",") if t.strip()]
                if tipo == "artigo":
                    # Artigo precisa ser string com vírgula + espaço
                    extra["tags"] = ", ".join(tags)
                else:
                    # Mídia usa lista
                    extra["tags"] = tags
            elif campo == "contributor":
                extra["contributor"] = [c.strip() for c in val.split(",") if c.strip()]
            elif campo == "is_public":
                extra["is_public"] = val.lower() in ("true","1","yes","sim")
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
            t = titulo or input(f"Título para artigo '{os.path.basename(arq)}': ")
            d = descricao or input(f"Descrição opcional para '{t}' (Enter para pular): ") or None
            artigo = criar_artigo(api_url, token, galaxia, mucua, t, descricao=d, extra=extra, verify=verify)
            smid = artigo["smid"]
            print(f"📝 Artigo criado: {t}")
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="artigo", verify=verify)
        else:
            grupos.setdefault(tipo, []).append(arq)

    for tipo, lista in grupos.items():
        extra = coletar_extra(args, "midia")
        t = titulo or input(f"Título para grupo '{tipo}' ({len(lista)} arquivos): ")
        d = descricao or input(f"Descrição opcional para grupo '{t}' (Enter para pular): ") or None
        midia = criar_midia(api_url, token, galaxia, mucua, t, descricao=d, tipo=tipo, extra=extra, verify=verify)
        smid = midia["smid"]
        print(f"🎞️ Mídia criada ({tipo}): {t}")
        for arq in lista:
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="midia", verify=verify)

# --------- Main ---------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("caminho", nargs="+", help="Arquivos ou pastas para enviar")
    parser.add_argument("--url", help="URL da API (default: https://baobaxia.net/api/v2)")
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
    parser.add_argument("--insecure", action="store_true")

    args = parser.parse_args()
    verify = not args.insecure

    if args.url and args.url.strip():
        api_url = args.url.strip()
    else:
        entrada = input("URL da API [https://baobaxia.net/api/v2]: ").strip()
        api_url = entrada if entrada else "https://baobaxia.net/api/v2"
        verfy = False

    usuario = args.usuario or input("Usuário: ")
    senha = args.senha or getpass.getpass("Senha: ")

    token = autenticar(api_url, usuario, senha, verify=verify)
    galaxia, mucua = escolher_galaxia_mucua(api_url, token, args.galaxia, args.mucua, verify=verify)

    arquivos = carregar_arquivos(args.caminho)
    processar(api_url, arquivos, token, galaxia, mucua, args.titulo, args.descricao, args, verify=verify)

