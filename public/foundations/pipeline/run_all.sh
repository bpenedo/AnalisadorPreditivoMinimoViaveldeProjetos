#!/usr/bin/env bash
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# Esteira completa do projeto.
#   ./run_all.sh              esteira inteira
#   ./run_all.sh --demo       demonstração de 60 s com dados de exemplo (DC9)
#   ./run_all.sh --rapido     pula as etapas caras
#   ./run_all.sh --background executa em screen + watchdog de 20 min (D11/D12)
set -uo pipefail
cd "$(dirname "$0")"

RAIZ="$(cd ../../.. && pwd)"
SESSAO="analisadorpreditivominimoviaveldeprojetos"
MODO="completo"
for a in "$@"; do
  case "$a" in
    --demo) MODO="demo";;
    --rapido) MODO="rapido";;
    --background) MODO="background";;
    -h|--ajuda) sed -n '5,12p' "$0"; exit 0;;
  esac
done

mkdir -p "$RAIZ/logs"

if [[ "$MODO" == "background" ]]; then
  # D11 — SEMPRE screen, NUNCA nohup: screen permite reatar, ver ao vivo e interagir.
  if ! command -v screen >/dev/null; then
    echo "⚠️  'screen' não encontrado. Rodando em primeiro plano."
    echo "    (nunca caímos para nohup: nohup perde o terminal e não reata.)"
    exec "$0"
  fi
  screen -dmS "$SESSAO" bash -c "'$0' 2>&1 | tee '$RAIZ/logs/pipeline.log'"
  echo "🚀 Esteira iniciada em background — sessão screen: $SESSAO"
  echo "   Reatar: screen -r $SESSAO    ·    Encerrar: screen -S $SESSAO -X quit"
  # D12 — watchdog obrigatório, status de 20 em 20 minutos até concluir
  bash watchdog.sh --sessao "$SESSAO" --log "$RAIZ/logs/pipeline.log" \
       --intervalo 20 --rotulo esteira &
  echo "🐕 Watchdog ativo (status a cada 20 min)."
  exit 0
fi

passo() { echo; echo "▶️  $*"; }
falhou() { echo "❌ FALHOU: $*"; exit 1; }

echo "═══════════════════════════════════════════════════════════"
echo "  Analisador Preditivo Mínimo Viável de Projetos — esteira ($MODO)"
echo "  Início: $(date '+%d/%m/%Y %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════"

passo "Verificando o ambiente"
python3 --version || falhou "Python 3 ausente"

passo "Compilando os módulos Python (higiene — Passada 1)"
python3 -m py_compile ./*.py apmv/*.py apmv/mcdm/*.py || falhou "erro de sintaxe"

if [[ "$MODO" == "demo" ]]; then
  passo "DEMONSTRAÇÃO — resultado visível em menos de 60 s (DC9)"
  python3 analisar.py ideia "Automatizar a conciliação bancária manual que meu escritório de contabilidade faz todo dia em planilha" \
      --iter 500 | head -24 || falhou "demonstração"
  echo; echo "✅ Demo concluída em $SECONDS s."
  exit 0
fi

passo "Testes do analisador — invariantes, fundamentação e regressões (Passada 1)"
python3 testes_apmv.py || falhou "testes do analisador"

passo "Prova cruzada Python × Rust (D9)"
if command -v cargo >/dev/null; then python3 prova_cruzada_rust.py || falhou "motores divergem"
else echo "  ⏭️  cargo ausente — prova cruzada pulada (instale Rust para a Passada 1 completa)"; fi

passo "Testes de imunidade herdada (Passada 1 — DC1)"
[[ -f testes_imunidade.py ]] && { python3 testes_imunidade.py || falhou "imunidade"; } || echo "  ⏭️  rode imunidade.py --semear"

if [[ "$MODO" != "rapido" ]]; then
  passo "Medição de desempenho (D14)"
  [[ -f bench.py ]] && { python3 bench.py --registrar || falhou "bench"; } || echo "  ⏭️  a criar"

  passo "Telas (D21)"
  python3 gerar_telas.py || falhou "telas"

  passo "Internacionalização (D4/D20)"
  [[ -f gerar_i18n.py ]] && { python3 gerar_i18n.py --tudo || falhou "i18n"; } || echo "  ⏭️  a criar"
  [[ -f gerar_readmes.py ]] && { python3 gerar_readmes.py || echo "  ⚠️  READMEs incompletos — blocos por traduzir"; }
fi

echo
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Esteira concluída em ${SECONDS}s"
echo "  Próximo passo: bash verificar_publicacao.sh"
echo "═══════════════════════════════════════════════════════════"
