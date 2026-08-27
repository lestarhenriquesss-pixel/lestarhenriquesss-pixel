# Configuração do perfil GitHub — Lestar Henriques

Este pacote já está personalizado para o usuário **`lestarhenriquesss-pixel`**.

O GitHub exibe automaticamente o `README.md` de um repositório público cujo nome seja **exatamente igual ao seu usuário**. Portanto, o repositório final deve ser:

`lestarhenriquesss-pixel/lestarhenriquesss-pixel`

## 1. Criar o repositório de perfil

No GitHub, crie um repositório público chamado:

`lestarhenriquesss-pixel`

Não é necessário criar README pelo site se você for enviar este pacote completo.

## 2. Enviar os arquivos pelo PowerShell

Abra o PowerShell dentro desta pasta e execute:

```powershell
git init
git branch -M main
git add -A
git commit -m "feat: perfil profissional de Lestar Henriques"
git remote add origin https://github.com/lestarhenriquesss-pixel/lestarhenriquesss-pixel.git
git push -u origin main
```

## 3. Permitir que o GitHub Actions atualize os gráficos

No repositório:

**Settings → Actions → General → Workflow permissions → Read and write permissions → Save**

Isso permite que os workflows atualizem os SVGs e criem a branch `output` usada pela animação Snake.

## 4. Criar o token de métricas

O workflow de métricas usa um token próprio para ler informações do perfil.

1. Abra as configurações de tokens do GitHub.
2. Gere um **Personal Access Token clássico**.
3. Marque `read:user`.
4. Se quiser contabilizar repositórios privados nas métricas, adicione também `repo`.
5. No repositório de perfil, abra **Settings → Secrets and variables → Actions**.
6. Crie um secret chamado **`METRICS_TOKEN`** e cole o token.

Não coloque o token dentro do README, de scripts ou de arquivos versionados.

## 5. Executar os workflows pela primeira vez

Abra a guia **Actions** do repositório e execute manualmente:

| Workflow | Resultado |
|---|---|
| **Metrics** | calendário, linguagens, hábitos e conquistas |
| **Snake** | animação do gráfico de contribuições |
| **Charts and cards** | radar de linguagens, estatísticas e cards de projetos |

Depois da primeira execução, as atualizações passam a ocorrer automaticamente pelos agendamentos configurados.

## 6. Alterar competências do radar

Edite:

`assets/skills.json`

Depois execute:

```powershell
python scripts\radar.py --data assets\skills.json -o assets\radar
```

## 7. Atualizar a foto

A foto original está em:

`assets/profile.jpg`

Para gerar novamente o retrato visual usado no README:

```powershell
python scripts\dotify.py assets\profile.jpg -o assets\portrait --cols 100 --equalize --detail 0.5 --color --circle --reveal
```

## 8. Projetos em destaque

Os projetos selecionados estão em:

`assets/projects.json`

Atualmente:

- DASHIFY
- social-hub-v3
- Arbitrage-Bot
- Meu-portf-lio

O workflow **Charts and cards** busca automaticamente linguagem, estrelas e forks desses repositórios.

## 9. Pré-visualização local

Abra `preview.html` no navegador para conferir os principais SVGs antes de publicar.
