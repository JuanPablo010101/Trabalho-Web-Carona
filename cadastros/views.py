from django.shortcuts import redirect, render
from django.contrib import messages
from cadastros.models import OfertaCarona, ReservaCarona, Usuario
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
    usuario = request.user
    return render(request, 'perfil_usuario.html', {'user': usuario})

@login_required
def editar_perfil(request):
    usuario = request.user

    
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
            if not usuario.check_password(senha): 
                messages.error(request, 'A nova senha não pode ser igual à senha atual.')
                usuario.set_password(senha) 
                usuario.save()
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
    if request.method == 'POST':
        acao = request.POST.get('btnAcao')
        if acao == "oferecer_carona":
            # Busca motorista que é o Usuario          
            motorista = request.user  
            # Obtendo os dados do formulário
            origem = request.POST.get('txtOrigem')
            destino = request.POST.get('txtDestino')
            data = request.POST.get('txtData')  
            hora = request.POST.get('txtHora') 
            num_vagas = request.POST.get('txtVagas')
            descricao = request.POST.get('txtDescricao')

            # Combinando data e hora para criar o valor de 'data_hora'
            try:
                data_hora_str = f"{data} {hora}"  # Combine a data e a hora
                data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")

                # Criando a oferta de carona
                oferta = OfertaCarona(
                    motorista=motorista,
                    origem=origem,
                    destino=destino,
                    data_hora=data_hora,
                    vagas_ofertadas=num_vagas,
                    descricao=descricao,
                    status='Aberta'
                )
                oferta.save()
                messages.success(request, 'Oferta de Carona cadastrada com sucesso!')
                # Redirecionamento correto após o cadastro
                return redirect('autenticacao:volta_home')  
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao cadastrar a carona: {e}')
                return redirect('cadastros:oferta_carona')
                
    return render(request, 'oferta_carona.html')



@login_required
def minhas_ofertas(request):
    # Buscar todas as ofertas de carona do usuário autenticado
    ofertas = OfertaCarona.objects.filter(motorista=request.user)

    return render(request, 'minhas_ofertas.html', {'ofertas': ofertas})

@login_required
def alterar_status_oferta(request):
    if request.method == 'POST':
        oferta_id = request.POST.get('oferta_id')
        acao = request.POST.get('acao')

        try:
            oferta = OfertaCarona.objects.get(id=oferta_id, motorista=request.user)

            if acao == 'cancelar':
                oferta.status = 'cancelada'
                messages.success(request, 'Oferta cancelada com sucesso!')
            elif acao == 'finalizar':
                oferta.status = 'encerrada'
                messages.success(request, 'Oferta finalizada com sucesso!')
           # elif acao == 'reservar':  # Verificando a ação 'reservar'
                # Redireciona para a página de reserva
            #    return redirect('cadastros:reservar_carona', oferta_id=oferta.id)
            else:
                messages.error(request, 'Ação inválida.')
            
            oferta.save()  # Salva as alterações

        except OfertaCarona.DoesNotExist:
            messages.error(request, 'Oferta não encontrada ou você não tem permissão para alterá-la.')

    return redirect('cadastros:minhas_ofertas')



@login_required
def reservar_carona(request):
    # Buscar todas as ofertas de carona com o status 'aberta', excluindo as que o usuário publicou
    ofertas = OfertaCarona.objects.filter(status__in=['Aberta', 'aberta']) \
                                  .exclude(motorista=request.user)  # Exclui ofertas do próprio motorista

    # Obter os IDs das ofertas que o usuário já reservou
    reservas_feitas_ids = ReservaCarona.objects.filter(passageiro=request.user).values_list('oferta_id', flat=True)

    return render(request, 'reserva_carona.html', {'ofertas': ofertas, 'reservas_feitas_ids': reservas_feitas_ids})

@login_required
def aceita_reserva(request):
    if request.method == 'POST':
        oferta_id = request.POST.get('oferta_id')
        oferta = OfertaCarona.objects.filter(id=oferta_id).first()

        if not oferta:
            messages.error(request, 'Carona não encontrada.')
            return redirect('cadastros:minhas_ofertas')

        # Verifica se o usuário já reservou essa carona
        if ReservaCarona.objects.filter(oferta=oferta, passageiro=request.user).exists():
            messages.error(request, 'Você já tem uma reserva para essa carona.')
        elif oferta.vagas_disponiveis() > 0:  # Verifica se há vagas disponíveis
            # Cria a reserva
            reserva = ReservaCarona.objects.create(oferta=oferta, passageiro=request.user, status='Confirmada')

            # Decrementa o número de vagas disponíveis
            oferta.vagas_ofertadas -= 1
            oferta.save()  

            messages.success(request, 'Reserva realizada com sucesso! Aguarde a aprovação do motorista.')
        else:
            messages.error(request, 'Não há mais vagas disponíveis.')

    return redirect('cadastros:reservar_carona') 

@login_required
def minhas_reservas(request):
    # Obtém todas as reservas do usuário logado
    reservas_ativas = ReservaCarona.objects.filter(passageiro=request.user, status="Confirmada").select_related('oferta', 'oferta__motorista')
    reservas_canceladas = ReservaCarona.objects.filter(passageiro=request.user, status="Cancelada").select_related('oferta', 'oferta__motorista')

    # Passa todas as reservas para o template
    return render(request, 'minhas_reservas.html', {'reservas_ativas': reservas_ativas, 'reservas_canceladas': reservas_canceladas})

@login_required
def cancelar_reserva(request):
    reserva_id = request.GET.get("reserva_id")  # Obtém o ID da reserva 
    
    if reserva_id: # Verifica se o ID da reserva foi fornecido
        # Busca a reserva pelo ID e pelo passageiro
        reserva = ReservaCarona.objects.filter(id=reserva_id, passageiro=request.user).first()
        # Verifica se a reserva existe e se não foi cancelada
        if reserva and reserva.status != "Cancelada":
            reserva.status = "Cancelada"
            reserva.oferta.vagas_ofertadas += 1  # Devolve a vaga para a oferta
            reserva.oferta.save()  # Salva as alterações na oferta 
            reserva.save() 

    return redirect('cadastros:minhas_reservas')
