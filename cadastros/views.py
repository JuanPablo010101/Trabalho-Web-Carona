from django.shortcuts import redirect, render
from django.contrib import messages
from cadastros.models import Usuario

def cadastro_usuario(request):
    if request.method == 'POST':
        acao = request.POST.get('btnAcao')
        print(11,acao)
        if acao == "Novo_Usuario":
            nome = request.POST.get('txtNome')
            email = request.POST.get('txtEmail')
            senha = request.POST.get('txtSenha')
            print(f'Nome: {nome}, Email: {email}, Senha: {senha}')
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
            usuario = Usuario(nome=nome, email=email, is_active=True, is_admin=False)

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
