from django.shortcuts import redirect, render
from django.contrib import messages
from cadastros.models import OfertaCarona, Usuario, Veiculo
from django.contrib.auth.decorators import login_required

def cadastro_usuario(request):
    if request.method == 'POST':
        acao = request.POST.get('btnAcao')
    
        if acao == "Novo_Usuario":
            nome = request.POST.get('txtNome')
            email = request.POST.get('txtEmail')
            senha = request.POST.get('txtSenha')
            telefone = request.POST.get('txtTelefone')
            # Verificando se o e-mail já está cadastrado
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Usuário já cadastrado com esse Email!')
                return redirect('cadastros:cadastro_usuario')
            senha = request.POST.get('txtSenha')
            confirmar_senha = request.POST.get('confirmar_senha')

            # Verificando se as senhas coincidem
            if senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem!')
                return redirect('cadastros:cadastro_usuario')

            # Criando uma nova instância do usuário com os campos obrigatórios
            usuario = Usuario(nome=nome,telefone=telefone, email=email, is_active=True, is_admin=False)

            # Salvando a senha de forma segura
            usuario.set_password(senha)
            try:
                usuario.save()
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao salvar o usuário: {str(e)}')

            # Mensagem de sucesso e redirecionamento
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('autenticacao:login')

    return render(request, 'cadastro_usuario.html')
@login_required
def oferta_carona(request):
    if request.method == 'POST':
        acao = request.POST.get('btnAcao')
        if acao == "oferecer_carona":
            motorista = request.user  # Já temos o usuário autenticado, não precisa buscar de novo

            # Obtendo os dados do formulário
            veiculo_id = request.POST.get('slcVeiculo')
            origem = request.POST.get('txtOrigem')
            destino = request.POST.get('txtDestino')
            data = request.POST.get('txtData_hora')
            num_vagas = request.POST.get('txtVagas')
            descricao = request.POST.get('txtDescricao')

            # Verificar se o veículo selecionado pertence ao usuário
            try:
                veiculo = Veiculo.objects.get(id=veiculo_id, usuario=motorista)
            except Veiculo.DoesNotExist:
                messages.error(request, 'Veículo inválido ou não encontrado!')
                return redirect('core:oferta_carona')

            # Criando a oferta de carona
            oferta = OfertaCarona(
                motorista=motorista,  # Agora corretamente associado ao usuário logado
                veiculo=veiculo,  # Agora pegamos a instância correta
                origem=origem,
                destino=destino,
                data_hora=data,
                vagas_ofertadas=num_vagas,
                descricao=descricao,
                status='Aberta'
            )
            oferta.save()

            messages.success(request, 'Oferta de Carona cadastrada com sucesso!')
            return redirect('core:main')  # Redirecionamento correto após o cadastro

    # Listar apenas veículos do usuário logado
    veiculos = Veiculo.objects.filter(usuario=request.user)
    return render(request, 'oferta_carona.html', {'veiculos': veiculos})
@login_required
def cadastro_veiculo(request):
    if request.method == 'POST':
        acao = request.POST.get('btnAcao')
        
        if acao == "Novo_Veiculo":
            modelo = request.POST.get('txtModelo')
            placa = request.POST.get('txtPlaca')
            cor = request.POST.get('txtCor')
            ano = request.POST.get('txtAno')
            

            if Veiculo.objects.filter(placa=placa).exists():
                messages.error(request, 'Carro já cadastrado')
                return redirect('cadastros:cadastro_veiculo')

            id_User = request.session.get('id_atual')  # Corrigindo o acesso à sessão
            if not id_User:
                messages.error(request, 'Usuário não autenticado!')
                return redirect('autenticacao:login')

            try:
                usuario = Usuario.objects.get(id=id_User)  # Pegando um único objeto
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuário não encontrado!')
                return redirect('autenticacao:login')

            # Criando e salvando o veículo
            veiculo = Veiculo(usuario=usuario, modelo=modelo, placa=placa, ano=ano, cor=cor)
            veiculo.save()

            messages.success(request, 'Veículo cadastrado com sucesso!')
            return redirect('core:main')  # Se estiver dentro de um namespace

    return render(request, 'cadastro_veiculo.html')  

@login_required
def listar_caronas(request):
    ofertas = OfertaCarona.objects.filter(status='Aberta').exclude(motorista=request.user).order_by('data_hora')
    return render(request, 'lista_ofertas.html', {'ofertas': ofertas})

