// AnalisadorPreditivoMinimoViaveldeProjetos
// Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
// E-mail: profbruanbima@gmail.com
//
// Segundo motor INDEPENDENTE (D9): reimplementa, sem dependência alguma, a matemática
// financeira e a agregação em log-odds do analisador Python. Um erro de transcrição de
// fórmula raramente se repete idêntico em duas linguagens — se os dois motores
// concordam até 1e-9, a MATEMÁTICA está certa, não só o código.
//
// Entrada (stdin): blocos "caso <nome>" seguidos de linhas "chave = valor".
// Saída (stdout): "caso <nome>" + "chave = valor" com os resultados.
use std::collections::BTreeMap;
use std::io::{self, BufRead, Write};

const RAMPA_MESES: f64 = 6.0;
const MESES_ATE_DESISTIR: f64 = 3.0;
const ACURACIA_EXPERIMENTO: f64 = 0.75;
const ACURACIA_MVP: f64 = 0.85;
const FRACAO_MVP: f64 = 0.35;

fn g(m: &BTreeMap<String, f64>, k: &str) -> f64 {
    *m.get(k).unwrap_or_else(|| panic!("campo ausente: {k}"))
}

/// VP das receitas com rampa linear e desconto mensal pelo CDI.
fn vp_receita(mensal: f64, cdi: f64, horizonte: usize, infra: f64) -> f64 {
    let i = (1.0 + cdi).powf(1.0 / 12.0) - 1.0;
    (1..=horizonte)
        .map(|m| {
            let fluxo = mensal * (m as f64 / RAMPA_MESES).min(1.0) - infra;
            fluxo / (1.0 + i).powi(m as i32)
        })
        .sum()
}

fn payback(receita_liq: f64, custo_mes: f64, infra: f64, custo: f64) -> f64 {
    let mut acum = 0.0;
    for m in 1..=60 {
        acum += receita_liq * (m as f64 / RAMPA_MESES).min(1.0) - custo_mes - infra;
        if acum >= custo {
            return m as f64;
        }
    }
    -1.0 // sem payback em 60 meses
}

fn calcular(e: &BTreeMap<String, f64>) -> Vec<(String, f64)> {
    let p = g(e, "p_viavel");
    let c = g(e, "custo_construir");
    let h = g(e, "horizonte") as usize;
    let cdi = g(e, "cdi");
    let infra = g(e, "infra_mes");
    let margem_c = g(e, "margem_contribuicao");
    let horas_mes = g(e, "horas_mes");
    let valor_hora = g(e, "valor_hora");
    let vp_c = vp_receita(g(e, "receita_cons"), cdi, h, infra) * margem_c;
    let vp_o = vp_receita(g(e, "receita_otim"), cdi, h, infra) * margem_c;
    let vp = 0.7 * vp_c + 0.3 * vp_o;
    let oper = (horas_mes * valor_hora + infra) * h as f64;
    let desistir = oper * MESES_ATE_DESISTIR / h as f64;
    let ganho = vp - oper - c;
    let vpl = p * (vp - oper) - (1.0 - p) * desistir - c;
    let risco = c + desistir;
    let den = vp - oper + desistir;
    let p_be = if den > 0.0 { (risco / den).min(1.0) } else { 1.0 };
    let evpi = p * ganho.max(0.0) - vpl.max(0.0);
    let b = if risco > 0.0 { ganho / risco } else { 0.0 };
    let kelly = if b > 0.0 { p - (1.0 - p) / b } else { -1.0 };
    let cond = |inicial: f64, acc: f64, restante: f64| -> f64 {
        -inicial + p * acc * (vp - oper - restante) - (1.0 - p) * (1.0 - acc) * (restante + desistir)
    };
    let c_exp = g(e, "custo_experimento");
    let a1 = cond(c_exp, ACURACIA_EXPERIMENTO, c).max(-(c_exp + desistir));
    let a2 = cond(FRACAO_MVP * c, ACURACIA_MVP, (1.0 - FRACAO_MVP) * c).max(-(FRACAO_MVP * c + desistir));
    // Log-odds: logit(prior) + Σ contribuições
    let prior = g(e, "prior");
    let soma: f64 = e.iter().filter(|(k, _)| k.starts_with("contrib_")).map(|(_, v)| *v).sum();
    let lg = (prior / (1.0 - prior)).ln() + soma;
    let p_rec = 1.0 / (1.0 + (-lg).exp());
    vec![
        ("vp_receita_cons".into(), vp_c),
        ("vp_receita_otim".into(), vp_o),
        ("vpl_esperado".into(), vpl),
        ("p_breakeven".into(), p_be),
        ("evpi".into(), evpi),
        ("kelly".into(), kelly),
        ("rota_a1".into(), a1),
        ("rota_a2".into(), a2),
        ("payback".into(), payback(g(e, "receita_cons") * margem_c, horas_mes * valor_hora, infra, c)),
        ("p_viavel_recalculada".into(), p_rec),
    ]
}

fn main() {
    let stdin = io::stdin();
    let mut casos: Vec<(String, BTreeMap<String, f64>)> = Vec::new();
    for linha in stdin.lock().lines() {
        let linha = linha.expect("falha de leitura");
        let t = linha.trim();
        if t.is_empty() || t.starts_with('#') {
            continue;
        }
        if let Some(nome) = t.strip_prefix("caso ") {
            casos.push((nome.to_string(), BTreeMap::new()));
        } else if let Some((k, v)) = t.split_once('=') {
            let v: f64 = v.trim().parse().unwrap_or_else(|_| panic!("valor inválido em: {t}"));
            casos.last_mut().expect("chave antes de 'caso'").1.insert(k.trim().to_string(), v);
        }
    }
    let out = io::stdout();
    let mut w = out.lock();
    for (nome, e) in &casos {
        writeln!(w, "caso {nome}").unwrap();
        for (k, v) in calcular(e) {
            writeln!(w, "{k} = {v:.17e}").unwrap();
        }
    }
}
