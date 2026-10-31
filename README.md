# Odin3 Qt

Interface gráfica Qt (PyQt5) para Linux que reproduz o layout do Odin3 v3.14, usada para gravar firmware em aparelhos Samsung em Download Mode. A gravação em si é feita pelo binário de linha de comando `odin4`; este projeto é a interface, a detecção de aparelhos, a verificação de MD5 e o empacotamento em `.deb`.

![Odin3 Qt](docs/screenshot.png)

> Projeto independente, sem vínculo com a Samsung. "Odin" e "Samsung" são marcas de seus respectivos proprietários. Este repositório não contém código nem binários da Samsung (inclusive o `odin4`).

## Sumário

1. [Recursos](#recursos)
2. [Requisitos](#requisitos)
3. [Instalação](#instalação)
4. [Instalando o odin4](#instalando-o-odin4)
5. [Uso](#uso)
6. [Opções e limitações](#opções-e-limitações)
7. [Solução de problemas](#solução-de-problemas)
8. [Guia: antes de modificar o aparelho](#guia-antes-de-modificar-o-aparelho)
9. [Guia: gravar firmware oficial (stock)](#guia-gravar-firmware-oficial-stock)
10. [Guia: desbloquear o bootloader](#guia-desbloquear-o-bootloader)
11. [Guia: flashear o TWRP](#guia-flashear-o-twrp)
12. [Guia: instalar uma ROM customizada](#guia-instalar-uma-rom-customizada)
13. [Guia: Magisk, GApps e extras](#guia-magisk-gapps-e-extras)
14. [Guia: voltar ao stock e recuperar o aparelho](#guia-voltar-ao-stock-e-recuperar-o-aparelho)
15. [Desenvolvimento](#desenvolvimento)
16. [Licença](#licença)

## Recursos

- Layout fiel ao Odin3 v3.14: banner, 8 slots de status e ID:COM, abas Log, Options e Pit, campos BL, AP, CP, CSC e USERDATA, botões Start, Reset, Exit e Mass D/L.
- Detecção automática de aparelhos Samsung em Download Mode (USB 04e8:685d e 04e8:6601), com atualização do slot ID:COM e mensagens `Added!!` e `Removed!!` no log.
- Verificação do MD5 embutido nos arquivos `.tar.md5` antes de gravar. Arquivo corrompido bloqueia a gravação.
- Gravação em paralelo em todos os aparelhos conectados (até 8 slots), com barra de progresso e status PASS! ou FAIL! por slot.
- Pacote `.deb` com atalho no menu, ícones e regras udev para acesso USB sem root.

## Requisitos

- Linux com suporte a pacotes `.deb` (Debian, Ubuntu, Linux Mint e derivados). Também é possível rodar direto do código-fonte em outras distribuições.
- Python 3.8 ou superior e PyQt5 (`python3-pyqt5`).
- O binário `odin4` instalado separadamente (veja abaixo).
- Cabo USB de boa qualidade, de preferência o original, ligado direto a uma porta USB do computador (evite hubs).

## Instalação

### Pelo pacote .deb

Gere o pacote a partir do código-fonte (veja [Desenvolvimento](#desenvolvimento)) ou use um `.deb` já pronto e instale:

```bash
sudo apt install ./odin3-qt_3.14-1_all.deb
```

O `apt` instala as dependências (`python3` e `python3-pyqt5`) automaticamente. Depois, abra pelo menu de aplicativos (Odin3) ou pelo terminal:

```bash
odin3-qt
```

Para remover:

```bash
sudo apt remove odin3-qt
```

### Pelo código-fonte, sem instalar

```bash
git clone https://github.com/chespinowo/odin3-qt.git
cd odin3-qt
sudo apt install python3-pyqt5
./run-dev.sh
```

Nesse modo as regras udev não são instaladas. Se o aparelho for detectado mas o odin4 reclamar de permissão, copie `packaging/60-odin3-qt.rules` para `/etc/udev/rules.d/` e execute `sudo udevadm control --reload-rules`.

### O que o pacote instala

| Caminho | Conteúdo |
| --- | --- |
| `/usr/bin/odin3-qt` | Launcher do programa |
| `/usr/lib/odin3-qt/odin3_qt/` | Código Python da interface |
| `/usr/share/odin3-qt/images/` | Imagens usadas pelo estilo (checkbox e setas) |
| `/usr/share/applications/odin3-qt.desktop` | Atalho no menu |
| `/usr/share/icons/hicolor/` | Ícones do aplicativo |
| `/usr/lib/udev/rules.d/60-odin3-qt.rules` | Permissão USB para aparelhos Samsung |
| `/usr/share/doc/odin3-qt/` | Copyright, changelog e README.Debian |

## Instalando o odin4

O `odin4` é a versão de linha de comando do Odin para Linux. Ele não faz parte deste repositório nem do pacote. Obtenha-o de uma fonte em que você confie, confira o hash se houver e instale:

```bash
sudo install -m 755 odin4 /usr/local/bin/odin4
odin4 -v
```

Também é possível manter o binário em qualquer pasta e apontar para ele:

```bash
ODIN4=/caminho/para/odin4 odin3-qt
```

A interface procura o `odin4` nesta ordem: variável `ODIN4`, `PATH`, `/usr/local/bin`, `/opt/odin4`, `/usr/bin` e `~/.local/bin`.

Os argumentos que a interface repassa ao `odin4` são `-b`, `-a`, `-c`, `-s`, `-u` (arquivos BL, AP, CP, CSC e USERDATA), `-e` (apagar), `--reboot` e `-d <dispositivo USB>`. Como a ferramenta pode variar entre versões, confira com `odin4 --help` se algo não se comportar como esperado.

## Uso

1. Desligue o aparelho e entre em Download Mode. Em muitos modelos modernos, sem botão Home: com o aparelho desligado, segure Volume Cima e Volume Baixo juntos e conecte o cabo USB ligado ao computador. Na tela de aviso, pressione Volume Cima para continuar. O método varia por modelo; confirme o seu.
2. Abra o Odin3 Qt. Quando o aparelho for detectado, o primeiro slot ID:COM fica azul (por exemplo `0:[1-4]`) e o log mostra `Added!!`.
3. Clique nos botões BL, AP, CP, CSC e USERDATA conforme os arquivos que você vai gravar. O checkbox ao lado de cada campo é marcado automaticamente; desmarque para ignorar aquele arquivo.
4. Na aba Options, confira as opções (veja abaixo).
5. Clique em Start. A interface verifica o MD5 dos `.tar.md5`, depois chama o `odin4`. O slot mostra o progresso e termina com PASS! (verde) ou FAIL! (vermelho). O log fecha com `All threads completed`.
6. Reset limpa campos, log e status. Exit fecha o programa (se houver gravação em andamento, pede confirmação).

Nunca desconecte o cabo nem desligue o computador durante a gravação.

## Opções e limitações

| Opção | Comportamento |
| --- | --- |
| Auto Reboot | Marcada: passa `--reboot` ao odin4 e o aparelho reinicia ao final. Desmarcada: o aparelho permanece no Download Mode (necessário ao flashear o TWRP). |
| Nand Erase All | Passa `-e` ao odin4 (apaga a NAND). Pode remover partições críticas. Use somente se souber exatamente o que está fazendo. |
| Re-Partition e aba Pit | Reproduzidos pela fidelidade visual, mas o `odin4` não suporta PIT. Com Re-Partition marcado, o Start é bloqueado com um aviso. |
| F. Reset Time | Apenas visual nesta versão. |
| Mass D/L ? | Mostra uma explicação. O Start já grava em paralelo em todos os aparelhos detectados. |

Opções do Odin original como Phone EFS Clear e Phone Bootloader Update foram deliberadamente omitidas: o backend não as suporta e a primeira pode apagar o IMEI.

Estado do projeto: o fluxo completo (detecção, verificação MD5, gravação, progresso e log) foi validado com um dispositivo e um `odin4` simulados. Faça o primeiro teste com um aparelho que você possa recuperar.

## Solução de problemas

**O aparelho não aparece no slot ID:COM**

- Confirme que ele está em Download Mode e rode `lsusb | grep 04e8`. Deve aparecer algo como `04e8:685d`.
- Troque o cabo e a porta USB (prefira uma porta USB 2.0 direta na placa-mãe).
- Recarregue as regras udev e reconecte o cabo:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb
```

- Se o ModemManager estiver interferindo, pare-o durante a gravação: `sudo systemctl stop ModemManager`.

**Mensagem "odin4 binary not found"**: instale o `odin4` em `/usr/local/bin` ou defina `ODIN4` (veja acima).

**"is invalid" no log**: o MD5 do arquivo não confere. Baixe o firmware novamente; não grave arquivos corrompidos.

**FAIL! logo no início**: o log mostra a saída do `odin4`. Causas comuns são permissão USB, arquivo errado para o modelo, ou firmware com bootloader mais antigo que o instalado (proteção contra downgrade).

**`ModuleNotFoundError: No module named 'PyQt5'`**: instale `python3-pyqt5`.

**O texto parece diferente do Windows**: a interface usa Segoe UI se existir, senão Noto Sans, DejaVu Sans ou Liberation Sans. O layout é fixo (872x619), mas a largura do texto varia com a fonte.

## Guia: antes de modificar o aparelho

Este guia é genérico para aparelhos Samsung. Detalhes (teclas, nomes de arquivos, ROMs e TWRP disponíveis) mudam de modelo para modelo, então use sempre os arquivos e instruções do seu modelo exato (nome comercial, código do modelo e região).

Riscos que você aceita ao modificar o aparelho:

- Desbloquear o bootloader apaga todos os dados e **ativa o contador Knox (0x1), que é permanente**. Samsung Pay, Secure Folder, Samsung Pass e algumas funções de Samsung Health podem deixar de funcionar, e a garantia pode ser afetada.
- Firmware, TWRP ou ROM errados podem causar bootloop ou deixar o aparelho inutilizável (brick).
- Alguns aplicativos bancários e de pagamento passam a recusar aparelhos modificados.

Faça antes de começar:

1. Carregue a bateria acima de 70 por cento.
2. Faça backup de tudo (fotos, documentos, contatos, mensagens, autenticadores). Desbloquear o bootloader formata o aparelho.
3. Saia das contas Google e Samsung se for trocar de sistema, para evitar bloqueio por FRP (Factory Reset Protection) depois.
4. Anote o modelo exato em Configurações > Sobre o telefone (por exemplo `SM-XXXXX`), a região (CSC) e a versão de bootloader atual.
5. Baixe o firmware oficial do seu modelo e guarde. Ele é sua rota de volta se algo der errado.

## Guia: gravar firmware oficial (stock)

Serve para atualizar, reinstalar ou recuperar o sistema original.

1. Baixe o firmware do modelo e da região corretos em uma fonte confiável. O zip traz quatro ou cinco arquivos: `BL_...tar.md5`, `AP_...tar.md5`, `CP_...tar.md5`, `CSC_...tar.md5` e `HOME_CSC_...tar.md5`.
2. Extraia o zip.
3. Entre em Download Mode e conecte o aparelho.
4. No Odin3 Qt, selecione cada arquivo no slot correspondente: BL, AP, CP e CSC.
   - Use `CSC_` para uma instalação limpa (apaga os dados).
   - Use `HOME_CSC_` para atualizar mantendo os dados (nem sempre funciona e não é indicado quando se vem de ROM customizada).
5. Mantenha Auto Reboot marcado e clique em Start.
6. Aguarde o PASS! e o reinício. O primeiro boot é demorado.

Cuidado com a versão de bootloader: não grave firmware com bootloader mais antigo que o instalado, pois a proteção contra downgrade pode causar falha ou brick. A versão aparece no nome do firmware; por exemplo, em `XXXXXXXXU3AVB1` o `U3` indica bootloader 3. O número do bootloader não pode diminuir.

## Guia: desbloquear o bootloader

Necessário para instalar TWRP e ROMs customizadas. Isso apaga todos os dados.

1. Em Configurações > Sobre o telefone > Informações do software, toque 7 vezes em Número da versão para ativar as Opções do desenvolvedor.
2. Em Opções do desenvolvedor, ative Desbloqueio de OEM. Se a opção não aparecer ou estiver cinza, conecte o aparelho à internet, entre com a conta Samsung e aguarde. Em alguns modelos há um período de espera (até cerca de 7 dias) e não adianta alterar a data do sistema.
3. Desligue o aparelho e entre em Download Mode.
4. Na tela de aviso, siga a instrução para desbloquear (em muitos modelos, segurar Volume Cima por alguns segundos) e confirme. O aparelho será formatado e reiniciará.
5. Refaça a configuração inicial, ative as Opções do desenvolvedor novamente e confirme que Desbloqueio de OEM continua ativado. No Download Mode, o campo de bootloader deve indicar desbloqueado.

## Guia: flashear o TWRP

O TWRP é uma recovery customizada. Ela permite instalar ROMs e zips, fazer backup e restaurar partições. Requisitos: bootloader desbloqueado e o TWRP feito para o seu modelo exato (código do aparelho). Procure o arquivo na página oficial do TWRP ou em uma thread confiável do seu aparelho.

### Preparar o arquivo para o Odin

O Odin só grava arquivos `.tar` no formato ustar. Se você baixou o TWRP como `.img`, converta:

```bash
tar -H ustar -c recovery.img > twrp.tar
```

Muitos aparelhos recentes (Android 10 e posteriores) também exigem um `vbmeta` desativado, que costuma ser fornecido junto da thread do TWRP do aparelho. Nesse caso, empacote os dois no mesmo `.tar`:

```bash
tar -H ustar -c recovery.img vbmeta.img > twrp.tar
```

Os nomes dentro do `.tar` precisam corresponder às partições (`recovery.img` e `vbmeta.img`). Se o TWRP já vier como `.tar` ou `.img.tar`, use-o como está, seguindo as instruções da thread.

### Gravar

1. Entre em Download Mode e abra o Odin3 Qt.
2. Na aba Options, **desmarque Auto Reboot**. Isso é essencial: se o aparelho reiniciar normalmente, o sistema pode restaurar a recovery original e apagar o TWRP.
3. Clique em AP, selecione o `twrp.tar` e clique em Start.
4. Aguarde o PASS!.

### Entrar no TWRP pela primeira vez

1. Com o aparelho ainda no Download Mode, segure Volume Baixo e Power por cerca de 7 a 10 segundos até a tela apagar.
2. Assim que a tela apagar, troque imediatamente para Volume Cima e Power (em aparelhos antigos, Volume Cima, Home e Power) e segure até aparecer o logo do TWRP.
3. Se o sistema iniciar antes de você entrar no TWRP, a recovery original pode ter sido restaurada. Repita o procedimento desde o início.
4. Na primeira tela do TWRP, escolha Permitir modificações (Allow Modifications). Não escolha "Manter somente leitura".

### Remover a criptografia (primeira vez)

Para instalar ROMs customizadas, em geral é preciso formatar a partição de dados para remover a criptografia do sistema original:

1. No TWRP, vá em Wipe > Format Data, digite `yes` e confirme. Isso apaga o armazenamento interno.
2. Volte e escolha Reboot > Recovery para reiniciar no TWRP.
3. Se a thread do seu aparelho indicar, instale também o zip de desativação de verificação e criptografia (por exemplo, o "multidisabler" ou "no-verity-no-encrypt" indicado para o seu modelo e versão do Android). Sem isso, o sistema pode sobrescrever o TWRP ou entrar em bootloop.

Depois de formatar os dados, o TWRP consegue acessar o armazenamento interno e você pode copiar arquivos pelo cabo (MTP) ou por `adb push`.

## Guia: instalar uma ROM customizada

1. **Compatibilidade.** Leia a thread da ROM. Confirme o modelo, e a base de firmware exigida (versão do Android e do bootloader). Muitas ROMs só funcionam sobre uma versão específica do firmware oficial; se for o caso, grave esse firmware antes pelo Odin.
2. **Baixe os arquivos** para o computador: ROM (`.zip`), GApps compatível, se a ROM não incluir (siga a thread; o tipo e a arquitetura devem bater), e Magisk, se quiser root (opcional).
3. **Copie para o aparelho** (armazenamento interno ou cartão SD) pelo TWRP, ou use `adb sideload`.
4. **Backup (recomendado).** No TWRP, Backup: selecione Boot, System, Data e, se existirem, EFS e as partições de modem; salve em cartão SD ou copie para o computador. O backup do EFS é a sua proteção contra perda de IMEI e rede.
5. **Limpeza.** Em Wipe > Advanced Wipe, marque Dalvik / ART Cache, Cache, System e Data. Não marque Internal Storage nem o cartão SD, a menos que queira apagar seus arquivos. Em instalação limpa partindo do stock, também faça o Format Data se ainda não fez.
6. **Instale.** Em Install, escolha o zip da ROM e confirme deslizando. Em seguida, se necessário, instale o GApps e depois o Magisk. Siga a ordem da thread; algumas ROMs pedem reiniciar entre a ROM e o GApps.
7. **Reinicie.** Escolha Wipe Cache/Dalvik e depois Reboot System. O primeiro boot pode levar de 5 a 10 minutos.

### Instalar via ADB sideload

Útil quando o arquivo não cabe no armazenamento ou não dá para copiá-lo:

```bash
sudo apt install adb
```

No TWRP, vá em Advanced > ADB Sideload e deslize para iniciar. No computador:

```bash
adb sideload nome-da-rom.zip
```

### ROMs distribuídas em .tar.md5

Algumas ROMs vêm no formato de firmware (`.tar.md5`) e são gravadas pelo Odin, nos slots indicados pelo autor (AP e, às vezes, CP e CSC), em vez do TWRP. Siga a thread, e use o Odin3 Qt como no guia de firmware oficial.

### Atualizando a ROM depois

- **Dirty flash**: instalar a nova versão por cima, sem limpar dados. Só funciona quando a thread permitir.
- **Clean flash**: refazer a limpeza (passo 5) e instalar de novo. É a opção mais segura para trocar de versão do Android.

## Guia: Magisk, GApps e extras

- **GApps**: ROMs "vanilla" não trazem Google Play. Use o pacote indicado na thread da ROM (versão do Android e arquitetura corretas) e instale logo após a ROM, antes do primeiro boot.
- **Magisk**: baixe a versão oficial do projeto e siga a documentação para o seu aparelho. Em muitos aparelhos Samsung o método é gerar um `boot.img` ou `recovery.img` modificado com o app do Magisk e gravá-lo pelo Odin no slot AP. Em outros, instala-se o zip pelo TWRP. Siga a documentação do seu modelo.
- **Verificação de integridade (Play Integrity)**: aparelhos com bootloader desbloqueado podem falhar nesse teste, o que afeta apps bancários e alguns jogos. Soluções variam e mudam com o tempo; consulte as threads da comunidade do seu modelo.
- **Kernels customizados**: normalmente distribuídos como `.zip` para o TWRP ou `.tar` para o Odin (slot AP). Use apenas o que for feito para o seu modelo e versão do Android.

## Guia: voltar ao stock e recuperar o aparelho

Se o aparelho entrar em bootloop, não ligar ou você quiser remover as modificações:

1. Entre em Download Mode (se o TWRP ainda abrir, desligue por ele e entre pelos botões).
2. Grave o firmware oficial completo (BL, AP, CP e CSC) com o Odin3 Qt, conforme o guia de firmware oficial.
3. Se o aparelho continuar em bootloop depois do stock, entre na recovery original (Volume Cima + Power) e faça Wipe data / factory reset.
4. Se o Knox já foi acionado (0x1), ele continua assim mesmo depois de voltar ao stock.
5. Se o aparelho não aparece em Download Mode, tente outra porta, outro cabo, e a combinação de teclas do seu modelo. Em último caso, procure a assistência técnica.

IMEI zerado ou sem sinal depois de modificar o aparelho normalmente indica EFS ou modem corrompidos. Restaure o backup do EFS feito no TWRP, ou grave novamente o firmware completo com o CSC correto.

## Desenvolvimento

Estrutura do repositório:

```
odin3_qt/          Código Python (app, backend, banner, widgets)
packaging/         Arquivos do pacote .deb (DEBIAN, launcher, desktop, udev, docs)
tools/gen_assets.py  Gera os ícones e as imagens de estilo
build-deb.sh       Monta e gera o .deb em build/
run-dev.sh         Roda o programa direto do código-fonte
docs/              Imagens usadas neste README
```

Gerar o pacote:

```bash
sudo apt install python3-pyqt5 dpkg-dev
./build-deb.sh
# resultado: build/odin3-qt_3.14-1_all.deb
```

Para gerar um AppImage x86_64, instale `python3-pyqt5`, `python3-venv`, `curl` e `squashfs-tools` e rode:

```bash
./build-appimage.sh
# resultado: build/odin3-qt_3.14-1_x86_64.AppImage
```

O script prepara o PyInstaller e baixa o `appimagetool` oficial quando necessário. O AppImage inclui a interface e o PyQt5; o `odin4` e o `adb` continuam sendo ferramentas externas e devem estar instalados no sistema.

Renderizar a interface para um PNG (útil para comparar com a referência, sem abrir janela):

```bash
QT_QPA_PLATFORM=offscreen ODIN3_QT_IMAGES="$PWD/build/dev/usr/share/odin3-qt/images" \
    python3 -m odin3_qt --render /tmp/odin.png
```

Arquivos principais:

| Arquivo | Função |
| --- | --- |
| `odin3_qt/app.py` | Janela principal, posições medidas na captura do Odin3, estilo (QSS) e fluxo de gravação |
| `odin3_qt/backend.py` | Detecção USB via sysfs, verificação de `.tar.md5` e montagem da linha de comando do `odin4` |
| `odin3_qt/banner.py` | Banner desenhado com QPainter |
| `odin3_qt/widgets.py` | Caixa de status e barra de progresso dos slots |

## Licença

MIT. Veja o arquivo [LICENSE](LICENSE).
