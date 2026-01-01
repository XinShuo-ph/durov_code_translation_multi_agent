# Translation Template - Per Page Workflow

## Pre-Translation Checklist
- [ ] Sync with all workers (`git fetch --all --prune`)
- [ ] Run `verify_sync.py` to check consensus
- [ ] Identify next available page
- [ ] Claim page in WORKER_STATE.md
- [ ] Commit and push claim immediately

## Page Translation Steps

### 1. Context Gathering (10-15 minutes)
- [ ] Read extracted Russian text from `examples/page_XXX_original.txt`
- [ ] Review chapter summary from `research/chapter_summaries.md`
- [ ] Identify proper nouns, check `research/glossary.md`
- [ ] Note any cultural references requiring research
- [ ] Skim 2-3 pages before and after for narrative context

### 2. Research (15-20 minutes)
For each unfamiliar element:
- [ ] Names: Check `research/durov_bio.md` and `research/vk_history.md`
- [ ] Places: St. Petersburg locations, geographic context
- [ ] Cultural terms: Check `research/russia_context.md`
- [ ] Technical terms: VK features, internet terminology
- [ ] Historical events: Date check, verify facts

Document findings in translator_notes.

### 3. Sentence Segmentation (5 minutes)
- [ ] Break Russian text into logical sentence units
- [ ] Number each sentence for tracking
- [ ] Keep sentences together that should be translated as units

### 4. Translation - Russian to English (20-30 minutes)
- [ ] Translate each sentence preserving meaning
- [ ] Prioritize natural English flow over literal translation
- [ ] Adapt idioms appropriately
- [ ] Maintain Durov's voice (direct, sharp, intellectual)
- [ ] Use American English spelling
- [ ] Check glossary for consistent terminology

### 5. Translation - Russian to Chinese (20-30 minutes)
- [ ] Translate using Simplified Chinese
- [ ] Consider mainland Chinese internet culture
- [ ] Use established translations for names (杜罗夫, 圣彼得堡)
- [ ] Adapt cultural references for Chinese readers
- [ ] Keep technical terms consistent with Chinese tech industry

### 6. Translation - Russian to Japanese (20-30 minutes)
- [ ] Use katakana for foreign names (ドゥーロフ)
- [ ] Balance formal/informal register matching original
- [ ] Consider Japanese tech culture context
- [ ] Use appropriate particles and honorifics
- [ ] Adapt metaphors/idioms for Japanese cultural context

### 7. First Review Pass (10 minutes)
- [ ] Read all 4 versions aloud (or mentally)
- [ ] Check for awkward phrasing
- [ ] Verify no sentences skipped or duplicated
- [ ] Confirm terminology consistency with glossary
- [ ] Grammar check all languages

### 8. Second Review Pass (10 minutes)
- [ ] Read as target audience (Stanford grad student)
- [ ] Does humor/personality come through?
- [ ] Are Russian references accessible?
- [ ] Do translations feel natural in each language?
- [ ] Cross-reference difficult passages

### 9. Third Review Pass (10 minutes)
- [ ] Compare each translation back to Russian original
- [ ] Verify meaning preserved
- [ ] Check formatting will work in PDF
- [ ] Confirm translator notes are helpful
- [ ] Final polish

### 10. Create JSON File (5 minutes)
```json
{
  "page": XXX,
  "chapter": X,
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "中文翻译...",
      "ja": "日本語訳..."
    }
  ],
  "translator_notes": [
    "Note about cultural reference",
    "Explanation of name/term"
  ],
  "research_used": [
    "Source consulted",
    "Context gathered"
  ]
}
```

Save to: `translations/raw/page_XXX.json`

### 11. Generate PDF (2 minutes)
```bash
python3 tools/compile_pages.py \
  translations/raw/page_XXX.json \
  output/page_XXX_translated.pdf
```

### 12. Verify Output (3 minutes)
- [ ] PDF opens correctly
- [ ] All 4 languages visible
- [ ] Colors correct (Black/Blue/Red/Green)
- [ ] No encoding issues
- [ ] Readable layout

### 13. Update State and Commit (5 minutes)
- [ ] Update WORKER_STATE.md M2 section:
  - Change page status from "translating" to "done"
  - Add completion timestamp
  - Add JSON hash (first 8 chars of sha256)
- [ ] Commit with proper message format:
```bash
git add translations/raw/page_XXX.json output/page_XXX_translated.pdf WORKER_STATE.md
git commit -m "[655c] M2 DONE: Completed page XXX
PAGES: XXX
OUTPUT_HASH: $(sha256sum translations/raw/page_XXX.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 14. Sync and Claim Next (2 minutes)
- [ ] Pull latest from all workers
- [ ] Run `verify_sync.py` or `claim_page.sh`
- [ ] Identify next available page
- [ ] Repeat process

## Time Estimates

| Phase | Time | Notes |
|-------|------|-------|
| Context & Research | 25-35 min | Varies by page complexity |
| Translation (3 languages) | 60-90 min | Main work |
| Review (3 passes) | 30 min | Critical for quality |
| JSON & PDF | 10 min | Mostly mechanical |
| **Total per page** | **~2-2.5 hours** | For standard page |

### Complexity Adjustments
- **Simple pages** (front matter, short): 1-1.5 hours
- **Standard pages** (narrative): 2-2.5 hours  
- **Complex pages** (dense references, dialogue): 3-4 hours

## Quality Checkpoints

### Red Flags
- Awkward phrasing in any language
- Inconsistent terminology
- Lost humor/personality
- Unclear cultural references
- Grammar errors
- Missing translator notes for complex terms

### Green Flags
- Reads naturally in all 4 languages
- Consistent with glossary
- Durov's voice preserved
- Cultural references explained or adapted
- Clean, professional presentation

## Efficiency Tips
- Keep glossary open in browser tab
- Use previous pages for context/consistency
- Batch similar research (all names, all places)
- Don't get stuck >10 min on one sentence
- Mark [REVIEW NEEDED] and continue if blocked

## Emergency Protocols
If you realize mid-page you must stop:
1. Save current work to separate file
2. Update WORKER_STATE.md to "blocked" or note issue
3. Release page claim if can't finish
4. Commit status update
5. Another worker can pick up

## Token Budget Per Page
- Context/Research: ~10k tokens
- Translation work: ~20k tokens
- Review: ~5k tokens
- Admin: ~3k tokens
- **Total: ~38k tokens per page**

Aim to complete 2-3 pages per session before running low.
