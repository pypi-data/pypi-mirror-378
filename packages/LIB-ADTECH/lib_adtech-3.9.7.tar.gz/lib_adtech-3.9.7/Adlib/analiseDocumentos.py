import os
from Adlib.logins import getCredenciais
from Adlib.funcoes import mensagemTelegram
from Adlib.virtaus import finalizarSolicitacao
from Adlib.apiConferirRg import enviarDocumentos
from Adlib.apiValid import obterToken, coletarAnalysisId, verificarFraude


loginValid, senhaValid = getCredenciais(714)


def processarDocumentos(pastaDestino, virtaus, solicitacaoVirtaus, tokenTelegram, chatIdTelegram, cpfParceiro):
    try:
        status_code, resposta_api, documentos_true = enviarDocumentos(pastaDestino)
        print(f"Documentos com resposta True: {documentos_true}")
        print(f"{status_code}")
        print(f"{resposta_api}")

        if not documentos_true:
            return acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, motivo="Não haviam Documentos/Documentos inválidos ❌")

        listaDocumentosTrue = [os.path.join(pastaDestino, f) for f in documentos_true]
        token = obterToken(loginValid, senhaValid)

        if not token:
            return acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, motivo="Token inválido ❌")

        analisysID = coletarAnalysisId(token, cpfParceiro, listaDocumentosTrue)
        print("Analise iniciada, ID:", analisysID)

        if not analisysID:
            return acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, motivo="Falha ao coletar analysisID ❌")

        validarDocumento = verificarFraude(token, analisysID)
        print("Análise de fraude concluída:", validarDocumento, '📝')

        if validarDocumento is True:
            return acaoSucesso(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, status='Aguardando Videochamada',mensagem="Movimentado para: Aguardando Videochamada ✅")
        else:
            return acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, motivo=f"Score {validarDocumento} menor que 80 ❌")

    except Exception as e:
        print("Erro em processarDocumentos:", e)
        return acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacaoVirtaus, motivo=f"Erro ao baixar/processar documentos ❌: {e}")
    

def limparPastaDestino(pastaDestino):
    for arquivo in os.listdir(pastaDestino):  
                        caminho_arquivo = os.path.join(pastaDestino, arquivo) 
                        try:
                            os.remove(caminho_arquivo)  
                            print(f'Arquivo {arquivo} apagado 🗑️')
                        except Exception as e:
                            print(f'Erro ao apagar o arquivo {arquivo}: {e}')


def acaoSucesso(virtaus, tokenTelegram, chatIdTelegram, solicitacao, status, mensagem):
    print("Análise concluída 📝")
    finalizarSolicitacao(virtaus, status=status)
    mensagemTelegram(tokenTelegram, chatIdTelegram, f"Análise de Documentos <b>C6</b> Solicitação:{solicitacao}\n{mensagem}")


def acaoFalha(virtaus, tokenTelegram, chatIdTelegram, solicitacao, motivo):
    finalizarSolicitacao(virtaus, status='Aguardando analise')
    mensagemTelegram(tokenTelegram, chatIdTelegram, f"Análise de Documentos <b>C6</b> Solicitação:{solicitacao}\nMovimentado para: Aguardando Análise 🔍\n{motivo}")
