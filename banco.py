import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

class Pessoa:
    def __init__(self, nome, data_nascimento):
        self.nome = nome
        self.data_nascimento = data_nascimento

class Usuario(Pessoa):
    def __init__(self, nome, cpf, data_nascimento, senha, saldo=0):
        super().__init__(nome, data_nascimento)
        self.cpf = cpf
        self.senha = senha
        self.saldo = saldo

    def to_dict(self):
        return {
            'nome': self.nome,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento,
            'senha': self.senha,
            'saldo': self.saldo
        }

class Banco:
    def __init__(self, db_path='db.txt'):
        self.db_path = db_path
        self.usuarios = self._carregar_dados()

    def _carregar_dados(self):
        if not os.path.exists(self.db_path):
            return []
        with open(self.db_path, 'r') as f:
            return [json.loads(line) for line in f.readlines()]

    def salvar_dados(self):
        with open(self.db_path, 'w') as f:
            for usuario in self.usuarios:
                f.write(json.dumps(usuario) + '\n')

    def cadastrar_usuario(self, nome, cpf, data_nascimento, senha):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf:
                return False
        novo_usuario = Usuario(nome, cpf, data_nascimento, senha)
        self.usuarios.append(novo_usuario.to_dict())
        self.salvar_dados()
        return True

    def login(self, cpf, senha):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf and usuario['senha'] == senha:
                return True, usuario
        return False, None

    def atualizar_saldo(self, cpf, valor):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf:
                usuario['saldo'] += valor
                self.salvar_dados()
                return True
        return False

    def consultar_extrato(self, cpf):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf:
                return usuario['saldo']
        return None

    def atualizar_dados(self, cpf, novo_nome, nova_senha):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf:
                usuario['nome'] = novo_nome
                usuario['senha'] = nova_senha
                self.salvar_dados()
                return True
        return False

    def deletar_usuario(self, cpf):
        for usuario in self.usuarios:
            if usuario['cpf'] == cpf:
                self.usuarios.remove(usuario)
                self.salvar_dados()
                return True
        return False

class Servidor(BaseHTTPRequestHandler):
    banco = Banco()
    cpf_l = None

    def _send_response(self, file_path, content_type):
        try:
            with open(file_path, 'r') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read().encode())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Pagina nao encontrada')

    def do_GET(self):
        if self.path == "/":
            self._send_response('index.html', 'text/html')
        elif self.path == "/login.html":
            self._send_response('login.html', 'text/html')
        elif self.path == "/cadastro.html":
            self._send_response('cadastro.html', 'text/html')
        elif self.path == "/dashboard.html":
            self._send_response('dashboard.html', 'text/html')
        elif self.path == "/deposito.html":
            self._send_response('deposito.html', 'text/html')
        elif self.path == "/saque.html":
            self._send_response('saque.html', 'text/html')
        elif self.path == "/extrato.html":
            self._send_response('extrato.html', 'text/html')
        elif self.path == "/atualizar_dados.html":
            self._send_response('atualizar_dados.html', 'text/html')
        elif self.path == "/deletar_conta.html":
            self._send_response('deletar_conta.html', 'text/html')
        elif self.path == "/visualizar_banco.html":
            self._send_response('visualizar_banco.html', 'text/html')
        elif self.path == "/db.txt":
            self._send_response('db.txt', 'text/plain')
        elif self.path == "/style.css":
            self._send_response('style.css', 'text/css')
        elif self.path == "/script.js":
            self._send_response('script.js', 'application/javascript')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Pagina nao encontrada')

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode())

        if self.path == "/login":
            cpf = post_data.get('cpf', [None])[0]
            senha = post_data.get('senha', [None])[0]

            if cpf and senha:
                sucesso, usuario = self.banco.login(cpf, senha)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                if sucesso:
                    Servidor.cpf_l = cpf
                    self.wfile.write(b"Login bem-sucedido")
                else:
                    self.wfile.write(b"CPF ou senha incorretos")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/cadastrar":
            nome = post_data.get('nome', [None])[0]
            cpf = post_data.get('cpf', [None])[0]
            data_nascimento = post_data.get('data_nascimento', [None])[0]
            senha = post_data.get('senha', [None])[0]

            if nome and cpf and data_nascimento and senha:
                if self.banco.cadastrar_usuario(nome, cpf, data_nascimento, senha):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b"Usuario cadastrado com sucesso!")
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"CPF ja cadastrado")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/depositar":
            valor = float(post_data.get('valor', [0])[0])

            if Servidor.cpf_l and valor:
                sucesso = self.banco.atualizar_saldo(Servidor.cpf_l, valor)
                self.send_response(200)
                self.end_headers()
                if sucesso:
                    self.wfile.write(b"Deposito realizado com sucesso!")
                else:
                    self.wfile.write(b"Erro ao realizar deposito")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/sacar":
            valor = float(post_data.get('valor', [0])[0])

            if Servidor.cpf_l and valor:
                sucesso = self.banco.atualizar_saldo(Servidor.cpf_l, -valor)
                self.send_response(200)
                self.end_headers()
                if sucesso:
                    self.wfile.write(b"Saque realizado com sucesso!")
                else:
                    self.wfile.write(b"Erro ao realizar saque")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/extrato":
            if Servidor.cpf_l:
                saldo = self.banco.consultar_extrato(Servidor.cpf_l)
                self.send_response(200)
                self.end_headers()
                if saldo is not None:
                    self.wfile.write(f"Seu saldo e: {saldo}".encode())
                else:
                    self.wfile.write(b"Erro ao consultar extrato")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/atualizar_dados":
            novo_nome = post_data.get('novo_nome', [None])[0]
            nova_senha = post_data.get('nova_senha', [None])[0]

            if Servidor.cpf_l and novo_nome and nova_senha:
                sucesso = self.banco.atualizar_dados(Servidor.cpf_l, novo_nome, nova_senha)
                self.send_response(200)
                self.end_headers()
                if sucesso:
                    self.wfile.write(b"Dados atualizados com sucesso!")
                else:
                    self.wfile.write(b"Erro ao atualizar dados")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

        elif self.path == "/deletar_conta":
            if Servidor.cpf_l:
                sucesso = self.banco.deletar_usuario(Servidor.cpf_l)
                self.send_response(200)
                self.end_headers()
                if sucesso:
                    self.wfile.write(b"Conta deletada com sucesso!")
                else:
                    self.wfile.write(b"Erro ao deletar conta")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Dados invalidos")

def run():
    server = HTTPServer(('localhost', 8080), Servidor)
    print('Servidor iniciado na porta 8080...')
    server.serve_forever()

if __name__ == "__main__":
    run()
