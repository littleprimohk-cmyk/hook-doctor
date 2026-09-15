# Hook Doctor 使用教學

目標：從一條已剪好的 Reel，得到更清楚的開場、可繼續編輯的 CapCut 版本、封面及 Caption。

## 1. 安裝整個 skill

下載此 repository 的 ZIP，解壓後找到 `skills/hook-doctor`。

最簡單的方法是把整個資料夾交給支援 skills 的 Agent，請它安裝並驗證。不同工具的技能目錄可能不同；以該工具目前提供的安裝流程為準。

本專案開發環境的 Codex 使用者技能目錄是 `~/.codex/skills`；自訂 `CODEX_HOME` 的環境可能採用其下的 `skills`。這不是對所有 Agent 或所有 Codex 版本的通用路徑保證。可請 Agent 先確認目前版本支援的位置。官方 skill 結構說明：[Build skills](https://learn.chatgpt.com/docs/build-skills)。

手動安裝後應保留這個結構：

```text
你的技能目錄/
└── hook-doctor/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    │   ├── hook-report.md
    │   ├── capcut-edit.md
    │   └── cover-caption-qa.md
    └── scripts/inspect_hook.py
```

開新對話，請 Agent 確認能找到 `$hook-doctor`。若找不到，先核對資料夾層級，避免多了一層 ZIP 解壓目錄。

## 2. 準備最少資料

你只需要提供影片，並在要直接修改時指定 CapCut 專案。**不需要手動截圖、拆片或抄字幕。**

可以額外提供，但不必全部準備：

| 資料 | 用途 |
|---|---|
| 舊影片／品牌參考 | 沿用字型、顏色、字幕節奏 |
| 安全區圖片 | 按你的實際版位檢查圖文 |
| 語言偏好 | 例如廣東話溝通、台式繁體書面字幕 |
| 封面偏好 | 例如保留實景、不去背 |
| 不能改動的部分 | 例如保留產品特寫與原有配樂 |

原始影片、CapCut 草稿和所需素材必須在 Agent 可存取的位置。只有匯出 MP4 時，已燒錄的文字不能假裝成獨立圖層。

## 3. 下達完整任務

```text
使用 $hook-doctor。
影片：我附上的 Reel。
CapCut 專案：我的影片。

請先檢查頭五秒，找出一個最大 Hook 問題，
直接建立第二版並修改，完成匯出、封面和 Caption。

保留我原有 B-roll 和品牌風格。
字幕及 Caption 用台式繁體書面語。
封面保留真人實景，不要去背。
請檢查安全區，也不要遮住人臉、產品或數據。
不要替我發佈。
```

Agent 會先確認素材版本和工具能力，自己拆幀查看，然後決定下一刀。若你只想分析，請明確寫「只分析，暫時不要修改」。如果你希望先批准方案，寫「先給我剪法，等我確認再進 CapCut」。

## 4. 理解 Agent 正在做什麼

### 檢查

預設分析頭五秒，每半秒取樣；遇到轉場、彈字會加密查看。它會看第一幀、人物動作、字幕與標題是否互相配合，以及每一秒有沒有新資訊。

### 選擇一個優先修改點

例如：畫面標題已經寫出答案，口播卻還在吊同一個答案；或最有說服力的產品結果太晚才出現。Agent 會先處理影響最大的問題。

### 在 CapCut 執行

建立獨立副本，調整真正的素材、字幕、圖片與時間軸。需要一起移動的軌道可以放入原生複合片段，但仍須保持可編輯性和同步。它不應用大色底蓋住原片來模擬修改。

### 封面與 Caption

封面標題配合新開場；Caption 補充觀看理由和一個適當行動呼籲。數字必須來自你的內容或可核對計算，不能保證觀看成效。

### 匯出及檢查

檢查匯出檔的開場、剪接點、字幕動畫、數據、遮擋與結尾。工具不能檢查音訊時，應說明限制，而不是聲稱聽過。

## 5. 收到成品後

打開 CapCut 副本及匯出影片，確認新的第一句和品牌語氣符合你的意思。下載封面、複製 Caption，再自行上傳。若需要修改，直接指出具體問題：

```text
用 $hook-doctor 繼續修改剛才的第二版。
保留新的剪接，但把擋住產品的字幕移到左上方。
請直接在 CapCut 改原有圖層，重新匯出並檢查。
```

## 進階：單獨使用拆幀腳本

這是給維護者或有需要的人使用；一般 Creator 不需要手動執行。

需要 Python 3 與 FFmpeg。從 repository 根目錄執行：

```bash
python3 skills/hook-doctor/scripts/inspect_hook.py "video.mp4" "hook-inspection" --audio
```

輸出：11 張預設取樣圖片、時間 manifest、影片 metadata，及可取得時的頭五秒音訊。輸出資料夾必須是新的或空白，避免覆寫已有工作。

```bash
python3 skills/hook-doctor/scripts/inspect_hook.py "video.mp4" "closer-inspection" --step 0.2
```

腳本只提取素材，不會自行評分或操作 CapCut。Agent 必須真正查看圖片及完成後續判斷。
