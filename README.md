# llm-wiki-skills

LLM Wiki 平台共用的 **Claude Code skills**，獨立成 repo 讓任何專案/agent 取用。

| skill | 做什麼 |
|---|---|
| [`wiki-doc-author`](wiki-doc-author/SKILL.md) | 產出餵進 wiki processor 的源頭文件 —— API（README + openapi.json）、cronjob/worker/CLI、純知識，都一份 README 搞定。一個檔讀完就能做，附純 stdlib 工具（`scripts/`）。 |
| [`sop-to-spec`](sop-to-spec/SKILL.md) | 把維運 SOP（DBA runbook、infra 程序…）轉成「人能審、AI 能照著實作三層 FastAPI 服務」的 spec。 |
| [`skill-author`](skill-author/SKILL.md) | 在本 repo 新增/修改一個**可安裝**的 skill —— 照標準產 SKILL.md、註冊進 marketplace。讓 AI agent 自己會寫 skill。 |

## 安裝（Claude Code plugin）

這個 repo 本身就是一個 **Claude Code plugin marketplace**，所以可以像其他 skill 一樣下載安裝 ——
**公司內網 GitLab 也可以**（不需要 GitHub 或公開 marketplace）。

```text
# 1) 加 marketplace（內網 GitLab 用 git URL；公開 repo 可用 owner/repo 縮寫）
/plugin marketplace add https://gitlab.<你的公司>/<group>/llm-wiki-skills.git

# 2) 安裝 —— 要哪個裝哪個，或一次全裝
/plugin install wiki-doc-author@llm-wiki-skills      # 只要寫 wiki 文件的
/plugin install sop-to-spec@llm-wiki-skills          # 只要 SOP→spec 的
/plugin install llm-wiki-skills@llm-wiki-skills       # bundle：一次裝兩個

# 之後更新
/plugin marketplace update llm-wiki-skills
```

- **source 用 git URL 或本地路徑**，不要用「直接指 `marketplace.json` 的 URL」—— 那只下載單一檔，
  skill 的相對路徑（含 `scripts/`）不會解析。
- **本地/離線**：先 clone，再 `/plugin marketplace add /path/to/llm-wiki-skills`。
- **企業 allow-list**（給 IT）：在 managed settings 用 regex 允許內網 GitLab host，全公司即可安裝。
  參考官方「Manage plugins for your organization」。

### 替代：直接複製（離線、不想用 plugin 時）

把需要的 skill 資料夾（含 `scripts/`）複製進專案的 `.claude/skills/<name>/`，Claude Code 會自動載入。

## 寫新 skill

照 [`CONTRIBUTING.md`](CONTRIBUTING.md) 的統一標準（官方 Agent Skills spec + 本 repo 慣例）。
從 [`template/`](template/) 複製起手，填完加進 `.claude-plugin/marketplace.json`。

## 設計原則

- **自包含**：每個 skill 一份 `SKILL.md` 讀完即可執行，不互相指來指去；工具放 `scripts/`（純 stdlib、無相依）。
- **通用**：不綁特定框架/語言/領域；新舊專案皆可。
- **安裝靠 plugin**：`.claude-plugin/marketplace.json` 把每個 skill 列為可安裝 plugin；skill 目錄放
  repo root，由 `skills` 自訂路徑指向。
