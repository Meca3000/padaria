from flask import Flask
from flask import render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_simplelogin import SimpleLogin , login_required
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padaria.db"
app.config["SECRET_KEY"] = "Minhasenha10#"
app.config["SIMPLELOGIN_USERNAME"] = "Alexandre"
app.config["SIMPLELOGIN_PASSWORD"] = "abc123"
db = SQLAlchemy()
db.init_app(app)
SimpleLogin(app)

class Product(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True) 
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    ingredientes = db.Column(db.String(500))
    origem = db.Column(db.String(100))
    imagem = db.Column(db.String(100))


    def __init__(self,
                 nome: str,
                 descricao: str,
                 ingredientes: str,
                 origem: str,
                 imagem: str ) -> None:
        self.nome = nome
        self.descricao = descricao
        self.ingredientes = ingredientes
        self.origem = origem
        self.imagem = imagem



@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/listar_produtos", methods=["GET","POST"])
@login_required
def listar_produtos():
    if request.method == "POST":
        termo = request.form["pesquisa"]
        resultado = db.session.execute(db.select(Product).filter(Product.nome.like(f'%{termo}%'))).scalars()
        return render_template('produtos.html', produtos=resultado)
    else:
        produtos = db.session.execute(db.select(Product)).scalars()
        return render_template('produtos.html', produtos=produtos)

@app.route("/cadastrar_produto" , methods=["GET","POST"])
@login_required
def cadastrar_produto():
    if request.method == "POST":
        status = {"type":"sucesso", "message": "Produto cadastrado com sucesso!"}
        dados = request.form 
        imagem = request.files['imagem']
        try:
            produto = Product(dados['nome'],
                            dados['descricao'],
                            dados['ingredientes'],
                            dados['origem'],
                            imagem.filename)
            imagem.save(os.path.join('static/imagens' , imagem.filename))
            db.session.add(produto)
            db.session.commit()
        except:
            status = {"type":"erro", "message": f"Houve um problema ao cadastrar o produto{dados['nome']}!"}
        
            
        return render_template('cadastrar.html', status=status) 
    else:
        return render_template("cadastrar.html")
    
@app.route("/editar_produtos/<int:id>", methods=["GET","POST"])
@login_required    
def editar_produto(id):
    if request.method == "POST":
        dados_editados = request.form
        imagem = request.files['imagem']
        produto = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
   
        produto.nome = dados_editados["nome"]
        produto.descricao = dados_editados["descricao"]
        produto.ingredientes = dados_editados["ingredientes"]
        produto.origem = dados_editados["origem"]
        
        if imagem.filename:
            produto.imagem = imagem.filename
            
        
        db.session.commit()
        return redirect("/lista_produtos")
    
    
    else:
        produto_editado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
        return render_template("editar.html",produto=produto_editado)   

@app.route("/deletar_produto/<int:id>")
@login_required
def deletar_produto(id):
    produto_deletado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
    db.session.delete(produto_deletado)
    db.session.commit()
    return redirect("/listar_produtos")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run()