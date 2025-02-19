from django.shortcuts import redirect, render
from django.contrib import messages
from cadastros.models import OfertaCarona, Usuario
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
def perfil_usuario(request): 
    print("A view do perfil foi chamada!") 
    usuario = request.user
    return render(request, 'perfil_usuario.html', {'user': usuario})

@login_required
def editar_perfil(request):
    usuario = request.user

    # Se o formulário for enviado via POST
    if request.method == 'POST':
        # Coleta os dados enviados pelo formulário
        nome = request.POST.get('id_nome')
        email = request.POST.get('id_email')
        telefone = request.POST.get('id_telefone')
        senha = request.POST.get('id_senha')
        imagem = request.FILES.get('id_profile_picture')  # A imagem é enviada como um arquivo

        # Verificação de atualização de senha
        if senha:
            # Verifica se a senha fornecida corresponde à senha armazenada
            if not usuario.check_password(senha):  # Verifica se a senha fornecida corresponde à armazenada
                messages.error(request, 'A nova senha não pode ser igual à senha atual.')
                usuario.set_password(senha)  # Atualiza a senha
                usuario.save()  # Salva o usuário com a nova senha
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
            else:
                
                messages.error(request, 'A nova senha não pode ser igual à senha atual.')
               
                

        # Atualizando os campos do usuário
        usuario.nome = nome
        usuario.email = email
        usuario.telefone = telefone

        # Verifica se o usuário enviou uma nova foto de perfil
        if imagem:
            usuario.profile_picture = imagem

        # Salva as alterações
        usuario.save()

        # Redireciona para o perfil de usuário com uma mensagem de sucesso
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('autenticacao:volta_home')

    else:
        return render(request, 'editar_perfil.html', {'user': usuario})
     
@login_required
def oferta_carona(request):
    print("Passei em Oferta Carona")   
    return render(request, 'oferta_carona.html')



@login_required
def listar_caronas(request):
    ofertas = OfertaCarona.objects.filter(status='Aberta').exclude(motorista=request.user).order_by('data_hora')
    return render(request, 'lista_ofertas.html', {'ofertas': ofertas})

