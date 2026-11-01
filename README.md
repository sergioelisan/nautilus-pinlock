# PinLock para Nautilus

Proteja pastas com um **PIN numérico** direto pelo menu de contexto do Nautilus (GNOME Files).
O conteúdo é **criptografado de verdade** com [gocryptfs](https://github.com/rfjakob/gocryptfs) — não é só esconder ou mudar permissões.

## Como funciona

A pasta mantém sempre o mesmo nome:

| Estado | O que você vê |
|---|---|
| **Bloqueada** | `Fotos` com ícone de cadeado, aparentemente vazia e somente leitura (por dentro é o cofre cifrado) |
| **Desbloqueada** | `Fotos` com seus arquivos; o cofre fica oculto como `.Fotos.pinlock` |

Clique com o botão direito na pasta (ou no fundo dela):

- **Proteger com PIN…** — cifra a pasta (PIN digitado duas vezes)
- **Desbloquear com PIN…** — pede o PIN e abre a pasta
- **Bloquear pasta** — fecha e volta a cifrar a visão
- **Remover proteção por PIN…** — decifra de volta para uma pasta comum

A pasta se **bloqueia sozinha após 15 minutos sem uso**. Se a sessão terminar com ela aberta,
o reparo automático no login a devolve ao estado bloqueado.

## Instalação

```bash
git clone https://github.com/sergioelisan/nautilus-pinlock.git
cd nautilus-pinlock
./install.sh
```

O instalador usa `apt` para instalar as dependências que faltarem
(`gocryptfs`, `zenity`, `python3-nautilus`) e reinicia o Nautilus.
Testado no Ubuntu 26.04 com Nautilus 50.

Para remover: `./uninstall.sh` (pastas protegidas continuam cifradas e intactas).

## Segurança

- **Esqueceu o PIN, perdeu os arquivos.** Não há recuperação.
- Use **6 ou mais dígitos**. Cada tentativa é propositalmente lenta (scrypt, `logN=18`, ~1 s),
  mas um PIN de 4 dígitos tem só 10 mil combinações e pode ser quebrado em horas por quem copiar o cofre.
- Ao proteger, a pasta original é apagada após a cópia ser verificada, mas sem apagamento seguro
  (em SSDs, restos podem persistir até o espaço ser reutilizado).
- Enquanto desbloqueada, a pasta está acessível a qualquer programa do seu usuário.

## Configuração

Variáveis de ambiente lidas pelo `pinlock-helper`:

| Variável | Padrão | Descrição |
|---|---|---|
| `PINLOCK_IDLE` | `15m` | Tempo de inatividade até o bloqueio automático |
| `PINLOCK_SCRYPTN` | `18` | Custo do scrypt para pastas novas (maior = tentativas mais lentas) |

## Linha de comando

```bash
~/.local/share/pinlock/pinlock-helper protect|unlock|lock|remove <pasta>
~/.local/share/pinlock/pinlock-helper repair
```

Uma pasta bloqueada também pode ser aberta manualmente, sem a extensão:
`gocryptfs Fotos /algum/ponto/de/montagem`.
