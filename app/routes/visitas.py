from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Visita, Usuario, Fornecedor, db
from datetime import datetime

bp = Blueprint('visitas', __name__, url_prefix='/api/visitas')


@bp.route('', methods=['GET'])
@jwt_required()
def listar_visitas():
    """Lista todas as visitas do usuário ou todas (se admin)"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        status = request.args.get('status')
        
        if usuario.tipo == 'admin':
            query = Visita.query
        else:
            query = Visita.query.filter_by(usuario_id=usuario_id)
        
        if status:
            query = query.filter_by(status=status)
        
        visitas = query.order_by(Visita.data_visita.desc()).all()
        
        return jsonify([v.to_dict() for v in visitas])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obter_visita(id):
    """Obtém uma visita específica"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin' and visita.usuario_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return jsonify(visita.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def criar_visita():
    """Cria uma nova visita"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('nome'):
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        
        visita = Visita(
            nome=data.get('nome'),
            email=data.get('email'),
            telefone=data.get('telefone'),
            localizacao_lat=data.get('localizacao_lat'),
            localizacao_lng=data.get('localizacao_lng'),
            endereco_completo=data.get('endereco_completo'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            observacoes=data.get('observacoes'),
            status='pendente',
            usuario_id=usuario_id,
            data_visita=datetime.utcnow()
        )
        
        db.session.add(visita)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Visita cadastrada com sucesso',
            'visita': visita.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_visita(id):
    """Atualiza uma visita existente"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin' and visita.usuario_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        if visita.status != 'pendente':
            return jsonify({'erro': 'Não é possível editar uma visita que já foi aprovada ou recusada'}), 400
        
        data = request.get_json()
        
        if data.get('nome'):
            visita.nome = data['nome']
        if 'email' in data:
            visita.email = data['email']
        if 'telefone' in data:
            visita.telefone = data['telefone']
        if 'localizacao_lat' in data:
            visita.localizacao_lat = data['localizacao_lat']
        if 'localizacao_lng' in data:
            visita.localizacao_lng = data['localizacao_lng']
        if 'endereco_completo' in data:
            visita.endereco_completo = data['endereco_completo']
        if 'cidade' in data:
            visita.cidade = data['cidade']
        if 'estado' in data:
            visita.estado = data['estado']
        if 'observacoes' in data:
            visita.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Visita atualizada com sucesso',
            'visita': visita.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>/recusar', methods=['POST'])
@jwt_required()
def recusar_visita(id):
    """Recusa uma visita (marca como negada)"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin' and visita.usuario_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        if visita.status != 'pendente':
            return jsonify({'erro': 'Esta visita já foi processada'}), 400
        
        data = request.get_json() or {}
        
        visita.status = 'recusada'
        visita.data_decisao = datetime.utcnow()
        visita.motivo_recusa = data.get('motivo', '')
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Visita marcada como recusada',
            'visita': visita.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>/aprovar', methods=['POST'])
@jwt_required()
def aprovar_visita(id):
    """Aprova uma visita e cria o fornecedor"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin' and visita.usuario_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        if visita.status != 'pendente':
            return jsonify({'erro': 'Esta visita já foi processada'}), 400
        
        data = request.get_json() or {}
        
        fornecedor = Fornecedor(
            nome=data.get('nome', visita.nome),
            email=data.get('email', visita.email),
            telefone=data.get('telefone', visita.telefone),
            cidade=data.get('cidade', visita.cidade),
            estado=data.get('estado', visita.estado),
            rua=data.get('rua', ''),
            numero=data.get('numero', ''),
            cep=data.get('cep', ''),
            bairro=data.get('bairro', ''),
            cnpj=data.get('cnpj'),
            cpf=data.get('cpf'),
            tipo_documento=data.get('tipo_documento', 'cnpj'),
            observacoes=data.get('observacoes', visita.observacoes),
            comprador_responsavel_id=data.get('comprador_responsavel_id', usuario_id),
            ativo=True
        )
        
        db.session.add(fornecedor)
        db.session.flush()
        
        visita.status = 'aprovada'
        visita.data_decisao = datetime.utcnow()
        visita.fornecedor_id = fornecedor.id
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Visita aprovada e fornecedor criado com sucesso',
            'visita': visita.to_dict(),
            'fornecedor': fornecedor.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>/dados-para-fornecedor', methods=['GET'])
@jwt_required()
def obter_dados_para_fornecedor(id):
    """Obtém os dados da visita formatados para criar fornecedor"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin' and visita.usuario_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return jsonify({
            'nome': visita.nome,
            'email': visita.email,
            'telefone': visita.telefone,
            'cidade': visita.cidade,
            'estado': visita.estado,
            'endereco_completo': visita.endereco_completo,
            'observacoes': visita.observacoes,
            'visita_id': visita.id
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def excluir_visita(id):
    """Exclui uma visita"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        visita = Visita.query.get(id)
        if not visita:
            return jsonify({'erro': 'Visita não encontrada'}), 404
        
        if usuario.tipo != 'admin':
            return jsonify({'erro': 'Apenas administradores podem excluir visitas'}), 403
        
        db.session.delete(visita)
        db.session.commit()
        
        return jsonify({'mensagem': 'Visita excluída com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def estatisticas():
    """Retorna estatísticas das visitas"""
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if usuario.tipo == 'admin':
            total = Visita.query.count()
            pendentes = Visita.query.filter_by(status='pendente').count()
            aprovadas = Visita.query.filter_by(status='aprovada').count()
            recusadas = Visita.query.filter_by(status='recusada').count()
        else:
            total = Visita.query.filter_by(usuario_id=usuario_id).count()
            pendentes = Visita.query.filter_by(usuario_id=usuario_id, status='pendente').count()
            aprovadas = Visita.query.filter_by(usuario_id=usuario_id, status='aprovada').count()
            recusadas = Visita.query.filter_by(usuario_id=usuario_id, status='recusada').count()
        
        return jsonify({
            'total': total,
            'pendentes': pendentes,
            'aprovadas': aprovadas,
            'recusadas': recusadas
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
