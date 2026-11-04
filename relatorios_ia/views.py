import logging
import os

from drf_spectacular.utils import extend_schema
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .selectors import (
    consultar_contas_receber_proximos_dias,
    consultar_detalhes_cliente,
    consultar_principais_clientes,
    consultar_produtos_estoque_critico,
    consultar_produtos_mais_vendidos,
    consultar_resumo_vendas,
)

logger = logging.getLogger(__name__)


def extrair_texto(content) -> str:
    """Garante que o retorno seja sempre uma string formatada."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for bloco in content:
            if isinstance(bloco, dict) and "text" in bloco:
                partes.append(bloco["text"])
            elif isinstance(bloco, str):
                partes.append(bloco)
        return "\n".join(partes)
    return str(content)


# ==============================================================================
# FERRAMENTAS DO LANGCHAIN (TOOLS)
# ==============================================================================
@tool
def obter_resumo_vendas(dias: int = 30) -> str:
    """Consulta os dados de faturamento e vendas do ERP.
    Passe o parâmetro 'dias' para o período desejado (ex: 7 para semana, 30 para mês, 365 para ano, 0 para todo histórico).
    """
    dados = consultar_resumo_vendas(dias=dias)
    rotulo = (
        f"{dados['periodo_dias']} dias"
        if isinstance(dados["periodo_dias"], int)
        else dados["periodo_dias"]
    )
    return (
        f"📊 Resumo do Faturamento ({rotulo}):\n"
        f"• Total vendido: R$ {dados['total_faturado']:.2f}\n"
        f"• Pedidos concluídos: {dados['total_pedidos']} pedidos\n"
        f"• Ticket médio: R$ {dados['ticket_medio']:.2f}"
    )


@tool
def obter_principais_clientes(limite: int = 5, dias: int = 30) -> str:
    """Consulta os principais clientes (que mais compraram em R$) no ERP.
    Aceita 'limite' (quantidade de clientes) e 'dias' de histórico (0 para todo o histórico).
    """
    clientes = consultar_principais_clientes(limite=limite, dias=dias)
    if not clientes:
        return "Nenhum cliente registrado com compras no período."

    itens = "\n".join(
        [
            f"• {c['nome']}: R$ {c['total_gasto']:.2f} ({c['total_pedidos']} pedidos)"
            for c in clientes
        ]
    )
    return f"👥 Principais Clientes ({'Últimos ' + str(dias) + ' dias' if dias else 'Todo Histórico'}):\n{itens}"


@tool
def obter_produtos_mais_vendidos(limite: int = 5, dias: int = 30) -> str:
    """Consulta os produtos mais vendidos em quantidade no ERP no período especificado."""
    produtos = consultar_produtos_mais_vendidos(limite=limite, dias=dias)
    if not produtos:
        return "Nenhum produto vendido no período solicitado."

    itens = "\n".join(
        [
            f"• {p['nome']}: {p['quantidade_vendida']} un vendidas (Gerou R$ {p['faturamento_gerado']:.2f})"
            for p in produtos
        ]
    )
    return f"📦 Produtos Mais Vendidos:\n{itens}"


@tool
def obter_estoque_critico(limite_minimo: int = 5) -> str:
    """Consulta produtos com estoque zerado ou abaixo do limite especificado no ERP."""
    produtos = consultar_produtos_estoque_critico(limite_minimo=limite_minimo)
    if not produtos:
        return "Nenhum produto com estoque crítico no momento."

    itens = "\n".join(
        [
            f"{i+1}. {p['nome']} (Saldo: {p['saldo']} un{' - ZERADO' if p['saldo'] <= 0 else ''})"
            for i, p in enumerate(produtos)
        ]
    )
    return f"⚠️ Alerta de Estoque Crítico:\n{itens}"


@tool
def obter_contas_receber(dias: int = 7) -> str:
    """Consulta a previsão de contas a receber nos próximos N dias e parcelas em atraso."""
    dados = consultar_contas_receber_proximos_dias(dias=dias)
    return (
        f"💰 Contas a Receber (Próximos {dados['dias_previsao']} dias):\n"
        f"• A receber no período: R$ {dados['total_a_receber']:.2f} ({dados['qtd_parcelas_periodo']} parcelas)\n"
        f"• Vencido em atraso: R$ {dados['total_vencido']:.2f} ({dados['qtd_parcelas_vencidas']} parcelas)"
    )


@tool
def obter_detalhes_cliente(termo_busca: str) -> str:
    """Busca informações detalhadas e compras de um cliente pelo nome, CPF ou CNPJ."""
    clientes = consultar_detalhes_cliente(termo_busca=termo_busca)
    if not clientes:
        return f"Nenhum cliente encontrado com a busca '{termo_busca}'."

    linhas = []
    for c in clientes:
        linhas.append(
            f"👤 Cliente: {c['nome']}\n"
            f"• Documento: {c['documento']} | Telefone: {c['telefone']}\n"
            f"• E-mail: {c['email']}\n"
            f"• Total gasto acumulado: R$ {c['total_gasto']:.2f} em {c['total_compras']} pedidos"
        )
    return "\n\n".join(linhas)


TOOLS = [
    obter_resumo_vendas,
    obter_principais_clientes,
    obter_produtos_mais_vendidos,
    obter_estoque_critico,
    obter_contas_receber,
    obter_detalhes_cliente,
]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


# ==============================================================================
# SERIALIZERS & VIEW
# ==============================================================================
class RelatorioIARequestSerializer(serializers.Serializer):
    mensagem = serializers.CharField(
        help_text="Texto da pergunta ou comando enviado para a IA.",
        default="Quais são meus principais clientes?",
    )


class RelatorioIAResponseSerializer(serializers.Serializer):
    resposta = serializers.CharField(
        help_text="Resposta formatada em HTML sintetizada pela IA."
    )


@extend_schema(
    summary="Consultar Relatório com IA",
    description="Interface inteligente que executa e combina múltiplas ferramentas do ERP via Maritaca AI (Sabiá-3).",
    request=RelatorioIARequestSerializer,
    responses={200: RelatorioIAResponseSerializer},
)
@api_view(["POST"])
def relatorio_ia_view(request):
    serializer = RelatorioIARequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    mensagem = serializer.validated_data.get("mensagem", "").strip()

    try:
        api_key = os.getenv("MARITACA_API_KEY")
        if not api_key:
            return Response(
                {"detail": "Chave MARITACA_API_KEY não configurada no ambiente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Configuração do ChatOpenAI apontando para o endpoint da Maritaca AI
        llm = ChatOpenAI(
            model="sabiazinho-4",
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
            temperature=0.2,
            request_timeout=30.0,
            max_retries=5,
            model_kwargs={"extra_body": {"service_tier": "flex"}},
        )

        llm_with_tools = llm.bind_tools(TOOLS)

        messages = [
            HumanMessage(
                content=(
                    "Você é o assistente virtual do ERP Simples Gestão. "
                    "Responda à pergunta utilizando as ferramentas disponíveis. "
                    "Se necessário para uma resposta completa, invoque múltiplas ferramentas em sequência. "
                    "Formate a resposta final obrigatoriamente utilizando tags HTML simples (<strong>, <br/>, •).\n\n"
                    f"Pergunta do usuário: {mensagem}"
                )
            )
        ]

        # Loop do agente (até 5 iterações para combinação de ferramentas)
        for _ in range(5):
            response_msg = llm_with_tools.invoke(messages)
            messages.append(response_msg)

            if not response_msg.tool_calls:
                break

            for tool_call in response_msg.tool_calls:
                selected_tool = TOOLS_BY_NAME.get(tool_call["name"])
                if selected_tool:
                    tool_output = selected_tool.invoke(tool_call["args"])
                else:
                    tool_output = f"Ferramenta {tool_call['name']} não encontrada."

                messages.append(
                    ToolMessage(
                        content=extrair_texto(tool_output),
                        tool_call_id=tool_call["id"],
                    )
                )

        texto_resposta = extrair_texto(messages[-1].content)

    except Exception as e:
        logger.exception("Erro ao processar requisição na view relatorio_ia_view")
        return Response(
            {"detail": f"Erro interno ao consultar assistente de IA: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"resposta": texto_resposta}, status=status.HTTP_200_OK)
